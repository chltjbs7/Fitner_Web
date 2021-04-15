import cv2
#from vidgear.gears import CamGear
import pafy
from . import pose


class WebCam():
	def __init__(self):
		self.video = cv2.VideoCapture(0)

	def __del__(self):
		self.video.release()

	def get_frame(self):
		#success, image = self.video.read()

		#frame_flip = cv2.flip(image,1)
		#ret, jpeg = cv2.imencode('.jpg', frame_flip)
		get_pose=pose.pose(0)
		#return jpeg.tobytes()
		return get_pose.get_pose()

	#def get_pose(self):

class Youtube():
	def __init__(self):
		#self.url='https://www.youtube.com/watch?v=Waz8rfdvVsY'
		self.url='https://www.youtube.com/watch?v=e1DHt9wfQOA'
		self.video = pafy.new(self.url)
		self.best = self.video.getbest(preftype="mp4")

	#def __del__(self):
		#self.stream.release()

	def get_url(self):
		return self.best.url

	def get_pose(self):
		pose_obj=pose.pose(self.best.url)
		get_pose=pose_obj.get_pose()
		return get_pose
		



