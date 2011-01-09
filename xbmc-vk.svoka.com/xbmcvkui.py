__author__ = 'Shchvova'

import xbmcplugin, urllib, sys

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
        __dict_params.update(parameters)
        return sys.argv[0] + "?" + urllib.urlencode(__dict_params)
