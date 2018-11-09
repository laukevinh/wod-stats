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

def build_url(YYYY, MM, DD, option=API):
    return BASE_URL[option].format(year=YYYY, month=MM, day=DD)

# Create your views here.
def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))

def summarize(page):
    try:
        data = json.loads(page)
    except TypeError as e:
        raise e
    else:
        context = {
            'num_comments': len(data),
            'num_male': 0,
            'num_female': 0,
            'num_rx': 0,
            'num_scale': 0,
            'details': [],
            }

        for i in range(context['num_comments']):
            comment = data[i]['commentText'].lower()
            commenter = data[i]['commenter']
            rx = RE_RX.search(comment)
            scale = RE_SCALE.search(comment)
            gender = RE_GENDER.search(comment)

            detail = {
                'comment_text': comment, 
                'scale': None, 
                'gender': None,
                'created': data[i]['created'],
                'commenter': {
                    'first_name': commenter.get('firstName'),
                    'last_name': commenter.get('lastName'),
                    'picture_url': commenter.get('pictureUrl'),
                    'created': commenter.get('created'),
                }
            }

            if rx is not None:
                context['num_rx'] += 1
                detail['scale'] = rx.group(1)
            elif scale is not None:
                context['num_scale'] += 1
                detail['scale'] = scale.group(1)

            if gender is not None:
                if 'm' in gender.group(1):
                    context['num_male'] += 1
                else:
                    context['num_female'] += 1
                detail['gender'] = gender.group(1)

            context['details'].append(detail)

        return context
    
def get_valid_date(request):
    today = datetime.date.today()
    YYYY = int(request.GET.get('YYYY', today.year))
    MM   = int(request.GET.get('MM', today.month))
    DD   = int(request.GET.get('DD', today.day))
    date = datetime.date(YYYY,MM,DD)
    if date < EARLIEST_DATE or date > today:
        raise ValueError("Date must be between Feb 1, 2001 and today")
    return (YYYY, MM, DD)

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

def add_comments(context):
    
    workout = Workout(
        title = get_str_date(*context['date']),
        description = get_str_date(*context['date']),
        tags = "",
    )
    workout.save()

    post = Post(
        workout = workout,
        created = datetime.date(*context['date']),
        url = context['url'],
        num_comments = len(context['details']),
        num_male = context['num_male'],
        num_female = context['num_female'],
        num_rx = context['num_rx'],
        num_scale = context['num_scale']
    )
    post.save()

    for i in range(len(context['details'])):

        detail = context['details'][i]
            
        commenter = Commenter(
            first_name = detail['commenter']['first_name'],
            last_name = detail['commenter']['last_name'],
            picture_url = detail['commenter']['picture_url'],
            created = datetime.datetime(
                *get_datetime(detail['commenter']['created'])
            ),
        )
        commenter.save()

        comment = Comment(
            post=post,
            commenter=commenter,
            comment_text=detail['comment_text'],
            created=datetime.datetime(
                *get_datetime(detail['created'])
            ),
            scale=detail['scale'],
            gender=detail['gender'],
            raw_score="",
            score=None,
            height=None,
            weight=None,
            age=None
        )
        comment.save()

def cache(context):
    _cache[context['date']] = [context, 0]

def cache_responds(date):
    return  _cache.get(date)    

def db_responds(date):
    post = Post.objects.filter(created=datetime.date(*date))
    return post.first()

def get_new_data(url):
    with urllib.request.urlopen(url) as resp:
        page = resp.read().decode('utf-8')
        context = summarize(page)
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
                'date': (post.created.year, post.created.month, post.created.day),
                'num_comments': post.num_comments,
                'num_male': post.num_male,
                'num_female': post.num_female,
                'num_rx': post.num_rx,
                'num_scale': post.num_scale,
                'details': post.comment_set.all(),
            }
            print("DB HIT************\n\n")
            cache(context)
            print("Add to cache\n\n")
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))
        else:
            context = get_new_data(build_url(*date, API))
            context['url'] = build_url(*date, REG)
            context['date'] = date
            add_comments(context)
            cache(context)
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))

    return HttpResponse("Failed")
