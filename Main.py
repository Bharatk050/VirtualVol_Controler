from typing import Text
import cv2
import time
import numpy as np
import handTrackingModule as htm  # HandTrackingModule
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)
wCam, hCam = 640, 480
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

Detector = htm.handDetector(detectionCon= 0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

while True:
    _, img = cap.read()
    img = Detector.findHands(img)
    lmlist = Detector.findPosition(img, draw= False)
    if len(lmlist) != 0:
        # print(lmlist[4], lmlist[8])
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2
        
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        lenght = math.hypot(x2-x1, y2-y1)
        # print(lenght)

        vol = np.interp(lenght, [50, 300], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)

        if lenght < 50:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    

    cTime = time.time()
    fps= 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (30, 50), cv2.FONT_HERSHEY_PLAIN, 2, 0, 3)

    cv2.imshow("Original", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
