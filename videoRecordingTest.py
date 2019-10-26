import numpy as np
import cv2
from matplotlib import pyplot as plt
import time


start_time = time.time()

def main():
    frameCount = 0
    circleCount = 0
    cap = cv2.VideoCapture('FoosVideos/video1.mp4')

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

        findBall(processedImage, output, circleCount)

    
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
    print(circles)
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
