from time import sleep
import zmq
import cv2
import base64
from queue import Queue
from threading import Thread

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")
sleep(2)

class FileVideoStream:
    def __init__(self, queueSize=32):
        self.stream = cv2.VideoCapture(0)
        self.queue = Queue(maxsize=queueSize)
    def start(self):
        thread = Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()
        return self
    def update(self):
        while True:
            if not self.queue.full():
                _, frame = self.stream.read()
                self.queue.put(frame)
    def read(self):
        return self.queue.get()
    def more(self):
        return self.queue.qsize() > 0

# start streaming video feed into queue
fvs = FileVideoStream().start()
topic = 'camera_frame'
captured_count = 0
while True:
    if not fvs.more():
        continue
    captured_count += 1
    frame = fvs.read()
    _, buffer = cv2.imencode('.jpg', frame)
    socket.send(base64.b64encode(buffer))
    if captured_count % 10 == 0:
        print(f'Have send {captured_count} frames')

