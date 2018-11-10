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
                *get_datetime(raw_commenter['created'])
            )
        )

def summarize(page, url, date):
    try:
        data = json.loads(page)
    except TypeError as e:
        raise e
    else:
        workout = new_workout(url)
        workout.save()

        post = new_post(workout, date, len(data))
        post.save()

        for i in range(post.num_comments):

            raw_comment = data[i]

            commenter = new_commenter(raw_comment['commenter'])
            commenter.save()

            comment_text = raw_comment['commentText']

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

            comment = Comment(
                post = post,
                commenter = commenter,
                comment_text = comment_text,
                created=datetime.datetime(
                    *get_datetime(raw_comment['created'])
                ),
                scale = scale_type,
                gender = gender_type,
                raw_score="",
                score=None,
                height=None,
                weight=None,
                age=None
            )
            comment.save()

        post.save()

        context = {
            'post': post,
            'details': post.comment_set.all(),
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
    _cache[context['post'].created] = [context, 0]

def cache_responds(date):
    return  _cache.get(date) 

def db_responds(date):
    post = Post.objects.filter(created=date)
    return post.first()

def get_page(url):
    with urllib.request.urlopen(url) as resp:
        page = resp.read().decode('utf-8')
    return page

def get_new_data(url, date):
    context = summarize(get_page(url), url, date)
    return context 

def search(request):
    if request.method == 'GET':
        try:
            date = get_valid_date(request)
        except ValueError as invalid_date:
            return HttpResponse(invalid_date)

        if cache_responds(date):
            context_wrapper = cache_responds(date)
            context_wrapper[1] += 1
            context = context_wrapper[0]
            print("CACHE HIT************\n\n")
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))
        elif db_responds(date):
            post = db_responds(date)
            context = {
                'post' : post,
                'details': post.comment_set.all(),
            }
            print("DB HIT************\n\n")
            cache(context)
            print("Add to cache\n\n")
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))
        else:
            print("Add to db\n\n")
            context = get_new_data(build_url(date, API), date)
            print("Add to cache\n\n")
            cache(context)
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))

    return HttpResponse("Failed")
