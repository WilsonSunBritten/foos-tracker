from time import sleep
import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b'camera_frame')
sleep(2)

received_count = 0
while True:
    received_count += 1
    # just receive the topic string and toss away
    socket.recv_string()
    frame = socket.recv_pyobj()
    if received_count % 10 == 0:
        print(f'total received frames: {received_count}')

