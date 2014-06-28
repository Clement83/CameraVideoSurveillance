#!/usr/bin/env python

# See also: http://sundararajana.blogspot.com/2007/05/motion-detection-using-opencv.html

import cv
import time
import pygame
#~ from scipy import *
#~ from scipy.cluster import vq
import numpy
import sys, os, random, hashlib

import helperMail
from helperMail import *

from math import *

pygame.mixer.init()

class Target:
	def __init__(self):
		
		self.isAffichageServeur = False
		self.liste = ['Turret_turret_active_2_fr.wav', 'Turret_turret_active_7_fr.wav', 'Turret_turret_active_8_fr.wav', 'Turret_turret_autosearch_5_fr.wav', 'Turret_turret_disabled_8_fr.wav', 'Turret_turret_pickup_6_fr.wav']
		
		if len( sys.argv ) > 1:
			self.writer = None
			self.capture = cv.CaptureFromFile( sys.argv[1] )
			frame = cv.QueryFrame(self.capture)
			frame_size = cv.GetSize(frame)
		else:
			fps=15
			is_color = True

			self.capture = cv.CaptureFromCAM(0)
			#cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640 );
			#cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480 );
			cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 320 );
			cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 240 );
			frame = cv.QueryFrame(self.capture)
			frame_size = cv.GetSize(frame)

			self.writer = None
			#self.writer = cv.CreateVideoWriter("/dev/shm/test1.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, frame_size, is_color )
			#self.writer = cv.CreateVideoWriter("test2.mpg", cv.CV_FOURCC('P', 'I', 'M', '1'), fps, frame_size, is_color )
			#self.writer = cv.CreateVideoWriter("test3.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, cv.GetSize(frame), is_color )
			#self.writer = cv.CreateVideoWriter("test4.mpg", cv.CV_FOURCC('P', 'I', 'M', '1'), fps, (320, 240), is_color )

			# These both gave no error message, but saved no file:
			###self.writer = cv.CreateVideoWriter("test5.h263i", cv.CV_FOURCC('I', '2', '6', '3'), fps, cv.GetSize(frame), is_color )
			###self.writer = cv.CreateVideoWriter("test6.fli",   cv.CV_FOURCC('F', 'L', 'V', '1'), fps, cv.GetSize(frame), is_color )
			# Can't play this one:
			###self.writer = cv.CreateVideoWriter("test7.mp4",   cv.CV_FOURCC('D', 'I', 'V', '3'), fps, cv.GetSize(frame), is_color )

		# 320x240 15fpx in DIVX is about 4 gigs per day.
		
		frame = cv.QueryFrame(self.capture)
		if self.isAffichageServeur:
			cv.NamedWindow("Target", 1)
			#cv.NamedWindow("Target2", 1)

	def mailAlert(self):
		# Identification du serveur SMTP a utiliser (vous mettez le votre!)
		# si pas d authentification: ne pas indiquer les 2 derniers parametres
		# 25 est le port par defaut
		serveur = ServeurSMTP("quintard.me", 25)
		 
		# adresse de l expediteur (vous!): c'est une chaine de caracteres 
		exped = "moi <clement@quintard.me>"
		 
		# adresse du ou des destinataire(s) direct(s): c'est une liste de chaine comportant au moins une adresse (sinon=erreur)
		to = ["clement@quintard.me"]
		 
		# adresse du ou des destinataire(s) en copie: c'est une liste de chaines, eventuellement vide
		cc = []
		 
		# adresse du ou des destinataire(s) en copie cachee: c'est une liste de chaines, eventuellement vide
		bcc = []
		 
		# sujet du mail (monolignes). Avec un encodage le permettant (ISO-8859-1, UTF-8), le sujet peut avoir des caracteres accentues
		sujet = "Mouvement detecter"
		 
		# corps du mail (en general multilignes). Avec un encodage le permettant (ISO-8859-1, UTF-8), le sujet peut avoir des caracteres accentues
		corps = """
		ALERT INTRUSION
		"""
		 
		# pieces jointes eventuelles (ici, [])
		pjointes=["test.JPG"]
		 
		# choix du codage: 'US-ASCII', 'ISO-8859-1', 'ISO-8859-15', 'UTF-8', None (None=application du codage par defaut)
		# rappel: ISO-8859-15 permet, en plus de l'ISO-8859-1, l'utilisation du sigle de l'Euro 
		codage = 'ISO-8859-15'
		 
		# type de texte: 'plain', 'html', ... Ici, c'est 'plain'
		typetexte = 'plain'
		 
		# creation du mail correctement formate (en-tete + corps) et encode
		try:
			message = MessageSMTP(exped, to, cc, bcc, sujet, corps, pjointes, codage, typetexte)
		except:
			print u"%s" % sys.exc_info()[1]
			sys.exit()
		 
		# envoi du mail et affichage du resultat
		rep = envoieSMTP(message, serveur)
		print rep
	
	
	def jouerSon(self):
		
		#TODO mettre son alleatoire
		monson = pygame.mixer.music.load(self.liste[0])
		monson.play()
		
	
	
	
	def run(self):
		# Initialize
		#log_file_name = "tracker_output.log"
		#log_file = file( log_file_name, 'a' )

		frame = cv.QueryFrame( self.capture )
		frame_size = cv.GetSize( frame )

		# Capture the first frame from webcam for image properties
		display_image = cv.QueryFrame( self.capture )

		# Greyscale image, thresholded to create the motion mask:
		grey_image = cv.CreateImage( cv.GetSize(frame), cv.IPL_DEPTH_8U, 1 )

		# The RunningAvg() function requires a 32-bit or 64-bit image...
		running_average_image = cv.CreateImage( cv.GetSize(frame), cv.IPL_DEPTH_32F, 3 )
		# ...but the AbsDiff() function requires matching image depths:
		running_average_in_display_color_depth = cv.CloneImage( display_image )

		# RAM used by FindContours():
		mem_storage = cv.CreateMemStorage(0)

		# The difference between the running average and the current frame:
		difference = cv.CloneImage( display_image )

		target_count = 1
		last_target_count = 1
		last_target_change_t = 0.0
		k_or_guess = 1
		codebook=[]
		frame_count=0
		last_frame_entity_list = []

		t0 = time.time()

		# For toggling display:
		image_list = [ "camera", "difference", "threshold", "display"]
		image_index = 0   # Index into image_list


		# Prep for text drawing:
		text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
		text_coord = ( 5, 15 )
		text_color = cv.CV_RGB(255,255,255)

		###############################
		### Face detection stuff
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_default.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_alt.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_alt2.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_mcs_mouth.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_eye.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_alt_tree.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_upperbody.xml' )
		#haar_cascade = cv.Load( 'haarcascades/haarcascade_profileface.xml' )

		# Set this to the max number of targets to look for (passed to k-means):
		max_targets = 3
		
		lastDetection = time.time()

		while True:

			# Capture frame from webcam
			camera_image = cv.QueryFrame( self.capture )

			frame_count += 1
			frame_t0 = time.time()

			# Create an image with interactive feedback:
			display_image = cv.CloneImage( camera_image )

			# Create a working "color image" to modify / blur
			color_image = cv.CloneImage( display_image )

			# Smooth to get rid of false positives
			cv.Smooth( color_image, color_image, cv.CV_GAUSSIAN, 19, 0 )

			# Use the Running Average as the static background			
			# a = 0.020 leaves artifacts lingering way too long.
			# a = 0.320 works well at 320x240, 15fps.  (1/a is roughly num frames.)
			cv.RunningAvg( color_image, running_average_image, 0.320, None )

			# Convert the scale of the moving average.
			cv.ConvertScale( running_average_image, running_average_in_display_color_depth, 1.0, 0.0 )

			# Subtract the current frame from the moving average.
			cv.AbsDiff( color_image, running_average_in_display_color_depth, difference )

			# Convert the image to greyscale.
			cv.CvtColor( difference, grey_image, cv.CV_RGB2GRAY )

			# Threshold the image to a black and white motion mask:
			cv.Threshold( grey_image, grey_image, 2, 255, cv.CV_THRESH_BINARY )
			# Smooth and threshold again to eliminate "sparkles"
			cv.Smooth( grey_image, grey_image, cv.CV_GAUSSIAN, 19, 0 )
			cv.Threshold( grey_image, grey_image, 240, 255, cv.CV_THRESH_BINARY )

			#~ grey_image_as_array = numpy.asarray( cv.GetMat( grey_image ) )
			#~ non_black_coords_array = numpy.where( grey_image_as_array > 3 )
			#~ # Convert from numpy.where()'s two separate lists to one list of (x, y) tuples:
			#~ non_black_coords_array = zip( non_black_coords_array[1], non_black_coords_array[0] )


			# Now calculate movements using the white pixels as "motion" data
			contour = cv.FindContours( grey_image, mem_storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE )

			print len(contour)
			if len(contour) > 30 and time.time()-lastDetection>2:
				print "move"
				lastDetection = time.time()
				cv.PutText( camera_image, time.strftime('%d/%m/%y %H:%M',time.localtime()), text_coord, text_font, text_color )
			
				cv.SaveImage("test.JPG",camera_image)
				
				self.mailAlert()
		

			#print "min_size is: " + str(min_size)
			# Listen for ESC or ENTER key
			c = cv.WaitKey(7) % 0x100
			if c == 27 or c == 10:
				break
			
			if self.isAffichageServeur:
				image = camera_image
				cv.PutText( image, "Camera (Normal)", text_coord, text_font, text_color )
				cv.ShowImage( "Target", image )


			#~ frame_t1 = time.time()
			#~ delta_t = frame_t1 - frame_t0
			#~ if delta_t < ( 1.0 / 15.0 ): time.sleep( ( 1.0 / 15.0 ) - delta_t )
			#il faut laisser le temps au rasberry de s'en remettre
			time.sleep( ( 1.0 / 15.0 ) )


		t1 = time.time()
		time_delta = t1 - t0
		processed_fps = float( frame_count ) / time_delta
		print "Got %d frames. %.1f s. %f fps." % ( frame_count, time_delta, processed_fps )

if __name__=="__main__":
	t = Target()
#	import cProfile
#	cProfile.run( 't.run()' )
	#t.run()
	t.jouerSon()





