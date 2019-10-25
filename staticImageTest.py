#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import cv2
from matplotlib import pyplot as plt


def main():
    img = cv2.imread('FoosPhotos/IMG_20191025_091516.jpg')
    output = img.copy()

    # converting from BGR to HSV color space

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

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

    #Find circles in image

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=30, param2=15, minRadius=40, maxRadius=70)

	# ensure at least some circles were found

    if circles is not None:
	# convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
 
	# loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
			# draw the circle in the output image, then draw a rectangle
			# corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    # Color correct for matplotlib
    RGB_img = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
    (plt.subplot(111), plt.imshow(RGB_img, cmap = 'gray'))
    (plt.title('Foos Image'), plt.xticks([]), plt.yticks([]))
    plt.show()

main()
