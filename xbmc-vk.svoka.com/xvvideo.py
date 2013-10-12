#!/usr/bin/python
# -*- coding: utf-8 -*-
# VK-XBMC add-on
# Copyright (C) 2011 Volodymyr Shcherban

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


import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os, urllib, re, sys
import base64


from xml.dom import minidom

from vkparsers import GetVideoFiles
from xbmcvkui import XBMCVkUI_VKSearch_Base,SEARCH, PrepareString


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


SEARCH_RESULT, TOP_DOWNLOADS, SERIES, MY_VIDEOS, SEASONS, SEASON_SERIES = "SEARCH_RESULT,TOP_DOWNLOADS,SERIES,MY_VIDEOS,SEASONS,SEASON_SERIES".split(',')
MY_SHOWS_LIST = "MY_SHOWS_LIST"
SEARCH_RESULT_DOWNLOAD = "SEARCH_RESULT_DOWNLOAD"
VIDEO_DOWNLOAD = "VIDEO_DOWNLOAD"
GROUP_VIDEO = "GROUP_VIDEO"
GROUPS = "GROUPS"
NEXT_PAGE = "NEXT_PAGE"
# ALBUM_VIDEO = "ALBUM_VIDEO"



class XVKVideo(XBMCVkUI_VKSearch_Base):

    per_page = 50

    def __init__(self, *params):
        self.histId = None
        self.apiName = "video.search"
        self.locale = {"newSearch":__language__(30005), "history": __language__(30007), "input":__language__(30003)}
        XBMCVkUI_VKSearch_Base.__init__(self, *params)

    def DoSearchTweaks(self):
        if __settings__.getSetting('hdOnly') == 'true' or "hd" in self.params:
            self.searchTweaks["hd"] = "1"
        else:
            listItem = xbmcgui.ListItem(__language__(30019))
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH, query=self.searchTweaks["q"], hd = "1") , listItem, True)
        if __settings__.getSetting('sortLen') == 'true':
            self.searchTweaks["sort"] = "1"

    def ProcessFoundEntry(self, a):
        duration = str(datetime.timedelta(seconds=int(a["duration"])))
        title =   duration + " - " + PrepareString(a["title"])
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
                n = a[a.rfind("/")+1:]
                if a.startswith("http"):
                    n = __language__(30039) + " " + n
                else:
                    n = "YouTube: " + n
                listitem = xbmcgui.ListItem(n, "", self.params.get("thumb"), self.params.get("thumb"), path=a)
                listitem.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, a, listitem)
        if vf and __settings__.getSetting("ShowDownload"):        
            for a in vf:
                if a.startswith("http"):
                    listitem = xbmcgui.ListItem(__language__(30035) + " " + a[a.rfind("/")+1:], "", self.params.get("thumb"), self.params.get("thumb"))
                    xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=VIDEO_DOWNLOAD, thumb=self.params.get("thumb"), v=base64.encodestring(a).strip()), listitem, False)

    def Do_SEARCH_RESULT_DOWNLOAD(self):
        vf = GetVideoFiles("http://vkontakte.ru/video"  + self.params["v"])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(__language__(30035) + " " + a[a.rfind("/")+1:], "", self.params.get("thumb"), self.params.get("thumb"))
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=VIDEO_DOWNLOAD, thumb=self.params.get("thumb"), v=base64.encodestring(a).strip()), listitem, True)

    def Do_VIDEO_DOWNLOAD(self):
        downloadCmd = __settings__.getSetting("downloadCmd")
        if not downloadCmd:
            if xbmc.getCondVisibility("system.platform.windows"):
                downloadCmd = "start"
            else:
                downloadCmd = "open"
            __settings__.setSetting("downloadCmd", downloadCmd)

        url = base64.decodestring(self.params["v"])
        os.system(downloadCmd + " " + url)
        
        # dest = __settings__.getSetting('downloads')
        # n = 0
        # while not len(dest):
        #     xbmc.executebuiltin('XBMC.Notification("%s", "%s", 7)' % (__language__(30037),__language__(30038)))
        #     __settings__.openSettings()
        #     dest = __settings__.getSetting('downloads')
        #     n+=1
        #     if n>3 and not len(dest):
        #         return
        # import SimpleDownloader as downloader
        # downloader = downloader.SimpleDownloader()
        # url = base64.decodestring(self.params["v"])
        # user_keyboard = xbmc.Keyboard()
        # user_keyboard.setHeading(__language__(30036))
        # user_keyboard.setHiddenInput(False)
        # user_keyboard.setDefault(url[url.rfind('/')+1:])
        # user_keyboard.doModal()
        # if (user_keyboard.isConfirmed()):
        #     fn = user_keyboard.getText();
        #     ext = url[url.rfind('.'):]
        #     if fn[-len(ext):] != ext:
        #         fn += ext
        #     params = { "url": url, "download_path": dest }
        #     downloader.download(fn, params)

    def Do_HOME(self):
        XBMCVkUI_VKSearch_Base.Do_HOME(self)
        listItem = xbmcgui.ListItem(__language__(30010))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=TOP_DOWNLOADS) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30011))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SERIES) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30012))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=MY_VIDEOS) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30042))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=GROUPS) , listItem, True)

        self.friendsEntry()
        # listItem = xbmcgui.ListItem(__language__(30020))
        # xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=MY_SHOWS_LIST) , listItem, True)

    def Do_NEXT_PAGE(self):
        page = self.params.get('page')
        gid = self.params.get('gid')
        uid = self.params.get('uid')
        offset = self.per_page * int(page)
        if gid:
            v = self.api.call('video.get', gid=gid, count=self.per_page, offset=offset)
        elif uid:
            v = self.api.call('video.get', uid=uid, count=self.per_page, offset=offset)
        else:
            v = self.api.call('video.get', count=self.per_page, offset=offset)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
        if len(v[1:]) >= self.per_page:
            page = int(page); page += 1
            listItem = xbmcgui.ListItem(__language__(30044)%(page+1))
            if gid:
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=NEXT_PAGE, page=page, gid=gid) , listItem, True)
            else:
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=NEXT_PAGE, page=page, uid=uid) , listItem, True)

    def Do_GROUP_VIDEO(self):
        gid = self.params["gid"]
        v = self.api.call('video.get', gid=gid, count=self.per_page)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
            if len(v[1:]) >= self.per_page:
                listItem = xbmcgui.ListItem(__language__(30044)%2)
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=NEXT_PAGE, page=1, gid=gid) , listItem, True)

    def processFriendEntry(self, uid):
        v = self.api.call('video.get', uid=uid, count=200)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
            if len(v[1:]) >= self.per_page:
                listItem = xbmcgui.ListItem(__language__(30044)%2)
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=NEXT_PAGE, page=1, uid=uid) , listItem, True)

    def Do_GROUPS(self):
        resp = self.api.call('groups.get',extended=1)
        groups = resp[1:]
        for group in groups:
            listItem = xbmcgui.ListItem(group['name'], "", group['photo_big'])
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=GROUP_VIDEO, gid=group['gid'], thumb=group['photo_medium'])  , listItem, True)


    def Do_SERIES(self):
        html = urllib.urlopen("http://kinobaza.tv/series").read()
        r = re.compile(r'<img width="207" src="(.*?)" alt="(.*?)" class="poster-pic" />.*?<a href="http://kinobaza.tv/film/(.*?)/.*?span class="english">(.*?)</span>', re.DOTALL)
        res = r.findall(html)
        for thumb, ru, id, en in res:
            listItem = xbmcgui.ListItem(PrepareString(ru), en, thumb, thumb)
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEASONS,id=id, thumb=thumb), listItem, True)

    def Do_SEASONS(self):
        srl = minidom.parse(urllib.urlopen("http://kinobaza.tv/film/%s?format=xml" % self.params["id"]))
        n = 1
        for e in srl.getElementsByTagName("season"):
            episodes = len(e.getElementsByTagName("episode"))
            thumb = self.params["thumb"]
            listItem = xbmcgui.ListItem(__language__(30014) % (n,episodes), "", thumb, thumb)
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEASON_SERIES, thumb=thumb,
                                                                 id = self.params["id"], season = n), listItem, True)
            n += 1

    def Do_SEASON_SERIES(self):
        srl = minidom.parse(urllib.urlopen("http://kinobaza.tv/film/%s?format=xml" % self.params["id"]))
        film = srl.getElementsByTagName("film")[0]
        season = srl.getElementsByTagName("season")[int(self.params["season"])-1]
        season_num = season.attributes["number"].value
        for e in season.getElementsByTagName("episode"):
            if not(e.attributes["description"].value or e.attributes["name"].value or e.attributes["original_name"].value):
                continue
            n = e.attributes["number"].value
            thumb = self.params["thumb"]
            title = e.attributes["name"].value or e.attributes["original_name"].value
            desc = e.attributes["description"].value
            title = __language__(30015) % n + (title and (u": " + title))
            listItem =  xbmcgui.ListItem(PrepareString(title), desc, thumb, thumb)
            q = "%s  %s   %s" % (film.attributes["name"].value,season_num, n)
            q = q.encode('utf-8')
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH, query=q), listItem, True)

    def Do_MY_VIDEOS(self):
        v = self.api.call("video.get", count=self.per_page)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
            if len(v[1:]) >= self.per_page:
                listItem = xbmcgui.ListItem(__language__(30044)%2)
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=NEXT_PAGE, page=1) , listItem, True)

    def Do_TOP_DOWNLOADS(self):
        html = urllib.urlopen("http://kinobaza.tv/ratings/top-downloadable").read()
        regex = re.compile(r'<img width="60" src="(.*?)" alt="(.*?)" class="poster-pic" />.*?<span class="english">(.*?)</span>',re.UNICODE|re.DOTALL)
        r = regex.findall(html)
        for thumb, ru, en in r:
            thumb = thumb.replace('60.jpg','207.jpg')
            title = ru.decode("utf-8") + " / " + en.decode('utf-8')
            listItem = xbmcgui.ListItem(PrepareString(title) , en, thumb, thumb)
            q= ru + " " + en.replace("(","").replace(")","")
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH,query=q), listItem, True)

    def Do_MY_SHOWS_LIST(self):
        pass
