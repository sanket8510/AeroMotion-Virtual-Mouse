from HandTrackingModule import HandDetector, fingers
import cv2
import pyautogui as pag
from math import hypot
import time
import numpy as np
import screen_brightness_control as sbc
import pygetwindow as pgw
from PIL import Image, ImageTk
import tkinter as tk


def is_browser_open():
    for player in media_players:
        if window is not None:
            if player in window.title:
                return False

    for browser in browsers:
        if window is not None:
            if browser in window.title:
                return True


def is_thumb_down():
    tip_ids = [4, 8, 12, 16, 20]
    thumb_status = []

    # thumb
    if (landmarks_list[tip_ids[0]][2] > landmarks_list[tip_ids[0] - 1][2] > landmarks_list[tip_ids[0] - 2][2] >
            landmarks_list[tip_ids[0] - 3][2]):
        thumb_status.append(1)
    else:
        thumb_status.append(0)

    # other fingers
    for tip_id in range(1, 5):
        if landmarks_list[tip_ids[tip_id]][1] < landmarks_list[tip_ids[tip_id] - 2][1]:
            thumb_status.append(1)
        else:
            thumb_status.append(0)

    return thumb_status


def rect_check(lm, left_top, right_bottom):
    wrist_x, wrist_y = lm[0][1], lm[0][2]
    if (left_top[0] <= wrist_x < right_bottom[0]) and (left_top[1] < wrist_y < right_bottom[1]):
        if lm[0][-1] == 'Left':
            return 'Left'
        else:
            return 'Right'


# def right_rect_check(lm):
#     wrist_x, wrist_y = lm[0][1], lm[0][2]
#     if ((left_top_right[0] <= wrist_x < right_bottom_right[0]) and
#             (left_top_right[1] < wrist_y < right_bottom_right[1]) and
#             (lm[0][-1] == 'Right')):
#
#         return True
#     return False


def is_media_player_open():
    for media_player in media_players:

        try:
            if window is not None:
                window_name = window.title
                print(window_name)
                if media_player in window_name:
                    return True
        except Exception as ex:
            print(f"Error Checking media player: {ex}")

    return False


# Volume Controlling function
def volume_control(index_x, index_y, thumb_x, thumb_y):
    # drawing circles on index and thumb tips
    cv2.circle(img_resized, (index_x, index_y), 8, (0, 0, 0), 6)
    cv2.circle(img_resized, (thumb_x, thumb_y), 8, (0, 0, 0), 6)

    # draw line
    cv2.line(img_resized, (index_x, index_y), (thumb_x, thumb_y), (0, 0, 0), 6)

    # calculate center of fingers
    center_x, center_y = (index_x + thumb_x) // 2, (index_y + thumb_y) // 2

    # draw circle at center
    cv2.circle(img_resized, (center_x, center_y), 8, (0, 0, 0), cv2.FILLED)

    length = hypot(index_x - thumb_x, index_y - thumb_y)
    # print(length)

    if length > 80:
        pag.press("volumeup")
        time.sleep(0.1)
    else:
        pag.press("volumedown")
        time.sleep(0.1)


# Brightness Controlling function
def brightness_control(middle_x, middle_y, thumb_x, thumb_y):
    cv2.circle(img_resized, (middle_x, middle_y), 8, (0, 0, 0), 6)
    cv2.circle(img_resized, (thumb_x, thumb_y), 8, (0, 0, 0), 6)
    # draw line
    cv2.line(img_resized, (middle_x, middle_y), (thumb_x, thumb_y), (0, 0, 0), 6)

    # calculate center of fingers
    center_x, center_y = (middle_x + thumb_x) // 2, (middle_y + thumb_y) // 2
    # draw circle at center
    cv2.circle(img_resized, (center_x, center_y), 8, (0, 0, 0), cv2.FILLED)

    length = hypot(middle_x - thumb_x, middle_y - thumb_y)
    bright = np.interp(length, [15, 220], [0, 100])

    try:
        sbc.set_brightness(int(bright))
        time.sleep(0.1)
    except Exception as ex:
        print(f"Error in Brightness Control: {ex}")


cap = cv2.VideoCapture(0)
detector = HandDetector(detection_confidence=0.85)

screen_width, screen_height = pag.size()
screen_width_division = screen_width // 3
right_rect_x = screen_width_division * 2

color_left = color_right = (0, 0, 255)

