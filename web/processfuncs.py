import numpy as np
import cv2
import time
import math
import zmq
import base64

# unit = inch TODO recalc for table
pixels_per_unit = 10
units_per_pixel = 1 / pixels_per_unit
mph_to_pps = 5280 * 12 * pixels_per_unit / 3600

def maskImage(frame):
    #converting from BGR to HSV color space
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(frame, lower_red, upper_red)

    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask = mask + cv2.inRange(frame, lower_red, upper_red)

    #  blur
    return cv2.GaussianBlur(mask, (5, 5), 0)

def findBall(processedImage):
    circles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=19, maxRadius=35)

    if circles is not None:
        # convert the (x, y) coordinates and radius of circles to ints
        circles = np.round(circles[0, :]).astype("int")
        # TODO line above only bother doing for the first circle
        return circles[0]
    else:
        return None

class VelocityTracker:
    def __init__(self):
        self.prev_x = None
        self.prev_y = None
        self.prev_t = None
        self.prev_v = None
        self.prev_prev_v = None
    def get_velocity(self, circle, time):
        if self.prev_x is None:
            self.prev_x = circle[0]
            self.prev_y = circle[1]
            self.prev_t = time
            return None
        else:
            x = circle[0]
            y = circle[1]
            delta_x = x - self.prev_x
            delta_y = y - self.prev_y
            delta_t = time - self.prev_t
            delta_p = math.sqrt(delta_x ** 2 + delta_y ** 2)
            v = delta_p / delta_t / mph_to_pps
            if self.prev_prev_v is not None:
                return_val = np.mean((self.prev_prev_v, self.prev_v, v))
            elif self.prev_v is not None:
                return_val = np.mean((self.prev_v, v))
            else:
                return_val = v
            self.prev_prev_v = self.prev_v
            self.prev_v = v
            self.prev_x = x
            self.prev_y = y
            self.prev_t = time
            return v

def frame_generator():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.CONFLATE, 1)
    socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
    socket.connect("tcp://localhost:5555")
    while True:
        jpg_frame = socket.recv_string()
        jpg_image = base64.b64decode(jpg_frame)
        npimg = np.fromstring(jpg_image, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        yield source

def tracked_frame_generator():
    velocity_tracker = VelocityTracker()
    for frame in frame_generator():
        mask = maskImage(frame)
        ball = findBall(mask)
        if ball is None:
            yield frame
            continue
        velocity = velocity_tracker.get_velocity(ball, time.time())
        # apply layers to image to show ball/tet
        cv2.circle(frame, (ball[0], ball[1]), ball[2], (0, 255, 0), 4)
        if velocity is not None:
            cv2.putText(frame, "{0:.2f}".format(velocity), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        yield frame

