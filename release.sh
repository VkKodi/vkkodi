#!/bin/sh
rm -f xbmc-vk.svoka.com.zip
find xbmc-vk.svoka.com -name "*.pyc" | xargs -I {} rm -v "{}"
find xbmc-vk.svoka.com -name "*.pyo" | xargs -I {} rm -v "{}"
find xbmc-vk.svoka.com -name ".DS_Store" | xargs -I {} rm -rfv "{}"
find xbmc-vk.svoka.com -name ".idea" | xargs -I {} rm -rfv "{}"

zip -qr xbmc-vk.svoka.com.zip xbmc-vk.svoka.com
