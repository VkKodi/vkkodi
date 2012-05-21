#!/bin/sh
if [ $# -eq 1 ]
then
	echo "Congrantulations!!! vk-xbmc.$1 released"
	cp gpl.txt xbmc-vk.svoka.com/
	zip -qr vk-xbmc.$1.zip xbmc-vk.svoka.com
	rm xbmc-vk.svoka.com/gpl.txt
else
	echo "no params given, creating test 00 release"
	zip -qr vk-xbmc.0.0.zip xbmc-vk.svoka.com
fi