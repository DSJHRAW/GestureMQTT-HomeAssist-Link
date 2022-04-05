from cvzone import HandTrackingModule
import os
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from turtle import delay

# The goal is to create a dictionary, where the keys are the values from (0,len(fingerImages) and the values are the
# strings from fingerImages
class handDictionary():
    def __init__(self, folderPath):
        self.folderPath = folderPath


def main():

    #=======================#
    #Initialize MQTT Broke..#
    mqttBroker ="172.20.10.9"
    client = mqtt.Client("FingerCount")
    client.connect(mqttBroker)
    delay_mqtt = 0
    #=======================#

    # variables
    width, height = 640, 480

    # camera setup

    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)

    #   Accessing the fingers
    folderPath = "FingerImages1"
    fingerImages = sorted(os.listdir(folderPath), key=len)  # Accesses all the fingerImages
    print(fingerImages)
    overLayList = []
    for imPath in fingerImages:
        image = cv2.imread(f'{folderPath}/{imPath}')
        overLayList.append(image)
    # print(overLayList)

    #   Hand Detector
    detector = HandTrackingModule.HandDetector(detectionCon=0.8, maxHands=1)
    # Main Body
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)  # calls findHands method
        
        if hands:  # if there are hands
            hand = hands[0]  # only one hand
            fingers = detector.fingersUp(hand)            # calls fingersUp method to see how many fingers are up,
            key = str(binaryCalc(fingers))
            thisDict = fingerDict(fingerImages)
            delay_mqtt += 1
            if key in thisDict.keys():  # Tests if the str value is in keys
                #print("True")
                print(thisDict.get(key))                    #Prints the value that is associated with the key
                for i in range(len(fingerImages)):
                    if thisDict.get(key) == fingerImages[i]: #Compares the strings
                        print(i)
                        picture = overLayList[i]
                        #print(picture)
                        h, w, c = picture.shape
                        img[0:h, 0:w] = picture[0:h, 0:w]
                        
                        #====================================#
                        #Relay Finger Count to MQTT Subcriber#
                        if delay_mqtt >= 10:
                            client.publish("Count",fingerImages[i])
                            print("Finger Count Has Been Sent To Home Assistant")
                            delay_mqtt = 0

                    # h, w, c = thisDict.get(key).shape  # takes the height, width and color of the image,    (My code)
                    # img[0:h, 0:w] = thisDict.get(key).shape[0:h, 0:w]  # overlays the image on top of the video recording   (My code)
            else:
                print("False")

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break


def binaryCalc(fingArray):                  #Returns int = fingers open in terms of pow(2,open)
    runningTotal = []                       #Empty array to populate later
    for i in range(len(fingArray)):         #Runs for loop for length of fingArray (fingerimages is passed value)
        if fingArray[i] == 1:               #checks if the value at the given point is a 1 or a zero
            runningTotal.append(pow(2, i))  #appends the runningTotal array with value of pow(2^i)
    return sum(runningTotal)                #adds the total and returns it as an int

def fingerDict(fingImgs): #Creates a dictionary using images passed in, str value of file is key, .jpg is value
    dict = {}
    fingKeys = []                       #Creates a blank array
    for img in range(len(fingImgs)):    #for each image in the range of fingImages (passed value is array of .jpgs
        image = fingImgs[img]           #Each image str is saved
        key = image[:-4]                #The .jpg suffix is removed
        fingKeys.append(key)            #Adds the key value (number)
    total = zip(fingKeys, fingImgs)     #zips up the keys with their respective values
    for i, j in total:                  #populates the dictionary with the key and their value
        dict[i] = j
    return dict                         #Returns Dictionary

if __name__ == "__main__":
    main()
