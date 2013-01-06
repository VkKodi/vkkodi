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
import urllib
from vk_auth import auth
__author__ = 'Volodymyr Shcherban'

import urllib2, cookielib, xbmcaddon, xbmc, xbmcgui, xbmcplugin, os, re


try:
    import json
except ImportError:
    import simplejson as json

try:
   from hashlib import md5
except ImportError:
   from md5 import md5

from vkcookie import GetCookie


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


APP_ID = "2054573"
USER_AUTH_URL  = "http://j.mp/vk-xbmc-media"
authUrlFile = os.path.join(xbmc.translatePath('special://temp/').decode('utf-8'), u'vk-auth-url.sess')

OAUTH_URL="http://oauth.vk.com/authorize?client_id=%s&scope=friends,photos,audio,video,offline&redirect_uri=http://oauth.vk.com/blank.html&display=wap&response_type=token" % APP_ID


from vkapicaller import ApiFromURLNew as UrlToApi

class XBMCVkAppCreator:
    def __init__(self):
        self.VkInstance = None
        self.cookie = None
        pass

    def GetInstance(self):
        return self.VkInstance or self.NewInstance()

    def NewInstance(self):
        loginSuccessUrl = self._AuthVKAppNew()
        if not loginSuccessUrl:
            raise Exception("Error, could not authorize application")
        self.VkInstance = UrlToApi(APP_ID, loginSuccessUrl)
        return self.VkInstance


    def _AuthVKAppNew(self, ignoreFile=False):
        if os.path.isfile(authUrlFile) and not ignoreFile:
            f = open(authUrlFile, "r")
            ret = f.read()
            f.close()
            return ret

        login = None
        accUrl=""
        isLoginPassword = len(__settings__.getSetting('password')) and len(__settings__.getSetting('username'))
        count = 5;
        while not accUrl and count>0:
            if not isLoginPassword:
                if not self._askLogin():
                    raise Exception("no valid user/password provided")
            isLoginPassword = False
            count -= 0;
            try:
                token, id = auth(__settings__.getSetting('username'),__settings__.getSetting('password'), APP_ID,'friends,groups,photos,audio,video,offline');
                accUrl = 'http://oauth.vk.com/blank.html#access_token='+token+'&expires_in=0&user_id='+id
            except:
                pass

        fl = open(authUrlFile, "w")
        fl.write(accUrl)
        fl.close()
        return accUrl


    def _AuthVKApp(self, showBrowser = False):
        if os.path.isfile(authUrlFile):
            f = open(authUrlFile, "r")
            ret = f.read()
            f.close()
            return ret

        authUrl = "http://vk.com/login.php?app=%s&layout=popup&type=browser&settings=28" % APP_ID
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
        proc.cookiejar.set_cookie(cookielib.Cookie(0, 'remixsid', self._initCookie(),
                                   '80', False, 'vk.com', True, False, '/',
                                   True, False, None, False, None, None, None))
        opener = urllib2.build_opener(urllib2.HTTPHandler(), proc)
        opener.addheaders.append(('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13'))
        opener.addheaders.append(('Referer', authUrl))
        ret = opener.open(authUrl).url
        opener.close()
        if not ret.startswith("http://vk.com/api/login_success"):
            #try again with browser, app is not authorized
            return self._AuthVKApp(True)

        fl = open(authUrlFile, "w")
        fl.write(ret)
        fl.close()
        return ret

    def _initCookie(self):
        while not self.cookie:
            try:
                self.cookie = GetCookie(__settings__.getSetting('username'),
                                      __settings__.getSetting('password'))
            except Exception:
                self.cookie = None
                if not self._askLogin():
                    return ""
        return self.cookie


    def _askLogin(self):
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






appManager = XBMCVkAppCreator()

def GetApi():
    try:
        return appManager.GetInstance()
    except Exception, e:
        xbmc.log("CAUGHT ERROR" + str(e))
        if os.path.isfile(authUrlFile):
            os.remove(authUrlFile)
        #return None
        raise


