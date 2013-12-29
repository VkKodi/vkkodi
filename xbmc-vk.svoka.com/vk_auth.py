#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib

try:
    import json
except ImportError:
    import simplejson as json


def auth(email, password, client_id, secret, scope):
    url = urllib.urlopen("https://oauth.vk.com/token?grant_type=password&" +
                         "client_id=%s&client_secret=%s&username=%s&password=%s&scope=%s"
                         % (client_id, secret, email, password, scope))
    out = json.load(url)
    if "access_token" not in out:
        print out
    return out["access_token"]