# left top rect coordinates
left_top_left = (0, 0)
right_bottom_left = (screen_width_division, screen_height)

# right top rect coordinates
left_top_right = (right_rect_x, 0)
right_bottom_right = (screen_width, screen_height)


# miniplayer dimensions
miniplayer_height = 500
miniplayer_width = 500

screen_width_division_miniplayer = miniplayer_width // 3

# left top rect coordinates for miniplayer
left_top_miniplayer_left = (0, 0)
right_bottom_miniplayer_left = (screen_width_division_miniplayer, miniplayer_height)

# right top rect coordinates for miniplayer
left_top_miniplayer_right = (screen_width_division_miniplayer * 2, 0)
right_bottom_miniplayer_right = (miniplayer_height, miniplayer_width)


# Media Players
media_players = ["Media Player", "VLC media player", "YouTube", "Plex", "RealPlayer", "GOM Media Player",
                 "ACG Player", "Winamp", "PowerDVD", "iTunes", "Spotify"]

# Browsers
browsers = ["- Google Chrome", "- Brave", "- Opera", "- Microsoft Edge", "- Mozilla Firefox"]

cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

# print(screen_width, " ", screen_height)
# print(screen_width_division)

img = None

while cap.isOpened():

    try:
        success, img = cap.read()
        if not success:
            raise Exception("Error: Unable to read the Video")
    except Exception as e:
        print(f"Error: {e}")

    window = pgw.getActiveWindow()

    img_flip = cv2.flip(img, 1)
    img = detector.find_hands(img_flip)

    img_resized = cv2.resize(img, (screen_width, screen_height), interpolation=cv2.INTER_AREA)
    miniplayer_size = cv2.resize(img, (miniplayer_width, miniplayer_height), interpolation=cv2.INTER_AREA)

    landmarks_list = detector.find_position(img_resized)

    # frame_height, frame_width, _ = img.shape
    # print("Frame Height: ", frame_height)
    # print("Frame Width: ", frame_width)

    if len(landmarks_list) != 0:

        finger = fingers(landmarks_list)

        # is_left_thumb_open = landmarks_list[4][1] > landmarks_list[3][1]
        is_left_thumb_open = (landmarks_list[4][1] > landmarks_list[3][1] > landmarks_list[2][1] >
                              landmarks_list[1][1] and landmarks_list[8][1] < landmarks_list[4][1])

        is_left_thumb_pointing_left = (landmarks_list[4][1] < landmarks_list[3][1] < landmarks_list[2][1] <
                                       landmarks_list[1][1] and landmarks_list[8][1] > landmarks_list[4][1])

        # Left Hand Gestures Detection
        if rect_check(landmarks_list, left_top_left, right_bottom_left) == 'Left':

            color_left = (0, 255, 0)

            if is_media_player_open():

                print("Media Player is open")

                # Pause
                if finger[1] == 1 and finger[2] == 1 and (not is_left_thumb_open) and finger[3] == 0 and finger[4] == 0:
                    # window.activate()
                    print("Two fingers are Open")
                    pag.press('space')
                    time.sleep(2)
                # not (all([finger[1], finger[2], finger[3], finger[4]]))

                elif finger[4] == 0 and finger[3] == 0 and finger[2] == 0 and finger[1] == 0:

                    # forward
                    if is_left_thumb_open:
                        if window.title is not None:
                            window_title = window.title
                            # if "Spotify" in window_title:
                            #     pag.hotkey('shift', 'right')
                            if "Media Player" in window_title:
                                pag.hotkey('ctrl', 'right')
                            elif "VLC Media Player" in window_title:
                                pag.hotkey('alt', 'right')
                            else:
                                pag.press('right')
                            time.sleep(1)

                    # rewind
                    elif is_left_thumb_pointing_left:
                        if window.title is not None:
                            window_title = window.title
                            print(window_title)
                            # if "Spotify" in window_title:
                            #     pag.hotkey('shift', 'left')
                            if "Media Player" in window_title:
                                pag.hotkey('ctrl', 'left')
                            elif "VLC Media Player" in window_title:
                                pag.hotkey('alt', 'left')
                            else:
                                pag.press('left')
                            time.sleep(1)

                # Forward
                # if is_left_thumb_open and finger[1] == 0 and finger[2] == 0 and finger[3] == 0 and finger[4] == 0:
                #     if window.title is not None:
                #         window_title = window.title
                #         # if "Spotify" in window_title:
                #         #     pag.hotkey('shift', 'right')
                #         if "Media Player" in window_title:
                #             pag.hotkey('ctrl', 'right')
                #         elif "VLC Media Player" in window_title:
                #             pag.hotkey('alt', 'right')
                #         else:
                #             pag.press('right')
                #     time.sleep(2)
                #
                # # Rewind
                # elif (finger[4] == 0 and is_left_thumb_pointing_left and finger[1] == 0 and finger[2] == 0 and
                #         finger[3] == 0):
                #     if window.title is not None:
                #         window_title = window.title
                #         print(window_title)
                #         # if "Spotify" in window_title:
                #         #     pag.hotkey('shift', 'left')
                #         if "Media Player" in window_title:
                #             pag.hotkey('ctrl', 'left')
                #         elif "VLC Media Player" in window_title:
                #             pag.hotkey('alt', 'left')
                #         else:
                #             pag.press('left')
                #     time.sleep(2)

            if is_browser_open():

                print("Browser is Open")

                if finger[4] == 0 and finger[3] == 0 and finger[2] == 0 and finger[1] == 0:

                    # next
                    if is_left_thumb_open:
                        print("Next")
                        pag.hotkey('alt', 'right')
                        time.sleep(1)

                    # previous
                    elif is_left_thumb_pointing_left:
                        print("Previous")
                        pag.hotkey('alt', 'left')
                        time.sleep(1)

                # # next
                # if is_left_thumb_open and finger[1] == 0 and finger[2] == 0 and finger[3] == 0 and finger[4] == 0:
                #     print("Next")
                #     pag.hotkey('alt', 'right')
                #     time.sleep(2)
                #
                # # previous
                # elif finger[4] and not is_left_thumb_open and finger[1] == 0 and finger[2] == 0 and finger[3] == 0:
                #     print("Previous")
                #     pag.hotkey('alt', 'left')
                #     time.sleep(2)

            # Open desktop
            thumb_down = is_thumb_down()

            if thumb_down == [1, 1, 1, 1, 1]:
                print("Thumb's Down")
                pag.hotkey('win', 'd')
                time.sleep(2)

            print("Left hand in left rectangle")

        else:
            color_left = (0, 0, 255)

        # Right Hand Gestures Detection
        if rect_check(landmarks_list, left_top_right, right_bottom_right) == 'Right':

            color_right = (0, 255, 0)

            if finger[2] == 0 and finger[3] == 0 and finger[4] == 0 and finger[0] == 1:
                volume_control(landmarks_list[8][1], landmarks_list[8][2], landmarks_list[4][1], landmarks_list[4][2])

            if finger[3] == 0 and finger[4] == 0 and finger[1] == 0 and finger[0] == 1:
                brightness_control(landmarks_list[12][1], landmarks_list[12][2], landmarks_list[4][1],
                                   landmarks_list[4][2])

            if finger[1] == 1 and finger[2] == 1 and finger[0] == 0 and finger[3] == 0 and finger[4] == 0:
                pag.press('printscreen')
                time.sleep(3)

            print("Right hand in right rectangle")
        else:
            color_right = (0, 0, 255)

        print("Thumb status: ", is_left_thumb_pointing_left)

    cv2.rectangle(img_resized, left_top_left, right_bottom_left, color_left, 6)
    cv2.rectangle(img_resized, left_top_right, right_bottom_right, color_right, 6)

    cv2.rectangle(miniplayer_size, left_top_miniplayer_left, right_bottom_miniplayer_left, color_left, 6)
    cv2.rectangle(miniplayer_size, left_top_miniplayer_right, right_bottom_miniplayer_right, color_right, 6)

    cv2.putText(miniplayer_size, "Left Hand Gestures", (14, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                (0, 0, 0), 2)
    cv2.putText(miniplayer_size, "Right Hand Gestures", (347, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                (0, 0, 0), 2)

    # cv2.circle(img_resized, (right_rect_x, 0), 3, (255, 255, 0), 6)

    cv2.imshow("Hand Gesture Detection", img_resized)

    # root = tk.Tk()
    # root.title("Hand Gestures Recognition")
    # video_label = tk.Label(root)
    # video_label.pack()
    #
    # img_tk = ImageTk.PhotoImage(Image.fromarray(img_resized))
    #
    # video_label.img = img_tk
    # video_label.config(image=img_tk)
    #
    # root.mainloop()

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
