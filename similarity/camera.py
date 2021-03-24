import cv2
from vidgear.gears import CamGear

class WebCam(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)

	def __del__(self):
		self.video.release()

	def get_frame(self):
		success, image = self.video.read()
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.
		frame_flip = cv2.flip(image,1)
		ret, jpeg = cv2.imencode('.jpg', frame_flip)
		return jpeg.tobytes()


class Youtube(object):
	def __init__(self):
		self.stream = CamGear(source='https://www.youtube.com/watch?v=1W9gMxLoW6Q',time_delay=1, logging=True,stream_mode=True).start()

	def __del__(self):
		self.stream.release()

	def get_frame(self):
		image = self.stream.read()
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.

		ret, jpeg = cv2.imencode('.jpg', image)
		return jpeg.tobytes()
