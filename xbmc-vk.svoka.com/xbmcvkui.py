__author__ = 'Shchvova'

import xbmcplugin, urllib, sys, os

PLUGIN_NAME = 'VK-xbmc'

HOME = 'HOME'

class XBMCVkUI_Base:
    def __init__(self, parameters, handle, api):
        self.api = api
        self.handle = handle
        self.params = parameters
        self.Populate(getattr(self, "Do_" + self.params["mode"], self.Do_HOME))

    def Populate(self, content):
        self.PrefixActions()
        content()
        xbmcplugin.setPluginCategory(self.handle, PLUGIN_NAME)
        xbmcplugin.endOfDirectory(self.handle)

    def PrefixActions(self):
        pass

    def Do_HOME(self):
        pass

    def GetURL(self, __dict_params=dict(), **parameters):
        #UNOCODE things here???
        __dict_params.update(parameters)
        return sys.argv[0] + "?" + urllib.urlencode(__dict_params)





import xbmc,xbmcaddon, xbmcgui

saved_search_file = os.path.join(xbmc.translatePath('special://temp/'), 'vk-search%s.sess')
__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
SEARCH, SEARCH_HISTORY = "SEARCH,SEARCH_HISTORY".split(",")



class XBMCVkUI_Search_Base(XBMCVkUI_Base):
    def PrefixActions(self):
        listItem = xbmcgui.ListItem(self.locale["newSearch"]) #new search - always first element
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH) , listItem, True)

    def Do_HOME(self):
        if self.GetSearchHistory(self.histId):
            listItem = xbmcgui.ListItem(self.locale["history"]) #search history
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_HISTORY) , listItem, True)

    def Do_SEARCH(self):
        query = self.params.get("query")
        if not query:
            kb = xbmc.Keyboard()
            kb.setHiddenInput(False)
            kb.setHeading(self.locale["input"])
            history = self.GetSearchHistory(self.histId)
            if history:
                kb.setDefault(history[0])
            kb.doModal()
            if kb.isConfirmed():
                query = kb.getText()
        self.Search(query)


    def Do_SEARCH_HISTORY(self):
        history = self.GetSearchHistory(self.histId)
        if history:
            for q in history:
                listItem = xbmcgui.ListItem(q)
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH,query=q), listItem, True)


    def GetSearchHistory(self, searchId = None):
        history = []
        if os.path.isfile(saved_search_file % searchId):
            fl = open(saved_search_file % searchId,"r")
            history = fl.readlines()
            history = map(lambda s: s.strip(), history)
            history = filter(None, history)
            fl.close()
        return history

    def AddSearchHistory(self, query, searchId = None):
        query = query.strip()
        if not query:
            return
        max = int(__settings__.getSetting('history'))
        lines = []
        if os.path.isfile(saved_search_file % searchId):
            fl = open(saved_search_file % searchId,"r")
            lines = fl.readlines()
            fl.close()
        lines = map(lambda s: s.strip(), lines)
        lines = filter(None, lines)
        while query in lines:   #could replace with `if`, nothing should change...
            lines.remove(query)
        lines.insert(0, query)
        fl = open(saved_search_file % searchId, "w")
        fl.write("\n".join(lines[:max]))
        fl.close()



class XBMCVkUI_VKSearch_Base(XBMCVkUI_Search_Base):
    def Search(self,query):
        result = None
        if query:
            self.AddSearchHistory(query, self.histId)
            result = self.transformResult(self.api.call(self.apiName,q=query, count="10"))
        if result:
            for a in result:
                self.ProcessFoundEntry(a)

    def transformResult(self, res):
        return res
