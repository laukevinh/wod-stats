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
    

def build_url(YYYY, MM, DD, option=API):
    if len(MM) < 2:
        MM = "0{}".format(MM)
    if len(DD) < 2:
        DD = "0{}".format(DD)
    if len(YYYY) < 4:
        YYYY = "20{}".format(YYYY)
    return BASE_URL[option].format(year=YYYY, month=MM, day=DD)

# Create your views here.
def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))

def summarize(page):
    try:
        data = json.loads(page)
    except TypeError as e:
        print("THere's an error {}".format(e))
    else:
        result = {
            'len': len(data),
            'm': 0,
            'f': 0,
            'rx': 0,
            'details': [],
            }

        for i in range(result['len']):
            comment = data[i]['commentText'].lower()
            rx = RE_RX.search(comment)
            gender = RE_GENDER.search(comment)

            detail = {
                'comment': comment, 
                'rx': 0, 
                'gender': None
                }

            if rx is not None:
                result['rx'] += 1
                detail['rx'] = rx.group(1)
            if gender is not None:
                result[gender.group(1)] += 1
                detail['gender'] = gender.group(1)

            result['details'].append(detail)

        return result
    
def search(request):
    if request.method == 'GET':
        today = datetime.date.today()
        YYYY = request.GET.get('YYYY', str(today.year))
        MM   = request.GET.get('MM', str(today.month))
        DD   = request.GET.get('DD', str(today.day))
        with urllib.request.urlopen(build_url(YYYY, MM, DD)) as resp:
            page = resp.read().decode('utf-8')
            context = summarize(page)
            context['url'] = build_url(YYYY, MM, DD, REG)
            context['YYYY'] = YYYY
            context['MM'] = MM
            context['DD'] = DD
            return HttpResponse(loader.get_template('comments.html')\
                .render(context, request))
    return HttpResponse("Failed")
