# import requests
from urllib.error import HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, date


Y = 2000  # dummy leap year to allow input X-02-29 (leap day)
SEMESTERS = [('fall schedule', (date(Y, 8, 24), date(Y, 12, 18))),
           ('spring schedule', (date(Y, 1, 15), date(Y, 5, 18)))]

MAINPAGE = "https://scheduling.uconn.edu/class-schedule-snapshots/"


# https://stackoverflow.com/a/28688724
def get_semester(today):
    now = today.replace(year=Y)
    return next(season for season, (start, end) in SEMESTERS if start < now < end)


def getHTMLContent(link):
    html = urlopen(link)
    soup = BeautifulSoup(html, features="html.parser")
    return soup


def getSchedule(today):
    schedule_type = get_semester(today)
    try:
        content = getHTMLContent(MAINPAGE)
    except HTTPError:
        return None

    try:
        textwidget = content.find('div', {'class': 'textwidget'})
        for semester in textwidget.find_all('li'):
            if semester.text.lower() == schedule_type:
                return semester.a.get('href')
    except AttributeError:
        return None

    return None




