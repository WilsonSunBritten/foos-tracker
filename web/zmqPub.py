from time import sleep
import zmq
import cv2

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")
capture = cv2.VideoCapture(0)
sleep(2)

topic = 'camera_frame'
captured_count = 0
while True:
    captured_count += 1
    ret, frame = capture.read()
    socket.send_string(topic, zmq.SNDMORE)
    socket.send_pyobj(frame)
    if captured_count % 10 == 0:
        print(f'Have send {captured_count} frames')

