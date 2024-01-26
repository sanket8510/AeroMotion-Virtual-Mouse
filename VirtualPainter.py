import cv2
import mediapipe as mp
import numpy as np
import time
import HandTrackingModule2 as htm
import os

folderPath="Header"
mylist=os.listdir(folderPath)
print(mylist)
################
brushThickness=15
EraserThickness=50
#########
overLay=[]
for imPath in mylist:
    image=cv2.imread(f'{folderPath}/{imPath}')
    overLay.append(image)
print(len(overLay))


header=overLay[0]
drawColor=(255,0,255)

# Set the desired window size
#window_width = 800
#window_height = 600

# Create a named window with the specified size
#cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
#cv2.resizeWindow("Image", window_width, window_height)

cap=cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

detector =htm.HandDetector(detection_confidence=0.85)
xp,yp=0,0
imgCanvas=np.zeros((720,1280,3),np.uint8)

while True:
#Import image
    success,img=cap.read()
    img=cv2.flip(img,1)

    #2 find hand landmarks
    img=detector.find_hands(img)
    lmList=detector.find_position(img,draw=False)

    if len(lmList)!=0:

        print(lmList)

        #tip of index and middle finger
        x1,y1=lmList[8][1:]
        x2, y2 = lmList[12][1:]


        #3 Checking which finger is up
        fingers=detector.fingersUp()
        print(fingers)



         #4 If Selection mode_ two finger are up
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0

            print("Selection mode ")

            #checking for the click
            if y1<125:
                if 250<x1<450:
                    header=overLay[0]
                    drawColor=(0,0,255)
                elif 550< x1 < 750:
                   header=overLay[1]
                   drawColor = (255, 0, 0)
                elif 800< x1 < 950:
                   header=overLay[2]
                   drawColor = (0, 255, 0)
                elif 1050< x1 < 1200:
                   header=overLay[3]
                   drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        #5 if we have drawing mode -- index finger is up
        if fingers[1] and fingers[2]==False:
            cv2.circle(img,(x1,y1),15,drawColor,cv2.FILLED)
            print("Drawing Mode")
            if xp==0 and yp==0:
                xp,yp=x1,y1
            if drawColor==(0,0,0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, EraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, EraserThickness)
            else:
                cv2.line(img,(xp,yp),(x1,y1),drawColor,brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp,yp=x1,y1

    imgGray=cv2.cvtColor(imgCanvas,cv2.COLOR_BGR2GRAY)
    _,imgInv=cv2.threshold(imgGray,50,255,cv2.THRESH_BINARY_INV)
    imgInv=cv2.cvtColor(imgInv,cv2.COLOR_GRAY2BGR)
    img=cv2.bitwise_and(img,imgInv)
    img=cv2.bitwise_or(img,imgCanvas)

#Setting the header image
    img[0:125,0:1280]=header
    cv2.imshow("Image",img)
    cv2.imshow("Canvas",imgCanvas)
    cv2.waitKey(1)

