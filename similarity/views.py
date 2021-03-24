from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from similarity.camera import Youtube, WebCam

def index(request):
	return render(request, 'similarity/similarity.html')


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def webcam_feed(request):
	return StreamingHttpResponse(gen(WebCam()),
					content_type='multipart/x-mixed-replace; boundary=frame')


def youtube_feed(request):
	return StreamingHttpResponse(gen(Youtube()),
					content_type='multipart/x-mixed-replace; boundary=frame')