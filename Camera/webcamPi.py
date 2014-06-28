#!/usr/bin/env python
# -*- coding: utf-8 -*-


from EventHook import EventHook
import ThreadCam

import picamera
import time


class webcamPi(): 

	def __init__(self,fps,nameImg,numeroCam):
		self.isRecording = False
		self.fps = fps
		self.nameImg = nameImg
		self.onNewImage=EventHook()
		self.numeroCam=numeroCam
		
		  

	def startRecord(self):
		# Wait for modprobe
		
		try :
			camera = picamera.PiCamera()
			time.sleep(2)
			
			camera.led = False		
			self.isRecording =True
			while self.isRecording:
				# Grab one frame from camera
				
				camera.capture(self.nameImg)
				self.onNewImage.fire()
				time.sleep( ( 1.0 / self.fps) )
		finally : 
			# self.onNewImage.clear()
			camera.close()
			print "stop recording"
			
	def stopRecord(self):
		#TODO proteger la variable !!
		self.isRecording =False
		
def GetInstance(fps,nameImg,numeroCam) :
	return webcamPi(fps,nameImg,numeroCam)