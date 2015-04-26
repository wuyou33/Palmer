#===============================================================
#====== COLOR DETECTION - NO COMMUNICATION WITH ARDUINO ========
#===============================================================

# Camera view angle - 50 degrees

import cv2
import cv2.cv as cv
import numpy as np
import serial
import sys
import math as mt

center_frame = (88,72)    # The (x,y) coordinates of the center of the frame with the resolution 640*480
radius_frame = (10)        # The minimum desired radius of the object being tracked
area_frame = 314          # The desired area of the object that is being tracked
radius_frame_max = (25)    # The maximum desired radius of the object being tracked
area_frame_max = 1964   # The maximum desired area of the object being tracked
size = (240, 180)         # The resolution of the camera

pid_hor = 1
pid_ver = 0.3
pid_dis = 0.01

source = cv2.VideoCapture(0)

ret = source.set(cv.CV_CAP_PROP_FRAME_WIDTH,size[0])
ret = source.set(cv.CV_CAP_PROP_FRAME_HEIGHT,size[1])
source.set(5,20)

while(1):
    kernel_open = np.ones((5,5),np.uint8, 3) # Erosion values
    kernel_close = np.ones((5,5),np.uint8, 3) #Dilution values
    _, frame = source.read() # reads one frame at a time

    # Use this to get the resolution of the picture
    print(frame.shape)

    # BGR to HSV conversion helps better isolate a single color
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([35,50,50])
    upper_blue = np.array([60,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel_close)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= closing)
    imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,1,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # Use this to see the array of the object print(contours)
    # additional methods can be used on contours in order to find the area/perimeter and the center_obj

    cv2.circle(res,center_frame,radius_frame,(255,0,0),2)
    cv2.circle(res,center_frame,radius_frame_max,(0,0,255),2)

    if len(contours) > 0:
        cnt = contours[0]
        (x,y),radius_obj = cv2.minEnclosingCircle(cnt)
        center_obj = (int(x),int(y))
        radius_obj = int(radius_obj)
        cv2.circle(res,center_obj,radius_obj,(0,255,0),-1)

        area_obj = ((radius_obj**2)*3.14159265359)


        distance = 6.573/(mt.tan(((radius_obj/3.52)*mt.pi)/180))

        # Produces the new PID_yaw setpoint "-" corresponds to the CCW activation; "+" to the CW activation
        offset_hor = (str((float(center_obj[0]) - center_frame[0])/3.52)+"\n")
        # Alters the START_SPEED where "-" corresponds to the decrease in thrust and "+" to the increase in thrust
        offset_ver = (str((float(center_frame[1]) - center_obj[1])*pid_ver)+"\n")
        to_be_sent = [offset_hor,offset_ver,distance]

        for i in to_be_sent:
            print (i)

        # print (area, radius_obj)

    #ser.write(send_val)

    cv2.imshow('res',res)
    cv2.imshow('frame',frame)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()