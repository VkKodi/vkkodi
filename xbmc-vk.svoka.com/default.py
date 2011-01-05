#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writen by me, yeah! Shchvova (www.svoka.com)
# Please leave my copyrights here cause as you can notice
# "Copyright" always means "absolutely right copying".
# Illegal copying of this code prohibited by real patsan's law!

import urllib, urllib2, cookielib, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, httplib, socket
import base64
import random
import sha
import datetime

try:
    import json
except ImportError:
    import simplejson as json

try:
   from hashlib import md5
except ImportError:
   from md5 import md5


APP_ID = "2054573"


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

LOGIN_URL = __settings__.getSetting('authUrl')
while not LOGIN_URL.startswith("http://vkontakte.ru/api/login_success.html"):
    filePath = xbmc.translatePath("special://temp/vk.txt")
    fl = open(filePath, 'w')
    strQ = """# Follow this link in your browser:
http://vkontakte.ru/login.php?app=%s&layout=popup&type=browser&settings=16
# you will be redirected to page with text 'Login success',
# copy ADDRESS of page containing 'Login sucess' text to next empty line in this file, save and close it
# return to XBMC and press ok (after closing this file)

""" % APP_ID
    if xbmc.getCondVisibility( "system.platform.windows" ):
        strQ = strQ.replace("\n","\r\n")
    fl.write(strQ)
    fl.close()
    urr = xbmc.Keyboard()
    urr.setHeading("Open file and follow instructions in it")
    urr.setDefault(filePath)
    urr.doModal()
    if (urr.isConfirmed()):
        fl = open(filePath, 'r')
        for line in fl.readlines():
            if line.strip().startswith("http://vkontakte.ru/api/login_success.html"):
                LOGIN_URL = line.strip()
                __settings__.setSetting('authUrl', LOGIN_URL)
                fl.close()
                os.remove(filePath)
                break
        fl.close()
    else:
        sys.exit()



PLUGIN_NAME = 'VKontakte Search'


vkcookiefile = os.path.join(xbmc.translatePath('special://temp/'), 'vkontakte-cookie.sess')
saved_search = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')




class VkontakteCookie:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookie = None

    def get_s_value(self):
        #Возвращает уникальный идентификатор, который выдается на домене login.vk.com
        host = 'http://login.vk.com/?act=login'
        post = urllib.urlencode({'email' : self.email,
                                 'expire' : '',
                                 'pass' : self.password,
                                 'vk' : ''})

        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13 (.NET CLR 3.5.30729)',
                   'Host' : 'login.vk.com',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache',
                  }

        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        ssv = data.read()
        return re.findall(r"name='s' value='(.*?)'", ssv)[0]

    def get_cookie(self):
        #Возвращает remixsid из куки
        if self.cookie: return self.cookie

        host = 'http://vkontakte.ru/login.php?op=slogin'
        post = urllib.urlencode({'s' : self.get_s_value()})
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://login.vk.com/?act=login',
                   'Connection' : 'close',
                   'Cookie' : 'remixchk=5; remixsid=nonenone',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache'
                  }
        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        cookie_src = data.info().get('Set-Cookie')
        cooke_str = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.vkontakte\.ru(?:,\s)?)', '', cookie_src)
        self.cookie =  cooke_str.split("=")[-1].split(";")[0].strip()
        if not self.cookie:
            raise Exception('Wront login')
        return self.cookie


