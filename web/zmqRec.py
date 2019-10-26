from time import sleep
import zmq
import base64
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)
socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
socket.connect("tcp://localhost:5555")
#socket.setsockopt(zmq.SUBSCRIBE, b'camera_frame')
sleep(2)
print('was here1')
received_count = 0
while True:
    received_count += 1
    # just receive the topic string and toss away
    frame = socket.recv_string()
    jpg_img = base64.b64decode(frame)
    if received_count % 10 == 0:
        print(f'total received frames: {received_count}')

