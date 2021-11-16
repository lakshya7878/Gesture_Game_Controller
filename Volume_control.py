import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput.keyboard import Key, Controller

wCam , hCam = 1280,720




keyboard = Controller()
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()


volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList)!= 0:
        # print(lmList[4],lmList[8])

        x1,y1 = lmList[4][1],lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        # cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
        # cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)

        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)
        cx,cy  = (x1+x2)//2 , (y1+y2)//2
        cv2.circle(img, (cx,cy), 8, (255, 0, 255), cv2.FILLED)
        length = math.hypot(y2-y1,x2-x1)
        print(length)

        # if length>50:
        #     keyboard.press(Key.space)
        #
        #     continue
        # else:
        #     keyboard.release(Key.space)
        #     cv2.waitKey(0)
        #     continue

        #conversion of one range to another using numpy
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])

        print(vol)

        volume.SetMasterVolumeLevel(vol, None)


        #if volume goes down a certain point it will change the color of centre circle
        if length<50:
            cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)


    #This is for the volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)


    #This is to print frequency aka fps
    cTime = time.time()
    if((cTime-pTime)!=0):
        fps = 1/(cTime-pTime)
        pTime = cTime
        cv2.putText(img,f'FPS: {int(fps)}',(30,50),cv2.FONT_HERSHEY_SIMPLEX,
                    1,(255,0,0),3)



    cv2.imshow("Img",img)
    cv2.waitKey(1)