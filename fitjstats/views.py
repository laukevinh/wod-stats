from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import urllib.request
import json
import re
import datetime

RE_RX = re.compile(r"(?<![a-cf-z])(rx)(?![a-cf-z])", re.I)
RE_GENDER = re.compile(r"(?:^|[\s/])([mf])[^a-z]", re.I)

API = 0
REG = 1
BASE_URL = ("https://crossfit.com/" 
            + "comments/api/v1/" 
            + "topics/mainsite." 
            + "{year}{month}{day}"
            + "/comments",
            "https://www.crossfit.com/"
            + "workout/"
            + "{year}/{month}/{day}")
    
EARLIEST_DATE = datetime.date(2001, 2, 1)

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
            'len': len(data),
            'm': 0,
            'f': 0,
            'rx': 0,
            'details': [],
            }

        for i in range(context['len']):
            comment = data[i]['commentText'].lower()
            rx = RE_RX.search(comment)
            gender = RE_GENDER.search(comment)

            detail = {
                'comment': comment, 
                'rx': 0, 
                'gender': None
                }

            if rx is not None:
                context['rx'] += 1
                detail['rx'] = rx.group(1)
            if gender is not None:
                context[gender.group(1)] += 1
                detail['gender'] = gender.group(1)

            context['details'].append(detail)

        return context
    
def get_valid_date(request):
    today = datetime.date.today()
    YYYY = request.GET.get('YYYY', str(today.year))
    MM   = request.GET.get('MM', str(today.month))
    DD   = request.GET.get('DD', str(today.day))
    date = datetime.date(int(YYYY),int(MM),int(DD))
    if date < EARLIEST_DATE or date > today:
        raise ValueError("Date must be between Feb 1, 2001 and today")
    return ("{:0>4}".format(YYYY), "{:0>2}".format(MM), "{:0>2}".format(DD))

def search(request):
    if request.method == 'GET':
        try:
            date = get_valid_date(request)
        except ValueError as invalid_date:
            return HttpResponse(invalid_date)

        with urllib.request.urlopen(build_url(*date, API)) as resp:
            page = resp.read().decode('utf-8')
            context = summarize(page)
            context['url'] = build_url(*date, REG)
            context['date'] = date
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))
    return HttpResponse("Failed")
