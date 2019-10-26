from flask import Flask, render_template, Response
import cv2
import time
import zmq
import numpy as np
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

class VideoCamera(object):
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        self.socket.setsockopt(zmq.CONFLATE, 1)
        self.socket.connect("tcp://localhost:5555")
    def get_frame(self):
        jpg_frame = self.socket.recv_string()
        jpg_image = base64.b64decode(jpg_frame)
        #image = self.socket.recv_pyobj()
        #success, image = self.video.read()
        #for i in range(0, 4):
        #    self.video.grab()
        #print('success', success)
        #ret, jpeg = cv2.imencode('.jpg', image)
        #return jpg_image.tobytes()
        return jpg_image

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame == None:
            print('noneFrame occurred')
        else:
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
