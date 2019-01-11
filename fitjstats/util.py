from html.parser import HTMLParser

import re
import datetime

RE_RX = re.compile(r"(?<![a-cf-z])(rx)(?![a-cf-z])", re.I)
RE_SCALE = re.compile(r"\b(scale)(?:d|\b)", re.I)
RE_GENDER = re.compile(r"(?:^|[\s/])([mf])[^a-z]", re.I)
RE_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
RE_REG_URL = re.compile(
    r"^https://www.crossfit.com/workout/[0-9]{4}/[0-9]{2}/[0-9]{2}"
)
RE_WORD = re.compile(r"\w+")
RE_DATETIME = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\+(\d{4})"
)

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
EARLIEST_DATETIME = datetime.datetime(2001, 2, 1)

class WODHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.recording = 0
        self.recording_url = 0
        self.data = []
        self.links = []
        self.titles = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.recording:
                self.recording += 1
                return
            for name, value in attrs:
                if name == 'class' and 'content' in value:
                    self.recording = 1
                    return
        if tag == 'a':
            if self.recording < 0:
                return
            if self.recording_url:
                raise Exception("Nested anchor tag")
            for name, value in attrs:
                if name == 'href' and RE_REG_URL.match(value):
                    self.links.append(value)
                    self.recording_url = 1
                    return


    def handle_endtag(self, tag):
        if tag == 'div' and self.recording:
            self.recording -= 1
        if tag == 'a' and self.recording_url:
            self.recording_url -= 1

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)
            return

    def get_data(self):
        return self.data
    
    def get_links(self):
        return self.links

    def get_titles(self):
        return self.titles
