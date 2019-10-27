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

def distance_to_line( point, line_points):
    (l1x, l1y) = line_points[0]
    (l2x, l2y) = line_points[1]
    (x,y,_) = point
    dx = l2x - l1x
    dy = l2y - l1y
    dr2 = float(dx **2 + dy **2)
    lerp = ((x - l1x) * dx + (y - l1y) * dy) / dr2
    if lerp < 0:
        lerp = 0
    elif lerp > 1:
        lerp = 1
    newx = lerp * dx + l1x
    newy = lerp * dy + l1y
    _dx = newx - x
    _dy = newy - y
    return math.sqrt(_dx ** 2 + _dy ** 2)


class GoalTracker():
    def __init__(self, black_goal=((0,100), (0, 200)), yellow_goal=((480, 100), (460, 200))):
        self.black_goals = 0
        self.yellow_goals = 0
        self.last_goal = None
        self.goal_time = None
        self.black_goal = black_goal
        self.yellow_goal = yellow_goal
        self.last_ball_position = None
        self.goal_length = 3
        self.goal_distance_threshold = 100
        self.missed_frames_until_goal = 8
        self.current_missed_frames = 0
    def detect_goal(self, circle, time):
        if self.goal_time is not None:
            if time - self.goal_time < self.goal_length:
                return (self.last_goal, self.black_goals, self.yellow_goals)
            else:
                self.goal_time = None
                self.last_goal = None
        if circle is not None:
            self.last_ball_position = circle
            self.current_missed_frames = 0
            return (self.last_goal, self.black_goals, self.yellow_goals)
        self.current_missed_frames += 1
        if self.last_ball_position is not None and self.current_missed_frames > self.missed_frames_until_goal:
            last_known_distance_black = distance_to_line(self.last_ball_position, self.black_goal)
            if last_known_distance_black < self.goal_distance_threshold:
                self.last_goal = 'BLACK'
                self.goal_time = time
                self.last_ball_position = None
                self.black_goals += 1
                return (self.last_goal, self.black_goals, self.yellow_goals)
            last_known_distance_yellow = distance_to_line(self.last_ball_position, self.yellow_goal)
            if last_known_distance_yellow < self.goal_distance_threshold:
                self.last_goal = 'YELLOW'
                self.goal_time = time
                self.last_ball_position = None
                self.yellow_goals += 1
                return (self.last_goal, self.black_goals, self.yellow_goals)
        return (self.last_goal, self.black_goals, self.yellow_goals)

def tracked_frame_generator():
    velocity_tracker = VelocityTracker()
    frame_count = 0
    start = time.time()
    black_goal=((2,150), (2, 350))
    yellow_goal=((638, 150), (638, 350))
    goal_tracker = GoalTracker(black_goal=black_goal, yellow_goal=yellow_goal)
    for frame in frame_generator():
        now = time.time()
        time_diff = now - start
        cv2.putText(frame, "{0:.2f} FPS".format(frame_count / time_diff), (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # draw black goal
        cv2.line(frame, black_goal[0], black_goal[1], (0, 0, 0), 3)
        # draw yellow goal
        cv2.line(frame, yellow_goal[0], yellow_goal[1], (0, 255, 255), 3)

        # reset fps calc every 5 min... why not
        if time_diff > 300:
            frame_count = 0
            start = now
        frame_count += 1
        mask = maskImage(frame)
        ball = findBall(mask)
        (current_goal, black_goals, yellow_goals) = goal_tracker.detect_goal(ball, now)
        #black score
        cv2.putText(frame, f'{black_goals}', (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        #yellow score
        cv2.putText(frame, f'{yellow_goals}', (600, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (124, 255, 255), 2)
        #recent score
        if current_goal:
            cv2.putText(frame, f'{current_goal} GOAL', (180, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 6)

        if ball is None:
            yield frame
            continue
        velocity = velocity_tracker.get_velocity(ball, now)
        # apply layers to image to show ball/tet
        cv2.circle(frame, (ball[0], ball[1]), ball[2], (0, 255, 0), 4)
        if velocity is not None:
            cv2.putText(frame, "V:{0:.2f}".format(velocity), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        yield frame

