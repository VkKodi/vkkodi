__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from vkparsers import GetVideoFiles
from xbmcvkui import XBMCVkUI_Base,HOME


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
saved_search_file = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search.sess')

#modes
SEARCH, SEARCH_HISTORY, SEARCH_RESULT = "SEARCH,SEARCH_HISTORY,SEARCH_RESULT".split(",")




class XVKVideo(XBMCVkUI_Base):

    def PrefixActions(self):
        listItem = xbmcgui.ListItem(__language__(30005)) #new search - always first element
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH) , listItem, True)

    def Do_HOME(self):
        if os.path.isfile(saved_search_file):
            listItem = xbmcgui.ListItem(__language__(30007)) #search history
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_HISTORY) , listItem, True)

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
            if kb.isConfirmed():
                query = kb.getText()
        result = None
        if query:
            self.AddSearchHistory(query)
            result = self.api.call("video.search",q=query, count="10")
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
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_RESULT, thumb=a["thumb"], v=videos),
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
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH,query=q), listItem, True)


    def Do_SEARCH_RESULT(self):
        vf = GetVideoFiles("http://vkontakte.ru/video"  + self.params["v"])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(a[-8:], "", self.params.get("thumb"), self.params.get("thumb"))
                xbmcplugin.addDirectoryItem(self.handle, a, listitem)