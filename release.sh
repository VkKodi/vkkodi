#!/bin/sh
if [ $# -eq 1 ]
then
	echo "Congrantulations!!! vk-xbmc.$1 released"
	zip -qr vk-xbmc.$1.zip xbmc-vk.svoka.com
else
	echo "no params given, creating test 00 release"
	zip -qr vk-xbmc.0.0.zip xbmc-vk.svoka.com
fi