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
saved_search = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')


api = GetApi()
if api:
    #params = {"mode" : "home"}
    #params.update(urllib.decode(sys.argv[2])

    if not sys.argv[2] or sys.argv[2][:2]=='?S':
        query = ""
        result = None
        searchLineKbd = xbmc.Keyboard()
        searchLineKbd.setHiddenInput(False)
        searchLineKbd.setHeading(__language__(30003))
        if os.path.isfile(saved_search):
            fl = open(saved_search,"r")
            searchLineKbd.setDefault(fl.read())
            fl.close()
        searchLineKbd.doModal()
        if (searchLineKbd.isConfirmed()):
            query = searchLineKbd.getText()
        if query:
            fl = open(saved_search,"w")
            fl.write(query)
            fl.close()
            result = api.call("video.search",q=query, count="10")
        if result:
            listitem = xbmcgui.ListItem("-- new search --")
            xbmcplugin.addDirectoryItem(handle, sys.argv[0], listitem, True)
            for a in result:
                title = str(datetime.timedelta(seconds=int(a["duration"]))) + ") " + a["title"]
                videos = a["owner_id"]+"_"+a["id"]
                listitem = xbmcgui.ListItem(title,  thumbnailImage = a["thumb"])
                listitem.setInfo(type = "Video", infoLabels = {
                    "Title":	title
                    } )
                xbmcplugin.addDirectoryItem(handle, sys.argv[0]+"?L"+ videos, listitem, True)
        else:
            listitem = xbmcgui.ListItem("-- nothing found. Search again --")
            xbmcplugin.addDirectoryItem(handle, sys.argv[0], listitem, True)
        xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
        xbmcplugin.endOfDirectory(handle)
    elif sys.argv[2][:2]=="?L":
        xbmc.output("http://vkontakte.ru/video"+ sys.argv[2][2:])
        vf = GetVideoFiles("http://vkontakte.ru/video"  + sys.argv[2][2:])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(a[-8:])
                xbmc.output("--- "+a)
                xbmcplugin.addDirectoryItem(handle, a, listitem)
        xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
        xbmcplugin.endOfDirectory(handle)
else:
    listitem = xbmcgui.ListItem("-- something wrong, try again --")
    xbmcplugin.addDirectoryItem(handle, sys.argv[0], listitem, True)
    xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
    xbmcplugin.endOfDirectory(handle)
    xbmc.output("THIS IS THE END")
