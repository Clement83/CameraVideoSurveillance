#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import config
from EventHook import EventHook
import socket, sys, threading
import os

class ThreadReception(threading.Thread):
	"""objet thread gérant la réception des messages"""
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.connexion = conn           # réf. du socket de connexion
		self.onNewMessage=EventHook()
		self.onError = EventHook()
		
	def run(self):
		try :
			while 1:
				message_recu = self.connexion.recv(1024)
				print "*" + message_recu + "*"
				self.onNewMessage.fire(self.bytes_to_number(message_recu))
		except : 

			print "Client arrêté. Connexion interrompue."

			self.onError.fire()
		
	
	def bytes_to_number(self,b):
		# if Python2.x
		b = map(ord, b)
		res = 0
		for i in range(4):
			res += b[i] << (i*8)
		return res
	
class ThreadEmission(threading.Thread):
	"""objet thread gérant l'émission des messages"""
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.connexion = conn           # réf. du socket de connexion
		self.onError = EventHook()
			
	def run(self):
		
		try :			
			#length = os.path.getsize(config.nomImage)
			#self.connexion.send(self.convert_to_bytes(length))
			if os.path.exists(config.nomImage):
				traitement = 0
				self.connexion.send(self.convert_to_bytes(traitement))
				emeteur = config.identifiantCam
				self.connexion.send(self.convert_to_bytes(emeteur))
				length = os.path.getsize(config.nomImage)
				self.connexion.send(self.convert_to_bytes(length))

				reply = open(config.nomImage, 'rb').read()
				self.connexion.sendall(reply)
				#self.onError.clear()
		except : 
			print "Erreur dans l envoi du fichier" + str(sys.exc_info()[0])
			
			self.onError.fire()

	def convert_to_bytes(self,no):
		result = bytearray()
		result.append(no & 255)
		for i in range(3):
			no = no >> 8
			result.append(no & 255)
		return result



# Programme principal - Établissement de la connexion :
#connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#try:
#	connexion.connect((host, port))
#except socket.error:
#	print "La connexion a échoué."
#	sys.exit()    
#print "Connexion établie avec le serveur."
			
# Dialogue avec le serveur : on lance deux threads pour gérer
# indépendamment l'émission et la réception des messages :
#th_E = ThreadEmission(connexion)
#th_R = ThreadReception(connexion)
#th_E.start()
#th_R.start()        
