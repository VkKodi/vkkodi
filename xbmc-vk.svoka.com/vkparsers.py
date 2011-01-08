#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writen by me, yeah! Shchvova (www.svoka.com)
# Please leave my copyrights here cause as you can notice
# "Copyright" always means "absolutely right copying".
# Illegal copying of this code prohibited by real patsan's law!

import urllib, re

try:
    import json
except ImportError:
    import simplejson as json


def GetVideoFiles(url):
    html = urllib.urlopen(url).read()
    jsonStr = re.findall(r"loadFlashPlayer\((.*?}),", html)[0]
    prs = json.loads(jsonStr)

    urlStart = prs["host"] + "u" + str(prs["uid"]) + "/video/" + str(prs["vtag"])

    resolutions = ["240", "360", "480", "720", "1080"]
    videoURLs = []
    if prs["no_flv"]!=1:
        if str(prs["uid"])=="0": #strange bhvour on old videos
            urlStart = "http://" + prs["host"] + "/assets/videos/" + str(prs["vtag"]) + str(prs["vkid"]) + ".vk"
        videoURLs.append(urlStart + ".flv")

    if prs["hd"]>0 or prs["no_flv"]==1:
        for i in range(prs["hd"]+1):
            videoURLs.append(urlStart + "." + resolutions[i] + ".mp4")

    videoURLs.reverse()
    return videoURLs


