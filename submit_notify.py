#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

import re
from datetime import datetime
from operator import itemgetter
from urllib.parse import quote
from subprocess import call

import requests

login = {"user": "bhidepy84c229559cef6aecdc1e74ba51560e7a8cb7786d489f41cfb823422ec98bc8df", "password": "hidepy9ec29cac1134bdbf1262bed0aecf3ed3a5b982a3be99d6d407f28979118dbeae", "submit": "Login"}
req = requests.post("http://submit.cs.hacettepe.edu.tr/index.php", data=login, verify=False)

pattern = r'<td><a href="assignment_status\.php\?assignment_id=([^"]*)"\s*>([^<]*)</a>\s*<td.*?>(.*?)\s*<td.*?>(.*?)\s*<td.*?>(Yes|No)</tr>'
matches = re.findall(pattern, req.text, re.DOTALL)

time_format = "%Y-%m-%d %H:%M:%S"

assignments = []
for i in matches:
    id_, name, start, end, opened = i

    start = datetime.strptime(start, time_format)
    end = datetime.strptime(end, time_format)

    assert opened in ("Yes", "No")
    opened = opened == "Yes"
    
    d = {"id": id_, "name": name, "start": start, "end": end, "status": opened}
    assignments.append(d)

assignments = list(filter(itemgetter("status"), assignments))
assignments.sort(key=itemgetter("end"))

def read_delta(d):
    s = d.total_seconds()
    days, s = divmod(s, 24 * 60 * 60)
    hours, s = divmod(s, 60 * 60)
    minutes, seconds = divmod(s, 60)
    if days:
        pattern = "{d} days {h} hours remaining."
    else:
        pattern = "{h} hours {m} minutes remaining."

    if days == 1: pattern = pattern.replace("days", "day")
    if hours == 1: pattern = pattern.replace("hours", "hour")
    if minutes == 1: pattern = pattern.replace("minutes", "minute")    
        
    return pattern.format(d=int(days), h=int(hours), m=int(minutes))
    
for assignment in assignments:
    delta = assignment["end"] - datetime.today() 
    print("{id} ({name}): {delta}".format(delta=read_delta(delta), **assignment))


def is_submitted(id_):
    url = "https://submit.cs.hacettepe.edu.tr/assignment_status.php"
    payload = {"assignment_id": id_}
    headers = {"referer": "https://submit.cs.hacettepe.edu.tr/assignment_status.php"}
    cookies = {"user": login["user"], "password": quote(login["password"])}
    
    req = requests.get(url, params=payload, cookies=cookies, headers=headers, verify=False)
    return ">Get</a>" in req.text

for i in assignments:
    i["submitted"] = is_submitted(i["id"])

for assignment in assignments:
    delta = assignment["end"] - datetime.today() 
    ret = "{id} ({name}): {delta}".format(delta=read_delta(delta), **assignment)
    if assignment["submitted"]: ret = "\u0336".join(ret + " ") #strikethrough submitted assignments

    call(["notify-send", ret])

