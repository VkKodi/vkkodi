#!/usr/bin/python
# -*- coding: utf-8 -*-
# VK-XBMC add-on
# Copyright (C) 2011 Volodymyr Shcherban
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = 'Volodymyr Shcherban'

import urllib, re

try:
    import json
except ImportError:
    import simplejson as json


def GetVideoFiles(url):
    html = urllib.urlopen(url).read()
    player = re.findall(r"loadFlashPlayer\((.*?}),", html)
    if not player:
        player = re.findall(r"\\nvar vars =(.*?});", html)
        if not player:
            return ["/unable to play " + url]
        else:
            tmp = ""
            for a in player[0]:
                if ord(a)< 128:
                    tmp += a
                else:
                    tmp += urllib.quote(a)
            player[0] = filter(lambda x: x != "\\", tmp)
    jsonStr = player[0]
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


