from django.shortcuts import render
from django.http.response import StreamingHttpResponse,HttpResponse
from similarity.camera import Youtube, WebCam
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import condition
import time
import json

def index(request):
	video=Youtube()
	return render(request, 'similarity/similarity.html',
		context={'video_address':video.get_url})

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_feed(request):
	return StreamingHttpResponse(gen(WebCam()),
					content_type='multipart/x-mixed-replace; boundary=frame')

@condition(etag_func=None)
def stream_response(request):
	video=Youtube()
	response = StreamingHttpResponse(video.get_pose(), status=200, content_type='text/event-stream')
	response['Cache-Control'] = 'no-cache'
	return response

#def get_stream(request):

