#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib

try:
    import json
except ImportError:
    import simplejson as json


def auth(email, password, client_id, secret,scope,code):
    if code == "0":
        try:
            url = urllib.urlopen("https://oauth.vk.com/token?" + urllib.urlencode({
                    "grant_type": "password",
                    "client_id": client_id,
                    "client_secret": secret,
                    "username": email,
                    "password": password,
                    "scope": scope,
                    "2fa_supported": "1"
                }))

            out = json.load(url)

        except IOError as e:
            print(e.message)
            print("===VK 2FA Code requested===")
            return "-1"
    else:
        url = urllib.urlopen("https://oauth.vk.com/token?" + urllib.urlencode({
                    "grant_type": "password",
                    "client_id": client_id,
                    "client_secret": secret,
                    "username": email,
                    "password": password,
                    "scope": scope,
                    "2fa_supported": "1",
                    "code": code
                }))

        out = json.load(url)

    if "access_token" not in out:
        print out
    return out["access_token"]
