import os
import threading
import cv2

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.conf.urls.static import static


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.count = 0
        (self.grabbed, self.frame) = self.video.read()
        cv2.imwrite(f"temp/{self.count}.jpg", self.frame)
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode(".jpg", image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()
            self.count += 1
            cv2.imwrite(f"temp/{self.count}.jpg", self.frame)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


def realtime(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(
            gen(cam), content_type="multipart/x-mixed-replace;boundary=frame"
        )
    except Exception as e:  # This is bad! replace it with proper handling
        print(f"[ERROR]: {e}")
