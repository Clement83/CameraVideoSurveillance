#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, sys, threading
from sys import stdin
import time

from config import config
from ThreadCam import *

cameraModule = __import__(config.typeCam) 


class CameraCore():
	
	def __init__(self):
		print config.typeCam
		# if config.typeCam == 0:
			# self.camera = webcam(config.fps,config.nomImage,config.numcam)
		# elif config.typeCam == 1:
			# sinon on instancira une cam rasperry pi
			# self.camera = webcamPi(config.fps,config.nomImage,config.numcam)
		
		self.camera = cameraModule.GetInstance(config.fps,config.nomImage,config.numcam)
		self.camera.onNewImage += self.EnoiSurServeur
		self.connected = False
		self.cnx = None
		self.th_R = None;
		self.th_E = None;
		
		
	def StartCore(self):
		self.connected = False
		while True:
			try :
				if not self.connected :
					self.TryConnect() 
					self.EcouteCommande()
					self.StartCamera()
					self.connected=False
					self.StopCamera()
					print "Redemarage boucle"
				time.sleep(1)
				
			except :
				self.connected = False
				print "Erreur sur le demarage du core" + str(sys.exc_info()[0])
				print "nouvelle tentative de connexion"
				
				if self.th_R is not None :
					self.th_R._Thread__stop()
					self.th_R = None
				if self.th_E is not None :
					self.th_E._Thread__stop()
					self.th_E = None
				
				if self.cnx is not None :
					self.cnx.close()
				time.sleep(10)

			
	def TryConnect(self):
		notConnect = True
		self.cnx= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		while notConnect :
			try:
				self.cnx.connect((config.ip, config.port))
				notConnect = False
				print "connexion central OK"
			except :
				print  "La connexion a échoué." + str(sys.exc_info()[0])
				
				notConnect = True
				time.sleep(10.0)
			
	
		#TODO thread a supprimer classe a refactorer
		self.th_E = ThreadEmission(self.cnx)
		self.th_E.onError += self.ErrorInThread
	
	def EcouteCommande(self):
		print "TODO traiter reception cmd"
	

	def EnoiSurServeur(self):
		#envoi une image au central
		self.th_E.run() 
		
	def ExecuteCmd(self, numeroCmd):
		#executela commande
		if numeroCmd == 1:
			self.StartCamera()
		elif  numeroCmd == 2:
			self.StopCamera()
		
	def StartCamera(self):
		#demare la camera
		#initialisation et boucle infini
		#a = threading.Thread(None, self.camera.startRecord, None) 
		#a.start()
		self.camera.startRecord()
		
	def StopCamera(self):
		#arrete la cam
		if self.camera is not None :
			self.camera.stopRecord()
	
	def ErrorInThread(self):
		self.connected = False
		self.StopCamera()
		if self.th_R is not None :
			self.th_R._Thread__stop()
			self.th_R.onError.clear()
			self.th_R = None
		if self.th_E is not None :
			self.th_E._Thread__stop()
			self.th_E.onError.clear()
			self.th_E = None
		if self.cnx is not None :
			self.cnx.close()
			self.cnx=None

if __name__=="__main__":
	app = CameraCore()
	app.StartCore()
