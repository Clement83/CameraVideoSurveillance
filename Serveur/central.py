#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import config 
import socket, sys, threading,time
from datetime import datetime, timedelta
import os
import cv2
import cv
from MotionDetector import MotionDetectorInstantaneous
import numpy as np
import logging
import logging.handlers
import urllib2


class ThreadCamera(threading.Thread):
	'''dérivation d'un objet thread pour gérer la connexion avec un client'''
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.connexion = conn
		self.lvlAlert = config.lvlAlert
		#0 eteint, 1 alumer
		self.etat = 0 
		self.numeroCam = "-1"
		self.dataImage = None
		self.image_tmoin1 = None
		self.image_t = None
		self.tabImageEvent = []
		self.tabImageEventHD = []
		LOG_FILENAME = 'c:/central/\logs/central.log'
		logging.basicConfig(filename=LOG_FILENAME, filemode='w', level=logging.DEBUG)
		#self.my_logger = logging.getLogger('centralLogger')
		
		handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000, backupCount=20)
		#self.my_logger.addHandler(handler)
		# create a logging format
		# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		# handler.setFormatter(formatter)

		#self.motionDetecteur = MotionDetectorInstantaneous(8,logging)
		self.motionDetecteur = None
	def run(self):
		# Dialogue avec le client :
		nom = self.getName()        # Chaque thread possède un nom
		dateDetection = None
		try :
			while 1:
				
				self.TraiterReception()

				#on svg les images ou on traite les ordres
				# if self.lvlAlert ==0 :
					#on envoi au frontaux cam éteinte
					# self.PrintMessage("alert 0")

				# if self.lvlAlert >0:
					#on envoi les demande au frontaux
					# self.PrintMessage("alert 1")

				if self.lvlAlert >1:
					#on fait la reconnaissance d'image et on traite les alertes
					# self.PrintMessage("alert 2")
					self.InsertImageEvent(self.image_t)
						
				if self.motionDetecteur  == None :
					self.motionDetecteur = MotionDetectorInstantaneous(self.image_t,150,logging)
					
				if self.motionDetecteur.somethingHasMoved(self.image_tmoin1,self.image_t) :
					dateDetection = datetime.now() + timedelta(0,7)
					self.PrintMessage("Detection mouvement sur la camera  : "+ str(self.numeroCam))
						
				if not dateDetection == None and dateDetection < datetime.now() :
					dateDetection = None
					self.PrintMessage("Ecriture de l'evenement detecté de la cam : "+ str(self.numeroCam))
					self.WriteImageEvent()
					if self.numeroCam in config.numCamAlert :
						urllib2.urlopen('http://yana.quintard.me/action.php?action=freeSms_sendSms&message=mouvement_sur_la_camera_'+str(self.numeroCam))
					
			
				self.image_tmoin1 = self.image_t
		
		except : 
			self.PrintMessage("Erreur de reception réinitialisation connexion " + str(sys.exc_info()) )
		finally :
			self.connexion.close()
			del conn_client[nom]
		
	def InsertImageEvent(self,image) : 
		if len(self.tabImageEvent) >= config.nbImageEvent : 
			self.tabImageEvent.pop(0)
		self.tabImageEvent.append(image)	
		
	def InsertImageEventHD(self,image) : 
		if len(self.tabImageEventHD) >= config.nbImageEvent : 
			self.tabImageEventHD.pop(0)
		self.tabImageEventHD.append(image)	
		
	def WriteImageEvent(self):
		for index in range(len(self.tabImageEvent)):
			totalPath = config.pathImgMove + str(self.numeroCam)
			if not os.path.exists(totalPath):
				os.makedirs(totalPath)
	
			cv.SaveImage( totalPath+"\\mv"+str(index)+".jpg",self.tabImageEvent[index])
		# ecriture des images hd
		strDateTime = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
		for index in range(len(self.tabImageEventHD)):
			directory = config.pathImgHd + str(self.numeroCam) +'/'+strDateTime
			if not os.path.exists(directory):
				os.makedirs(directory)
			pathImageHd = directory +'/serveurFile_'+str(index)+'.jpg'
			f = open( pathImageHd,'wb')
			f.write(self.tabImageEventHD[index]) # python will convert \n to os.linesep
			f.close() # you can omit in most cases as the destructor will call if
			# cv.SaveImage( totalPath+"\\mv"+str(index)+".jpg",self.tabImageEvent[index])

	
	def TraiterReception(self) :
			
			#numero traitement
			traitement = self.connexion.recv(4)
			traitement = self.bytes_to_number(traitement)
		
			#numero camera
			numCam = self.connexion.recv(4)
			numCam = self.bytes_to_number(numCam)
			# self.PrintMessage("Numero cam : " +str(numCam) + ". Traitement : " + str(traitement))
			if numCam < 999 :
				self.numeroCam  = numCam
				if traitement == 0 :
					# self.PrintMessage("Recuperation image")
					#taille image si il y a 	
					size = self.connexion.recv(4) # assuming that the size won't be bigger then 1GB
					size = self.bytes_to_number(size)
					# self.PrintMessage("taille image : " + str(size))
					
					current_size = 0
					imageReseau = ""
					while current_size < size:
						data = self.connexion.recv(1024)
						if not data:
							break
						#if len(data) + current_size > size:
						#	data = data[:size-current_size] # trim additional data
						imageReseau += data
						# you can stream here to disk
						current_size += len(data)
						#print "current size = " + str(current_size) + " !=  size = "+str(size)
					strDateTime = datetime.now().strftime('%y-%m-%d-%H-%M-%S')
					
					self.InsertImageEventHD(imageReseau)
					#convert image pour open cv
					# CV2
					nparr = np.fromstring(imageReseau, np.uint8)
					img_np = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
					img_np = cv2.resize(img_np, (0,0), fx=0.5, fy=0.5)
					# CV
					img_ipl = cv.CreateImageHeader((img_np.shape[1], img_np.shape[0]), cv.IPL_DEPTH_8U, 3)
					cv.SetData(img_ipl, img_np.tostring(), img_np.dtype.itemsize * 3 * img_np.shape[1])

					self.image_t = img_ipl
			
					try :
						#oriimage = cv2.imread(pathImageHd)
						#small = cv2.resize(oriimage, (0,0), fx=0.5, fy=0.5) 
						#cv2.imwrite(pathImageSd,small)
						
						cv.SaveImage( config.pathImgSd+str(numCam)+"\\last.jpg" ,self.image_t)
						#cv2.imwrite(config.pathImgSd+str(numCam)+"\\last.jpg",small)
					except : 
						msg = "erreur resize image : " + str(sys.exc_info())
						logging.error(msg)
						print msg
						
					# self.PrintMessage( "fin traitement image")
						
				elif traitement == 1 :
					self.PrintMessage("envoi de l'ordre a la bonne camera")
					#recuperation de l'ordre
					ordre =  self.connexion.recv(4)
					ordre = self.bytes_to_number(ordre)
					
					self.PrintMessage("envoi d'un ordre " + str(ordre) + " a la camera : " + str(numCam))
			else :
				raise Exception('Erreur camera', 'redemarage requis')
	def PrintMessage(self,message) :
		if config.isDebug : 
			msg = str(datetime.now()) + " | " +message
			logging.debug(msg)
			print msg
			
	def traitementCamera(self,data) :
		# self.PrintMessage("reception image")
		self.etat = data[4:7]
		self.dataImage = data[7:]
		self.numeroCam = data[1:4] 
		
		# self.PrintMessage( self.etat)
		# self.PrintMessage( self.dataImage)
		# self.PrintMessage( self.numeroCam)
	

	def bytes_to_number(self,b):
		b = map(ord, b)
		res = 0
		for i in range(4):
			res += b[i] << (i*8)
		return res
	
