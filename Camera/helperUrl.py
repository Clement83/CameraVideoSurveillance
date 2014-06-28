#!/usr/bin/env python
# -*- coding: utf-8 -*-

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib, urllib2, cookielib
  
class EnvoiSurSite(): 
	def __init__(self, urlcible = ''): 
		self.urlcible = urlcible 
	def envoi(self): 
		#"http://ks.quintard.me/videosurveillance//video.php"
		 
		opener = register_openers()
		opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

		params = {'camera_image': open("test.JPG", "rb"), 'token': 'azerty', 'camera_name' : 'port'}
		datagen, headers = multipart_encode(params)
		
		request = urllib2.Request(self.urlcible, datagen, headers)
		result = urllib2.urlopen(request) 
