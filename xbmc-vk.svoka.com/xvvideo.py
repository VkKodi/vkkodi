#!/usr/bin/python
# -*- coding: utf-8 -*-
# This code written by anonymous, but modified by me, Shchvova!
# Please leave my copyrights here cause as you can notice
# "Copyright" always means "absolutely right copying".
# Illegal copying of this code prohibited by real patsan's law!

import re
import urllib
from xml.sax.saxutils import unescape

__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from vkparsers import GetVideoFiles
from xbmcvkui import XBMCVkUI_VKSearch_Base,SEARCH


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


SEARCH_RESULT, TOP_DOWNLOADS, SERIES, MY_VIDEOS = "SEARCH_RESULT,TOP_DOWNLOADS,SERIES,MY_VIDEOS".split(',')

class XVKVideo(XBMCVkUI_VKSearch_Base):
    def __init__(self, *params):
        self.histId = None
        self.apiName = "video.search"
        self.locale = {"newSearch":__language__(30005), "history": __language__(30007), "input":__language__(30003)}
        XBMCVkUI_VKSearch_Base.__init__(self, *params)

    def ProcessFoundEntry(self, a):
        duration = str(datetime.timedelta(seconds=int(a["duration"])))
        title =   duration + " - " + unescape(a["title"], {"&apos;": "'", "&quot;": '"'})
        videos = str(a["owner_id"])+"_"+str(a.get("id") or a.get("vid"))
        thumb = a.get("thumb") or a.get("image")
        listItem = xbmcgui.ListItem(title, a["description"], thumb, thumb)
        listItem.setInfo(type = "Video", infoLabels = {
            "title"     : title
            ,"duration" : duration
            ,"tagline" : a["description"]
            } )
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_RESULT, thumb=thumb, v=videos),
                                    listItem, True)

    def Do_SEARCH_RESULT(self):
        vf = GetVideoFiles("http://vkontakte.ru/video"  + self.params["v"])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(a[a.rfind("/")+1:], "", self.params.get("thumb"), self.params.get("thumb"))
                xbmcplugin.addDirectoryItem(self.handle, a, listitem)


    def Do_HOME(self):
        XBMCVkUI_VKSearch_Base.Do_HOME(self)
        listItem = xbmcgui.ListItem(__language__(30010))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=TOP_DOWNLOADS) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30011))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SERIES) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30012))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=MY_VIDEOS) , listItem, True)

    def Do_SERIES(self):
        pass

    def Do_MY_VIDEOS(self):
        v = self.api.call("video.get")
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
        

    def Do_TOP_DOWNLOADS(self):
        html = urllib.urlopen("http://kinobaza.tv/ratings/top-downloadable").read()
        regex = re.compile(r'<img width="60" src="(.*?)" alt="(.*?)" class="poster-pic" />.*?<span class="english">(.*?)</span>',re.UNICODE|re.DOTALL)
        r = regex.findall(html)
        for thumb, ru, en in r:
            listItem = xbmcgui.ListItem(ru, en, thumb, thumb)
            q = ru
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH,query=q), listItem, True)
