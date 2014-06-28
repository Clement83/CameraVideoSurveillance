import cv2.cv as cv
from datetime import datetime
import time

class MotionDetectorInstantaneous():
	def __init__(self,frame1, threshold=30,logger=None) :
		self.threshold = threshold
		self.logger = logger
		
		self.mem_storage = cv.CreateMemStorage(0)
		
		# The RunningAvg() function requires a 32-bit or 64-bit image...
		self.running_average_image = cv.CreateImage( cv.GetSize(frame1), cv.IPL_DEPTH_32F, 3 )
		# ...but the AbsDiff() function requires matching image depths:
		self.running_average_in_display_color_depth = cv.CloneImage(frame1)
		# The difference between the running average and the current frame:
		self.difference = cv.CloneImage( frame1 )
		self.grey_image = cv.CreateImage( cv.GetSize(frame1), cv.IPL_DEPTH_8U, 1 )
		
	
	def processImage(self,frame1,frame2) :
	
		# Create an image with interactive feedback:
		display_image = cv.CloneImage( frame2 )


		# Create a working "color image" to modify / blur
		color_image = cv.CloneImage( display_image )

		# Smooth to get rid of false positives
		cv.Smooth( color_image, color_image, cv.CV_GAUSSIAN, 19, 0 )

		# Use the Running Average as the static background			
		# a = 0.020 leaves artifacts lingering way too long.
		# a = 0.320 works well at 320x240, 15fps.  (1/a is roughly num frames.)
		cv.RunningAvg( color_image, self.running_average_image, 0.320, None )

		# Convert the scale of the moving average.
		cv.ConvertScale( self.running_average_image, self.running_average_in_display_color_depth, 1.0, 0.0 )

		# Subtract the current frame from the moving average.
		cv.AbsDiff( color_image, self.running_average_in_display_color_depth, self.difference )
		
		# Convert the image to greyscale.
		cv.CvtColor( self.difference, self.grey_image, cv.CV_RGB2GRAY )

		# Threshold the image to a black and white motion mask:
		cv.Threshold( self.grey_image, self.grey_image, 2, 255, cv.CV_THRESH_BINARY )
		# Smooth and threshold again to eliminate "sparkles"
		cv.Smooth( self.grey_image, self.grey_image, cv.CV_GAUSSIAN, 19, 0 )
		cv.Threshold( self.grey_image, self.grey_image, 240, 255, cv.CV_THRESH_BINARY )
		return self.grey_image
		
		
	def somethingHasMoved(self, frame1, frame2):
		if frame1 != None and frame2 != None :
			res = self.processImage(frame1, frame2)
			cv.SaveImage("res.JPG",res)
			contour = cv.FindContours( res, self.mem_storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE )
			nbContour = len(contour)
			if nbContour > self.threshold :
				self.logMessage("Detection : contour :" + str(nbContour))
				return True
			else : 
				self.logMessage("pas de detection : contour :" + str(nbContour))
		return False
	

		
	def logMessage(self,message) :
		#print message
		if not self.logger == None :
			self.logger.debug(message)