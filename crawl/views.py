from django.shortcuts import render
from django.http import HttpResponse

from urllib import request as req

def build_url(YYYY, MM, DD):
    if len(MM) < 2:
        MM = "0{}".format(MM)
    if len(DD) < 2:
        DD = "0{}".format(DD)
    if len(YYYY) < 4:
        YYYY = "20{}".format(YYYY)
    return "https://crossfit.com/" + \
        "comments/api/v1/" + \
        "topics/mainsite." + \
        "{year}{month}{day}".format(year=YYYY, month=MM, day=DD) + \
        "/comments"

# Create your views here.
def index(request):
    return HttpResponse("Crawl")
