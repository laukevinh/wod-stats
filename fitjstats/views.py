from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Workout, Post, Commenter, Comment

from .util import RE_RX, RE_SCALE, RE_GENDER, RE_DATE, RE_REG_URL
from .util import RE_WORD, RE_DATETIME
from .util import API, REG, BASE_URL
from .util import EARLIEST_DATE, EARLIEST_DATETIME
from .util import WODHTMLParser

import urllib.request
import json
import datetime

_cache = dict()

def build_url(date, option=API):
    return BASE_URL[option].format(
        year=date.year, 
        month=date.month, 
        day=date.day
    )

def new_commenter(commenter):
    return Commenter(
        first_name = commenter.get('firstName') or "",
        last_name = commenter.get('lastName') or "",
        picture_url = commenter.get('pictureUrl') or "",
        created = get_datetime(commenter.get('created'))
    )

def process_comment(comment):
    comment.post.num_comments += 1

    rx = RE_RX.search(comment.comment_text)
    scale = RE_SCALE.search(comment.comment_text)
    gender = RE_GENDER.search(comment.comment_text)
    
    if scale is not None:
        comment.post.num_scale += 1
        comment.scale = scale.group(1).lower()
    elif rx is not None:
        comment.post.num_rx += 1
        comment.scale = rx.group(1).lower()
    else:
        comment.scale = None

    if gender is not None:
        comment.gender = gender.group(1).lower()
        if 'm' in comment.gender:
            comment.post.num_male += 1
        elif 'f' in comment.gender:
            comment.post.num_female += 1
    else:
        comment.gender = None

def process_cmts(page, date, post):
    try:
        data = json.loads(page)
    except TypeError as e:
        raise e
    else:
        for entry in data:
            commenter = new_commenter(entry['commenter'])
            commenter.save()

            comment = Comment(
                post = post,
                commenter = commenter,
                comment_text = entry['commentText'],
                created = get_datetime(entry['created'])
            )

            process_comment(comment)
            comment.save()

        post.save()

        return {
            'post': post,
            'details': post.comment_set.all(),
            'views': 0,
        }

def process_post(page, date):
    parser = WODHTMLParser()
    parser.feed(str(page))
    post = Post(
        workout = None,
        created = date,
        url = build_url(date, REG),
        text = "".join(parser.data)
    )
    post.save()
    return post

def get_date(string):
    d = RE_DATE.match(string)
    try:
        date = datetime.date(*[int(i) for i in d.groups()])
    except TypeError:
        raise TypeError("Enter a date")
    except AttributeError:
        raise AttributeError("Enter date in a valid format YYYY-MM-DD")
    if date < EARLIEST_DATE or date > datetime.date.today():
        raise ValueError("Date must be between Feb 1, 2001 and today")
    return date

def get_datetime(string):
    d = RE_DATETIME.match(string)
    if d:
        return datetime.datetime(*[int(i) for i in d.groups()])
    else:
        return EARLIEST_DATETIME

def cache(context):
    print("\nCached\n")
    _cache[context['post'].created] = context

def uncache(date):
    if date in _cache:
        print("\nUncached\n")
        _cache.pop(date)

def get_from_cache(date):
    context = _cache.get(date)
    if context is not None:
        print("\nCACHE HIT\n")
        context['views'] += 1
    return context

def get_from_db(date):
    post = Post.objects.filter(created=date).first()
    if post is None:
        return None
    print("\nDB HIT\n")
    context = {
        'post' : post,
        'details': post.comment_set.all(),
        'views': 1,
    }
    cache(context)
    return context

def get_new_data(date):
    with urllib.request.urlopen(build_url(date, REG)) as resp:
        page = resp.read().decode('utf-8')
        post = process_post(page, date)

    with urllib.request.urlopen(build_url(date, API)) as resp:
        page = resp.read().decode('utf-8')
        context = process_cmts(page, date, post)
        print("\nNew entry\n")
        cache(context)

    return context 

def delete_post(date):
    post = Post.objects.filter(created=date).first()
    if post is not None:
        post.delete()
        uncache(date)

# Create your views here.
def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))

def search(request):
    if request.method == 'GET':
        try:
            date = get_date(request.GET.get('date'))
        except AttributeError as empty_date:
            return HttpResponse(empty_date)
        except ValueError as invalid_date:
            return HttpResponse(invalid_date)

        try:
            update = int(request.GET.get('update', 0))
        except ValueError as invalid_int:
            return HttpResponse(invalid_int)

        if update == 1:
            delete_post(date)
        context = get_from_cache(date) \
            or get_from_db(date) \
            or get_new_data(date)

        return HttpResponse(loader.get_template('comments.html')\
            .render(context, request))

    return HttpResponse("Failed")
