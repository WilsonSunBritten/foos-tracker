from flask import Flask, render_template, Response
import cv2
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()
    def get_frame(self):
        success, image = self.video.read()
        #for i in range(0, 4):
        #    self.video.grab()
        print('success', success)
        ret, jpeg = cv2.imencode('.jpg', image)
        print('ret', ret)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame == None:
            print('here')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
