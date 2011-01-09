__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from xbmcvkui import XBMCVkUI_Base,HOME
from datetime import datetime

__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
saved_search_file = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')

#modes
ALBUM = "ALBUM"


from xml.sax.saxutils import unescape



class XVKImage(XBMCVkUI_Base):

    def Do_HOME(self):
        for title, title2, thumb, id, owner in self.GetAlbums():
            listItem = xbmcgui.ListItem(title, title2, thumb, thumb, ) #search history
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=ALBUM, album=id, user=owner) , listItem, True)


            
    def Do_ALBUM(self):
        album = self.api.call("photos.get", uid = self.params["user"], aid = self.params["album"])
        photos = []
        for cameo in album:
            title = None
            if cameo["text"]:
                title = cameo["text"] + u" (" + unicode(str(datetime.fromtimestamp(int(cameo["created"])))) + u")"
            else:
                title =  unicode(str(datetime.fromtimestamp(int(cameo["created"]))))
            title = unescape(title, {"&apos;": "'", "&quot;": '"'})
            e = ( title,
                  cameo.get("src_xxbig") or cameo.get("src_xbig") or cameo.get("src_big") or cameo["src"],
                  cameo["src"] )
            photos.append(e)
        for title, url, thumb in photos:
            listItem = xbmcgui.ListItem(title, "", thumb, thumb, ) #search history
            xbmcplugin.addDirectoryItem(self.handle, url , listItem, False)



    def GetAlbums(self):
        albums=self.api.call("photos.getAlbums")
        q = []
        for album in albums:
            q.append(album["owner_id"] + "_" + album["thumb_id"])

        thumbs = self.api.call("photos.getById", photos=",".join(q))
        album_thumbs = dict()
        for e in thumbs:
            album_thumbs[e["aid"]] = e["src"]

        items = []
        for a in albums:
            e = ( a["title"] + unicode(" (%s photo)" % a["size"]),
                  a["description"],
                  album_thumbs[a["aid"]],
                  a["aid"],
                  a["owner_id"]  )
            items.append(e)
        return items