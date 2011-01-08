#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writen by me, yeah! Shchvova (www.svoka.com)
# Please leave my copyrights here cause as you can notice
# "Copyright" always means "absolutely right copying".
# Illegal copying of this code prohibited by real patsan's law!

import sys, xbmcaddon, xbmc, xbmcgui, xbmcplugin, os, urllib
import datetime

from vkapp import GetApi
from vkparsers import GetVideoFiles

__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString

handle = int(sys.argv[1])
PLUGIN_NAME = 'VK-xbmc'
saved_search_file = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')


#modes
HOME, SEARCH, SEARCH_HISTORY, SEARCH_RESULT = "HOME,SEARCH,SEARCH_HISTORY,SEARCH_RESULT".split(",")



class XBMCVkUI:
    def __init__(self, parameters):
        xbmc.output(repr(sys.argv))
        xbmc.output(repr(parameters))
        self.params = parameters
        self.Populate(getattr(self, "Do_" + self.params["mode"], self.Do_HOME))

    def Populate(self, content):
        listItem = xbmcgui.ListItem(__language__(30005)) #new search - always first element
        xbmcplugin.addDirectoryItem(handle, self.GetURL(mode=SEARCH) , listItem, True)
        content()
        xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
        xbmcplugin.endOfDirectory(handle)


    def Do_HOME(self):
        if os.path.isfile(saved_search_file):
            listItem = xbmcgui.ListItem(__language__(30007)) #search history
            xbmcplugin.addDirectoryItem(handle, self.GetURL(mode=SEARCH_HISTORY) , listItem, True)

    def Do_SEARCH(self):
        query = self.params.get("query")
        if not query:
            kb = xbmc.Keyboard()
            kb.setHiddenInput(False)
            kb.setHeading(__language__(30003))
            history = self.GetSearchHistory()
            if history:
                kb.setDefault(history[0])
            kb.doModal()
            if (kb.isConfirmed()):
                query = kb.getText()
        result = None
        if query:
            self.AddSearchHistory(query)
            result = api.call("video.search",q=query, count="10")
        if result:
            for a in result:
                duration = str(datetime.timedelta(seconds=int(a["duration"])))
                title = duration + " - " + a["title"]
                videos = a["owner_id"]+"_"+a["id"]
                listItem = xbmcgui.ListItem(title, a["description"], a["thumb"], a["thumb"])
                listItem.setInfo(type = "Video", infoLabels = {
                    "title"     : title
                    ,"duration" : duration
                    ,"tagline" : a["description"]
                    } )
                xbmcplugin.addDirectoryItem(handle, self.GetURL(mode=SEARCH_RESULT, thumb=a["thumb"], v=videos),
                                            listItem, True)

    def GetSearchHistory(self):
        history = []
        if os.path.isfile(saved_search_file):
            fl = open(saved_search_file,"r")
            history = fl.readlines()
            history = map(lambda s: s.strip(), history)
            history = filter(None, history)
            fl.close()
        return history

    def AddSearchHistory(self, query):
        query = query.strip()
        if not query:
            return
        max = int(__settings__.getSetting('history'))
        lines = []
        if os.path.isfile(saved_search_file):
            fl = open(saved_search_file,"r")
            lines = fl.readlines()
            fl.close()
        lines = map(lambda s: s.strip(), lines)
        lines = filter(None, lines)
        while query in lines:   #could replace with `if`, nothing should change...
            lines.remove(query)
        lines.insert(0, query)
        fl = open(saved_search_file, "w")
        fl.write("\n".join(lines[:max]))
        fl.close()


    def Do_SEARCH_HISTORY(self):
        history = self.GetSearchHistory()
        if history:
            for q in history:
                listItem = xbmcgui.ListItem(q)
                xbmcplugin.addDirectoryItem(handle, self.GetURL(mode=SEARCH,query=q), listItem, True)
                

    def Do_SEARCH_RESULT(self):
        vf = GetVideoFiles("http://vkontakte.ru/video"  + self.params["v"])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(a[-8:], "", self.params.get("thumb"), self.params.get("thumb"))
                xbmcplugin.addDirectoryItem(handle, a, listitem)


    def GetURL(self, __dict_params=dict(), **parameters):
        __dict_params.update(parameters)
        return sys.argv[0] + "?" + urllib.urlencode(__dict_params)


api = GetApi()
if api:
    params = {"mode" : HOME}
    if sys.argv[2]:
        l = [s.split("=") for s in sys.argv[2][1:].split("&")]
        l = map(lambda e: (e[0], urllib.unquote_plus(e[1])) , l)
        params.update(dict(l))
    ui = XBMCVkUI(params)
    
else:
    listitem = xbmcgui.ListItem("-- something wrong, try again --")
    xbmcplugin.addDirectoryItem(handle, sys.argv[0], listitem, True)
    xbmc.output("THIS IS THE END")
