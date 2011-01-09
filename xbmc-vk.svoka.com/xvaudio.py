from xml.sax.saxutils import unescape

__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from xbmcvkui import XBMCVkUI_VKSearch_Base,HOME
import datetime

__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
saved_search_file = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')

#modes
ALBUM,MY_MUSIC = "ALBUM,MY_MUSIC".split(',')

class XVKAudio(XBMCVkUI_VKSearch_Base):
    def __init__(self, *params):
        self.histId = "Audio"
        self.apiName = "audio.search"
        self.locale = {"newSearch":__language__(30008), "history": __language__(30007), "input":__language__(30003)}
        XBMCVkUI_VKSearch_Base.__init__(self, *params)

    def Do_HOME(self):
        XBMCVkUI_VKSearch_Base.Do_HOME(self)
        listItem = xbmcgui.ListItem(__language__(30009))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=MY_MUSIC) , listItem, True)



    def transformResult(self,res):
        if res and res[0]:
            return res[1:]
        else:
            return None

    def ProcessFoundEntry(self, a):
        self.AddAudioEntry(a)

            
    def Do_MY_MUSIC(self):
        for a in self.api.call("audio.get"):
            self.AddAudioEntry(a)



    def AddAudioEntry(self, a):
        title = a.get("artist")
        if title:
            title += u" : "
        title += a.get("title")
        d = unicode(datetime.timedelta(seconds=int(a["duration"])))
        title = d + u" - " + title
        listItem = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(self.handle, a["url"] , listItem, False)
