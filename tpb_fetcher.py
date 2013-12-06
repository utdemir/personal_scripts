#! /usr/bin/env python

import re
import json
import time
import datetime
import requests
import operator
import concurrent.futures

API_URL = "http://apify.ifc0nfig.com/tpb/search"
API_KEY = "hidepy5b1e979c675ec3d351b5ac1ac6de1fa3a61b08698b3e113787e4d5f24ae5a6ee"

def get_newest_episode(name_):
    def episode_of(s):
        patterns = ("S(\d{1,2})E(\d{1,2})[^\w]", "[^\w](\d{1,2})x(\d{1,2})[^\w]")
        
        for pattern in patterns:
            match = re.search(pattern, s)
            if match:
                season, episode = map(int, match.groups())
                return season, episode
        
        return None
    
    name = name_.strip().lower()
    params = {"id": name, "top": 20, "key": API_KEY}
    req = requests.get(API_URL, params=params, timeout=10)
   
    if not req.ok: return (name, None)
    
    answer = req.content.decode()
    torrents = [i for i in json.loads(answer) if i["trusted"]]
    for i in torrents: i["episode"] = episode_of(i["name"])
    torrents = [i for i in torrents if i["episode"]]
    
    m = max(torrents, key=operator.itemgetter("episode"))
    return (name_, m)

series = [
          "How I Met Your Mother",
          "Doctor Who",
          "The Simpsons", 
          "Two and a Half Men",
          "Elementary",
          "Bones",
          "The Big Bang Theory",
          "Revolution"
         ]

episodes = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    fs = [executor.submit(get_newest_episode, s) for s in series]
    episodes = [f.result() for f in concurrent.futures.as_completed(fs)]
    
for name, d in episodes:
    if d: 
        print(name, "S%02dE%02d" % d["episode"], "-", d["size"], "-", d["uploaded"], 
                "(%s)" % d["name"], "[%s/%s]" % (d["leechers"], d["seeders"]))
        print(d["magnet"])
    else:
        print("Connection error when searching for %s." % name)
            
    print()
