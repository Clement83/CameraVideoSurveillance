#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Définition d'un client réseau gérant en parallèle l'émission
# et la réception des messages (utilisation de 2 THREADS).

host = '127.0.0.1'
port = 1234

import socket, sys, threading
class ThreadReception(threading.Thread):
	"""objet thread gérant la réception des messages"""
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.connexion = conn           # réf. du socket de connexion
		
	def run(self):
		while 1:
			message_recu = self.connexion.recv(1024)
			print "*" + message_recu + "*"
			if message_recu =='' or message_recu.upper() == "FIN":
				break
		# Le thread <réception> se termine ici.
		# On force la fermeture du thread <émission> :
		th_E._Thread__stop()
		print "Client arrêté. Connexion interrompue."
		self.connexion.close()
	
class ThreadEmission(threading.Thread):
	"""objet thread gérant l'émission des messages"""
	def __init__(self, conn):
		threading.Thread.__init__(self)
		self.connexion = conn           # réf. du socket de connexion
			
	def run(self):
		while 1:
			message_emis = raw_input()			
			traitement = 1
			#self.connexion.send(self.convert_to_bytes(traitement))
			self.connexion.send(self.convert_to_bytes(traitement))
			emeteur = 1000
			self.connexion.send(self.convert_to_bytes(emeteur))

			messageAenvoyer = 1
			if message_emis == "0":
				messageAenvoyer = 0

			self.connexion.send(self.convert_to_bytes(messageAenvoyer))

	def convert_to_bytes(self,no):
		result = bytearray()
		result.append(no & 255)
		for i in range(3):
			no = no >> 8
			result.append(no & 255)
		return result


# Programme principal - Établissement de la connexion :
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	connexion.connect((host, port))
except socket.error:
	print "La connexion a échoué."
	sys.exit()    
print "Connexion établie avec le serveur."
			
# Dialogue avec le serveur : on lance deux threads pour gérer
# indépendamment l'émission et la réception des messages :
th_E = ThreadEmission(connexion)
th_R = ThreadReception(connexion)
th_E.start()
th_R.start()        