def SuppressionHistoriqueImage() :
	#return
	for dirpath, dirnames, filenames in os.walk(config.rootPathImages):
		for file in filenames:
			# print file
			curpath = os.path.join(dirpath, file)
			file_modified = datetime.fromtimestamp(os.path.getctime(curpath))
			# print str( file_modified) + str((datetime.now() - file_modified).days)
			if (datetime.now() - file_modified).days > 1:
				os.remove(curpath)
				print "suppression : " + curpath

def Repeater(delay, fun):
	def wrapper():
		while True:
			fun()
			
			t = time.localtime()
			t = time.mktime(t[:3] + (0,0,0) + t[6:])
			print "prochaine purge dans : " + str(t + 24*3600 - time.time()) + " secondes"
			time.sleep(t + 24*3600 - time.time())

	wrapper()
		
def functionThreadRepeater(delay, fun) :
	Repeater(delay, fun)
		
# Initialisation du serveur - Mise en place du socket :
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	mySocket.bind(('', config.port))
except socket.error:
	# logging.error("La liaison du socket à l'adresse choisie a échoué.")
	print "La liaison du socket à l'adresse choisie a échoué."
	sys.exit()
print "Serveur prêt, en attente de requêtes ..."
mySocket.listen(5)

# Attente et prise en charge des connexions demandées par les clients :
conn_client = {}                # dictionnaire des connexions clients


while 1:    
	time.sleep( ( 1.0) )
	try :
		connexion, adresse = mySocket.accept()
		#Créer un nouvel objet thread pour gérer la connexion :
		th = ThreadCamera(connexion)
		th.start()
		#Mémoriser la connexion dans le dictionnaire : 
		it = th.getName()        # identifiant du thread
		conn_client[it] = connexion
		print "Client %s connecté, adresse IP %s, port %s." %\
			   (it, adresse[0], adresse[1])
		#Dialogue avec le client :
		#connexion.send("Vous êtes connecté. Envoyez vos messages.")
	except :
		# logging.error("Erreur  init : " + str(sys.exc_info()))
		print "Erreur  init : "+ str(sys.exc_info())
		

