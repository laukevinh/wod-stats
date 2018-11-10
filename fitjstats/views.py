from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Workout, Post, Commenter, Comment

import urllib.request
import json
import re
import datetime

RE_RX = re.compile(r"(?<![a-cf-z])(rx)(?![a-cf-z])", re.I)
RE_SCALE = re.compile(r"\b(scale)(?:d|\b)", re.I)
RE_GENDER = re.compile(r"(?:^|[\s/])([mf])[^a-z]", re.I)

API = 0
REG = 1
BASE_URL = ("https://crossfit.com/" 
            + "comments/api/v1/" 
            + "topics/mainsite." 
            + "{year:0>4}{month:0>2}{day:0>2}"
            + "/comments",
            "https://www.crossfit.com/"
            + "workout/"
            + "{year:0>4}/{month:0>2}/{day:0>2}")
    
EARLIEST_DATE = datetime.date(2001, 2, 1)

_cache = dict()

def build_url(date, option=API):
    return BASE_URL[option].format(
        year=date.year, 
        month=date.month, 
        day=date.day
    )

# Create your views here.
def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))

def new_workout(context):
    return Workout(
            title = context,
            description = context,
            tags = "",
        )

def new_post(workout, date, num_comments):
    return Post(
        workout = workout,
        created = date,
        url = build_url(date, REG),
        num_comments = num_comments,
        num_male = 0,
        num_female = 0,
        num_rx = 0,
        num_scale = 0,
    )

def new_commenter(raw_commenter):
    return Commenter(
            first_name = raw_commenter.get('first_name') or "",
            last_name = raw_commenter.get('last_name') or "",
            picture_url = raw_commenter.get('picture_url') or "",
            created = datetime.datetime(
                *get_datetime(raw_commenter.get('created'))
            )
        )

def new_comment(post, commenter, comment_text, raw_comment):
    return Comment(
        post = post,
        commenter = commenter,
        comment_text = comment_text,
        created=datetime.datetime(
            *get_datetime(raw_comment.get('created'))
        ),
        scale = None,
        gender = None,
        raw_score="",
        score=None,
        height=None,
        weight=None,
        age=None
    )

def process_comment(post, comment, comment_text):
    rx = RE_RX.search(comment_text)
    scale = RE_SCALE.search(comment_text)
    gender = RE_GENDER.search(comment_text)

    if scale is not None:
        post.num_scale += 1
        scale_type = scale.group(1).lower()
    elif rx is not None:
        post.num_rx += 1
        scale_type = rx.group(1).lower()
    else:
        scale_type = None

    if gender is not None:
        gender_type = gender.group(1).lower()
        if 'm' in gender_type:
            post.num_male += 1
        elif 'f' in gender_type:
            post.num_female += 1
    else:
        gender_type = None

    return {
        'scale_type': scale_type,
        'gender_type' : gender_type,
    }

def summarize(page, date):
    try:
        data = json.loads(page)
    except TypeError as e:
        raise e
    else:
        workout = new_workout(build_url(date, REG))
        workout.save()

        post = new_post(workout, date, len(data))
        post.save()

        for i in range(post.num_comments):

            raw_comment = data[i]

            commenter = new_commenter(raw_comment['commenter'])
            commenter.save()

            comment_text = raw_comment['commentText']

            comment = new_comment(post, commenter, comment_text, raw_comment)
            comment.save()

            detail = process_comment(post, comment, comment_text)
            comment.scale_type = detail.get('scale_type')
            comment.gender_type = detail.get('gender_type')
            comment.save()

        post.save()

        context = {
            'post': post,
            'details': post.comment_set.all(),
            'views': 0,
        }

        return context
    
def get_valid_date(request):
    today = datetime.date.today()
    YYYY = int(request.GET.get('YYYY', today.year))
    MM   = int(request.GET.get('MM', today.month))
    DD   = int(request.GET.get('DD', today.day))
    date = datetime.date(YYYY,MM,DD)
    if date < EARLIEST_DATE or date > today:
        raise ValueError("Date must be between Feb 1, 2001 and today")
    return date

def get_str_date(YYYY, MM, DD):
    return ("{:0>4}".format(YYYY), "{:0>2}".format(MM), "{:0>2}".format(DD))

def get_datetime(string):
    #"2018-11-04T10:18:29+0000"
    if string == None:
        return [2001, 1, 1, 0, 0, 0]
    (d, ttz) = string.split('T')
    (t, tz) = ttz.split('+')
    a = []
    [a.append(i) for i in d.split('-')]
    [a.append(i) for i in t.split(':')]
    return [int(i) for i in a]

def cache(context):
    print("\nCached\n")
    _cache[context['post'].created] = context

def cache_responds(date):
    context = _cache.get(date)
    if context is not None:
        print("\nCACHE HIT\n")
        context['views'] += 1
    return context

def db_responds(date):
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

def get_new_data(url, date):
    with urllib.request.urlopen(url) as resp:
        page = resp.read().decode('utf-8')
        context = summarize(page, date)
        print("\nNew entry\n")
        cache(context)
    return context 

def search(request):
    if request.method == 'GET':
        try:
            date = get_valid_date(request)
        except ValueError as invalid_date:
            return HttpResponse(invalid_date)

        context = cache_responds(date) \
            or db_responds(date) \
            or get_new_data(build_url(date, API), date)

        return HttpResponse(loader.get_template('comments.html')\
            .render(context, request))

    return HttpResponse("Failed")
