#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cv2.cv as cv
import time
from EventHook import EventHook
import ThreadCam


class webcam(): 

	def __init__(self,fps,nameImg,numeroCam):
		self.isRecording = False
		self.fps = fps
		self.nameImg = nameImg
		self.onNewImage=EventHook()
		self.numeroCam=numeroCam
		
		  

	def startRecord(self):
		# Wait for modprobe
		time.sleep(2)

		capture = cv.CaptureFromCAM(self.numeroCam)

		text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
		text_coord = ( 5, 15 )
		text_color = cv.CV_RGB(255,255,255)
		self.isRecording =True
		try :
			while self.isRecording:
				# Grab one frame from camera
				frame = cv.QueryFrame(capture)
				
				
				cv.PutText( frame,"PORT : "+ time.strftime('%d/%m/%y %H:%M',time.localtime()), text_coord, text_font, text_color )
			
				cv.SaveImage(self.nameImg,frame)
				self.onNewImage.fire()
			
				time.sleep( ( 1.0 / self.fps) )
		finally : 
			# self.onNewImage.clear()
			print "stop recording"
			
	def stopRecord(self):
		#TODO proteger la variable !!
		self.isRecording =False
		
		
		
def GetInstance(fps,nameImg,numeroCam) :
	return webcam(fps,nameImg,numeroCam)