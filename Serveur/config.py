#!/usr/bin/env python
# -*- coding: utf-8 -*-

class config :
	#Port serveur central
	port=1234
	#niveau d'alert par default (0 => cam eteinte, 1 cam alumer pas d'envoi de mail, pas de detection, 2 tous peux arrivé!!)
	lvlAlert=2
	#chemin vers le repertoir des image hd
	pathImgHd="C:\\central\\images\\svgMoveHd\\"
	#chemin vers le repertoir des image sd
	pathImgSd="C:\\website\\videoSurveillance\\camera\\"
	#chemin vers le repertoir des image sd
	pathImgMove="C:\\website\\videoSurveillance\\events\\"
	#root path image
	rootPathImages = "C:\\central\\images"
	#varible de debug
	isDebug = True
	#heure a laquel la purge doit etre executer
	heurePurge = 23
	#nb image garder pour un evenement
	nbImageEvent = 40
	#numero des Cameras qui declanche un envoi sms
	numCamAlert = [2,3];