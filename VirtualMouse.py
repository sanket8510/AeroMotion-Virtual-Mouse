import pyautogui as pag
from HandTrackingModule import HandDetector
import time
import cv2
import numpy as np

previous_time = 0
current_time = 0
cap = cv2.VideoCapture(0)
detector = HandDetector()
pag.FAILSAFE = False
screen_width, screen_height = pag.size()


def fingers(lm):
    finger_tips = []
    tip_ids = [4, 8, 12, 16, 20]
    print(" ")

    # Thumbs
    if len(lm) != 0:
        if lm[tip_ids[0]][1] < lm[tip_ids[0] - 1][1]:
            finger_tips.append(1)
        else:
            finger_tips.append(0)

        # Other fingers
        for id_tip in range(1, 5):
            if lm[tip_ids[id_tip]][2] < lm[tip_ids[id_tip] - 2][2]:
                finger_tips.append(1)
            else:
                finger_tips.append(0)

    return finger_tips


while cap.isOpened():

    success, img = cap.read()

    img_flip = cv2.flip(img, 1)
    img = detector.find_hands(img_flip)

    landmarks_list = detector.find_position(img)

    frame_height, frame_width, _ = img.shape

    if len(landmarks_list) != 0:

        index_tip_x, index_tip_y = landmarks_list[8][1:]
        index_tip_x = index_tip_x * 5
        index_tip_y = index_tip_y * 4

        finger = fingers(landmarks_list)

        if all(finger):
            pag.mouseUp()

        elif finger[1]:
            pag.moveTo(index_tip_x, index_tip_y)

            if finger[0] and not finger[2]:
                pag.leftClick(index_tip_x, index_tip_y)
                time.sleep(0.2)
                print("Left")

            if finger[2] and not finger[0]:
                pag.rightClick(index_tip_x, index_tip_y)
                time.sleep(0.2)
                print("Right")

            if finger[4]:
                pag.doubleClick(index_tip_x, index_tip_y)
                time.sleep(0.2)
                print("Double")

        elif not any(finger):
            pag.mouseDown()
            pag.moveTo(index_tip_x, index_tip_y)

    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time

    cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Virtual Mouse", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
