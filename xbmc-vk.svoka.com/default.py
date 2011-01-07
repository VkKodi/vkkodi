#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writen by me, yeah! Shchvova (www.svoka.com)
# Please leave my copyrights here cause as you can notice
# "Copyright" always means "absolutely right copying".
# Illegal copying of this code prohibited by real patsan's law!

import sys,urllib, urllib2, cookielib, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, httplib, socket
import base64
import random
import sha
import datetime

import webbrowser

try:
    import json
except ImportError:
    import simplejson as json

try:
   from hashlib import md5
except ImportError:
   from md5 import md5



__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


handle = int(sys.argv[1])

APP_ID = "2054573"
PLUGIN_NAME = 'VK-xbmc'
USER_AUTH_URL  = "http://j.mp/vk-xbmc"

vkcookiefile = os.path.join(xbmc.translatePath('special://temp/'), 'vkontakte-cookie.sess')
saved_search = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')
authUrlFile = os.path.join(xbmc.translatePath('special://temp/'), 'vk-auth-url.sess')




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

        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
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

# http://vkontakte.ru/login.php?app=2054573&layout=popup&type=browser&settings=16
class VkiApi:
    def __init__(self):
        self.vkcookie = None
        self.initCookie()
        
        #auth vk app
        loginSuccessUrl = self.AuthVKApp()
        if not loginSuccessUrl:
            self.vkcookie = None
            return

        decoded=urllib.unquote(loginSuccessUrl)
        start = decoded.find("{")
        obj = json.loads(decoded[start:])
        api_id, sid, mid, secret = (APP_ID, obj["sid"], obj["mid"], obj["secret"])

        #param is API call parameters
        self.param = dict()
        self.param["v"] = "3.0"
        self.param["format"] = "JSON"
        self.param["api_id"] = api_id
        self.param["sid"] = sid
        self.mid = str(mid)
        self.secret = str(secret)

    def initCookie(self, resetCookie=False):
        self.vkcookie = None
        if os.path.isfile(vkcookiefile):
            if resetCookie:
                xbmc.output("reset cookie")
                os.remove(vkcookiefile)
            else:
                fh= open(vkcookiefile, 'r')
                self.vkcookie = fh.read()
                fh.close()

        while not self.vkcookie:
            try:
                cookieObj = VkontakteCookie(__settings__.getSetting('username'), 
                                            __settings__.getSetting('password'))
                self.vkcookie = cookieObj.get_cookie()
            except Exception:
                self.vkcookie = None
                if not self.askLogin():
                    return

        fh= open(vkcookiefile, 'w')
        fh.write(self.vkcookie)
        fh.close()

    def askLogin():
        user_keyboard = xbmc.Keyboard()
        user_keyboard.setHeading(__language__(30001))
        user_keyboard.setHiddenInput(False)
        user_keyboard.setDefault(__settings__.getSetting('username'))
        user_keyboard.doModal()
        if (user_keyboard.isConfirmed()):
            userName = user_keyboard.getText()
            pass_keyboard = xbmc.Keyboard()
            pass_keyboard.setHeading(__language__(30002))
            pass_keyboard.setHiddenInput(True)
            pass_keyboard.doModal()
            if (pass_keyboard.isConfirmed()):
                __settings__.setSetting('username', userName)
                __settings__.setSetting('password', pass_keyboard.getText())
                return True
            else:
                return False
        else:
            return False
        

    def AuthVKApp(self, showBrowser = False):
        authUrl = "http://vkontakte.ru/login.php?app=%s&layout=popup&type=browser&settings=16" % APP_ID
        ret = ""
        if os.path.isfile(authUrlFile):
            f = open(authUrlFile, "r")
            ret = f.read()
            f.close()

        if showBrowser:
            if xbmc.getCondVisibility( "system.platform.windows" ):
                os.system('start %s'% USER_AUTH_URL) #Windows su^W can't hadle full url
            else:
                os.system('open "%s"'% authUrl)

            kb = xbmc.Keyboard()
            kb.setHiddenInput(False)
            kb.setHeading(__language__(30004))
            kb.setDefault(USER_AUTH_URL)
            kb.doModal()
            if(not kb.isConfirmed()):
                return ""

        proc = urllib2.HTTPCookieProcessor()
        proc.cookiejar.set_cookie(cookielib.Cookie(0, 'remixsid', self.vkcookie,
                                   '80', False, 'vkontakte.ru', True, False, '/',
                                   True, False, None, False, None, None, None))
        opener = urllib2.build_opener(urllib2.HTTPHandler(), proc)
        opener.addheaders.append(('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13'))
        opener.addheaders.append(('Referer', authUrl))
        ret = opener.open(authUrl).url
        opener.close()

        if not ret.startswith("http://vkontakte.ru/api/login_success"):
            if showBrowser:
                #this is third or more time we got here. Lets try to reset cookie
                self.initCookie(True)
            #try again with browser, app is not authorized
            return self.AuthVKApp(True)

        fl = open(authUrlFile, "w")
        fl.write(ret)
        fl.close()
        return ret

        

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

        reply = urllib.urlopen(request_url)
        #replystr = reply.read()
        #resp = json.loads(replystr)
        resp = json.load(reply)
        if "error" in resp:
            if os.path.isfile(authUrlFile):
                os.remove(authUrlFile)
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
            if str(prs["uid"])=="0": #strange bhvour on old videos
                urlStart = "http://" + prs["host"] + "/assets/videos/" + str(prs["vtag"]) + str(prs["vid"]) + ".vk"
            videoURLs.append(urlStart + ".flv")

        if prs["hd"]>0:
            for i in range(prs["hd"]+1):
                videoURLs.append(urlStart + "." + rsls[i] + ".mp4")
        videoURLs.reverse()
        return videoURLs




api = None
try:
    api = VkiApi()
except Exception , e:
    if os.path.isfile(authUrlFile):
        os.remove(authUrlFile)
    xbmc.output("Error" + repr(e))
    raise e


if api and api.vkcookie:
    if sys.argv[2]:
        print sys.argv[2][0]
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
        vf = api.getVideoFile("http://vkontakte.ru/video"  + sys.argv[2][2:])
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