class VkiApi:

    @classmethod
    def fromURL(cls, url):
        # http://vkontakte.ru/login.php?app=2054573&layout=popup&type=browser&settings=16
        decoded=urllib.unquote(url)
        start = decoded.find("{")
        obj = json.loads(decoded[start:])
        return cls(APP_ID, obj["sid"], obj["mid"], obj["secret"])

    def __init__(self, api_id, sid, mid, secret):
        global USERNAME, USERPASS
        self.vkcookie = None
        if os.path.isfile(vkcookiefile):
            fh= open(vkcookiefile, 'r')
            self.vkcookie = fh.read()
            fh.close()

        while not self.vkcookie:
            try:
                cookieObj = VkontakteCookie(USERNAME, USERPASS)
                self.vkcookie = cookieObj.get_cookie()
            except Exception:
                self.vkcookie = None
                if not askLogin():
                    return

        fh= open(vkcookiefile, 'w')
        fh.write(self.vkcookie)
        fh.close()
        
        self.param = dict()
        self.param["v"] = "3.0"
        self.param["format"] = "JSON"
        self.param["api_id"] = api_id
        self.param["sid"] = sid
        self.mid = str(mid)
        self.secret = str(secret)

    def call(self, api, **vars):
        v = {"method" : api}
        v.update(self.param)
        v.update(vars)

        keys= sorted(v.keys())

        toCheck = "".join(["%s=%s" % (str(key), str(v[key])) for key in keys if key!="sid"])

        toCheck = self.mid + toCheck + self.secret

        v["sig"]=md5(toCheck).hexdigest()

        request = "&".join(["%s=%s" % (str(key), urllib.quote(str(v[key]))) for key in v.keys()])
        request_url = "http://vkontakte.ru/api.php?"+request

        print request_url
        reply = urllib.urlopen(request_url)
        #replystr = reply.read()
        #resp = json.loads(replystr)
        resp = json.load(reply)
        if "error" in resp:
            print "Error" + resp;
            return None
        else:
            return resp["response"]

    def getVideoFile(self, url):
        proc = urllib2.HTTPCookieProcessor()
        proc.cookiejar.set_cookie(cookielib.Cookie(0, 'remixsid', self.vkcookie,
                                   '80', False, 'vkontakte.ru', True, False, '/',
                                   True, False, None, False, None, None, None))
        opener = urllib2.build_opener(urllib2.HTTPHandler(),
                                      proc)
        opener.addheaders.append(('User-agent', 'Mozilla/5.0 (compatible)'))
        videoReply = opener.open(url).read()
        opener.close()
        bg = "loadFlashPlayer({"
        index = videoReply.find(bg)
        if index == -1:
            return None

        flashPlayerParams = videoReply[index+len(bg)-1:videoReply.find("},", index)+1]
        prs = json.loads(flashPlayerParams)
        urlStart = prs["host"] + "u" + str(prs["uid"]) + "/video/" + str(prs["vtag"])
        rsls = ["240", "360", "480", "720", "1080"]
        videoURLs = []
        if prs["no_flv"]!=1:
            videoURLs.append(urlStart + ".flv")
        if prs["hd"]>0:
            for i in range(prs["hd"]+1):
                videoURLs.append(urlStart + "." + rsls[i] + ".mp4")
        videoURLs.reverse()
        return videoURLs





def askLogin():
    global USERNAME, USERPASS
    user_keyboard = xbmc.Keyboard()
    user_keyboard.setHeading("Vkontakte email")
    user_keyboard.setDefault(USERNAME)
    user_keyboard.doModal()
    if (user_keyboard.isConfirmed()):
        USERNAME = user_keyboard.getText()
        pass_keyboard = xbmc.Keyboard()
        pass_keyboard.setHeading("Password")
        pass_keyboard.setHiddenInput(True)
        pass_keyboard.doModal()
        if (pass_keyboard.isConfirmed()):
            USERPASS = pass_keyboard.getText()
            __settings__.setSetting('username', USERNAME)
            __settings__.setSetting('password', USERPASS)
            return True
        else:
            return False
    else:
        return False

try:
    api = VkiApi.fromURL(LOGIN_URL)
except Exception:
    __settings__.setSetting('authUrl', "")

if api.vkcookie:
    if sys.argv[2]:
        print sys.argv[2][0]
    if not sys.argv[2] or sys.argv[2][:2]=='?S':
        query = ""
        result = None
        searchLineKbd = xbmc.Keyboard()
        searchLineKbd.setHeading("Search query")
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
        vf = api.getVideoFile("http://vkontakte.ru/video"  + sys.argv[2][2:])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(a[-8:])
                xbmcplugin.addDirectoryItem(handle, a, listitem)
        xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
        xbmcplugin.endOfDirectory(handle)
