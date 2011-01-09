from xml.sax.saxutils import unescape

__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from vkparsers import GetVideoFiles
from xbmcvkui import XBMCVkUI_VKSearch_Base,HOME


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


SEARCH_RESULT = "SEARCH_RESULT"

class XVKVideo(XBMCVkUI_VKSearch_Base):
    def __init__(self, *params):
        self.histId = None
        self.apiName = "video.search"
        self.locale = {"newSearch":__language__(30005), "history": __language__(30007), "input":__language__(30003)}
        XBMCVkUI_VKSearch_Base.__init__(self, *params)

    def ProcessFoundEntry(self, a):
            duration = str(datetime.timedelta(seconds=int(a["duration"])))
            title =   duration + " - " + unescape(a["title"], {"&apos;": "'", "&quot;": '"'})
            videos = a["owner_id"]+"_"+a["id"]
            listItem = xbmcgui.ListItem(title, a["description"], a["thumb"], a["thumb"])
            listItem.setInfo(type = "Video", infoLabels = {
                "title"     : title
                ,"duration" : duration
                ,"tagline" : a["description"]
                } )
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_RESULT, thumb=a["thumb"], v=videos),
                                        listItem, True)

    def Do_SEARCH_RESULT(self):
        vf = GetVideoFiles("http://vkontakte.ru/video"  + self.params["v"])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(a[a.rfind("/")+1:], "", self.params.get("thumb"), self.params.get("thumb"))
                xbmcplugin.addDirectoryItem(self.handle, a, listitem)
                