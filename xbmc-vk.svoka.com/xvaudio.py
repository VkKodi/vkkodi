__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from xbmcvkui import XBMCVkUI_Base,HOME
import datetime

__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
saved_search_file = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')

#modes
ALBUM = "ALBUM"


class XVKAudio(XBMCVkUI_Base):

    def Do_HOME(self):
        self.api.call("photos.getAlbums")
        for title, url in self.GetMusic():
            listItem = xbmcgui.ListItem(title) #search history
            xbmcplugin.addDirectoryItem(self.handle, url , listItem, False)



    def GetMusic(self):
        q = []
        for a in self.api.call("audio.get"):
            title = a.get("artist")
            if title:
                title += u" : "
            title += a.get("title")
            d = unicode(datetime.timedelta(seconds=int(a["duration"])))
            q.append( (d + ") " + title, a["url"]) )
        return q