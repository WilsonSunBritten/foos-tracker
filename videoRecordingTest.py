import numpy as np
import cv2
import time
import math
from datetime import date, datetime, timedelta

start_time = time.time()
frame_rate = 30
frame_gap = timedelta(seconds = 1 / frame_rate)

# unit = inch
pixels_per_unit = 10
units_per_pixel = 1 / pixels_per_unit
mph_to_pps = 5280 * 12 * pixels_per_unit / 3600

def main():
    frameCount = 0
    circleCount = 0
    X = []
    Y = []
    T = []
    v = 0
    V = np.array([])
    cap = cv2.VideoCapture(0)

    while(True and cap is not None):
        # Capture frame-by-frame
        _, frame = cap.read()
        try:
            output = frame.copy()
            frameCount = frameCount + 1
        except:
            print("Reached end of video stream.")    
            break
    
        processedImage = preProcessImage(frame)

        circle0 = findBall(processedImage, output, circleCount)

        # as frames come in, define x, y, t (ball loc and datetime)

        if circle0 is not None:
            x = circle0[0]
            y = circle0[1]
            t = frameCount * frame_gap
            X.append(x)
            Y.append(y)
            T.append(t)

            if len(X) > 1:
                delta_x = X[-1] - X[-2]
                delta_y = Y[-1] - Y[-2]
                delta_t = T[-1] - T[-2]
                delta_p = math.sqrt(delta_x ** 2 + delta_y ** 2)
                v = delta_p / delta_t.total_seconds() / mph_to_pps
                print((x, y, t))
                print(v)
                V = np.append(V, v)
                # avg_v_mpg is average velocity averaged over last 3 periods...not sure if we want this.  Depends on how many missed frames
                # avg_v_mpg = np.mean(V[-3:])

        cv2.putText(output, "{0:.2f}".format(v), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # Color correct for matplotlib
        #RGB_img = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

        cv2.imshow('frame',output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # (plt.subplot(111), plt.imshow(RGB_img, cmap = 'gray'))
        # (plt.title('Foos Image'), plt.xticks([]), plt.yticks([]))
        # plt.show()
    print("Frame Count: ", frameCount)    
    print("Circle Count: ", circleCount)
    print("Detection Ratio: ", circleCount/frameCount)
    cap.release()
    cv2.destroyAllWindows()


# Find a balls coordinates on the image.

def findBall(processedImage, output, circleCount):
     #Find circles in image
    
    #circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=40, maxRadius=70)
    #circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=20, maxRadius=30)   #Detectio Ratio = 0.46184738955823296  # Time: 23.78104305267334 seconds
    #circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=20, maxRadius=30)   #Detectio Ratio = 0.46586345381526106
    #circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=20, maxRadius=25)   #Detectio Ratio = 0.24899598393574296 #Time: 23.295908212661743s
    #circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=18, maxRadius=30)    #Detectio Ratio = 0.5742971887550201  # Time: 22.467453956604004 seconds
    #circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=18, maxRadius=35)    #Detectio Ratio = 0.5903614457831325  # Time: 22.175649642944336 seconds
    circles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=19, maxRadius=35)    #Detectio Ratio = 0.5903614457831325  # Time: 22.175649642944336 seconds
    # print(circles)
    # ensure at least some circles were found

    if circles is not None:
        circleCount = circleCount + 1
    # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
    # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        return circles[0]
    else:
        return None

# Preprocess image, convert to HSV and threshold out red.

def preProcessImage(frame):
    # converting from BGR to HSV color space
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Range for lower red
    
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    
    # Range for upper range
    
    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)
    
    # Generating the final mask to detect red color
    mask1 = mask1 + mask2
    blurred = cv2.GaussianBlur(mask1, (5, 5), 0)
    return blurred

main()
print("--- %s seconds ---" % (time.time() - start_time))
