from turtle import delay
import cv2
import time
import paho.mqtt.client as mqtt
from random import randrange, uniform 
import numpy as np
import HandTrackingModule as htm
import os

#=======================#
#Initialize MQTT Broke..#
mqttBroker ="172.20.10.9"
client = mqtt.Client("FingerCount")
client.connect(mqttBroker)
delay_mqtt = 0
#=======================#

#########################
wCam, hCam = 640, 480 # sets width and height of the display cam in pixels
#########################

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)

folderPath = "FingerImages"
myList = os.listdir(folderPath)
print(myList)
overLayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    #print(f'{folderPath}/{imPath}')
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    overLayList.append(image)

print(len(overLayList))

detector = htm.handDetector(detectionCon=0.75)           #calls the handDetector method, detectionCon sets the confidence value

tipIds = [4, 8, 12, 16, 20]                     #tips of the fingers as defined by mediaPipe

while True:
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # turns pictures greyscale
    #print(overLayList[0])
    #print() #check for img size
    #img = overLayList[0][0:200, 0:200]
    img = np.empty((wCam, hCam))                #populates the img with empty of size wCam and hCam (defined above) (My code)
    success, img = cap.read()                   #starts video recording
    img = detector.findHands(img)               #calls the findHands method, passes in img value, img val is returned

    lmList = detector.findPosition(img, draw=False)
    #print(lmList)

    if len(lmList) != 0:
        # cv2.imshow("Img", img)                                        #webcam turning on
        # cv2.waitKey(1)                                                #webcam delay
        fingers = []                                                    #Finger Array that saves if the finger is open or closed (1, 0)

        #   Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:             #sees if the tip of the thumb is to the right or left of the point below the thumb, (right hand only)
            fingers.append(1)
        else:
            fingers.append(0)
        #   For fingers except thumb
        for id in range(1,5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:         #if the fingerId is lower than the fingerId -2 (open or closed)
                #print("Index Finger open")
                fingers.append(1)
            else:
                fingers.append(0)

        #print(fingers)
        totalFingers = fingers.count(1)
        delay_mqtt += 1
        print(totalFingers)
        print(delay_mqtt)

        h, w, c = overLayList[totalFingers-1].shape              #takes the height, width and color of the image,    (My code)
        img[0:h, 0:w] = overLayList[totalFingers-1][0:h, 0:w]    #overlays the image on top of the video recording   (My code)

        
        #====================================#
        #Relay Finger Count to MQTT Subcriber#
        if delay_mqtt >= 10:
            client.publish("Count",totalFingers)
            print("Finger Count Has Been Sent To Home Assistant")
            delay_mqtt = 0
            
        cv2.imshow("Img", img)
        cv2.waitKey(1)
