import cv2
import mediapipe as mp
import numpy as np
import time
import HandTrackingModule2 as htm
import os
import tkinter as tk
import pyautogui as pag
from tkinter import filedialog


def take_user_input():
    # Create a Tkinter window for input
    root = tk.Tk()
    root.title("User Input")

    # Variable to store the user input
    user_text = tk.StringVar()

    # Function to retrieve text from the entry widget and close the window
    def get_text_and_close():
        nonlocal user_text
        user_text = entry.get()
        root.destroy()  # Close the Tkinter window

    # Add a label and entry field
    label = tk.Label(root, text="Enter your text:")
    label.pack()
    entry = tk.Entry(root, textvariable=user_text)
    entry.pack()

    # Create a button to trigger text retrieval
    button = tk.Button(root, text="Submit", command=get_text_and_close)
    button.pack()

    # Start the Tkinter event loop to display the window
    root.mainloop()

    return user_text


# #######################  image file dialog ######################################

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    file_path = filedialog.askopenfilename(title="Select File",
                                           filetypes=[("Image files", "*.png;*.jpg;*.jpeg"),
                                                      ("Text files", "*.txt"),
                                                      ("PDF files", "*.pdf"),
                                                      ("All files", "*.*")])  # Allow various file types
    root.destroy()  # Close the Tkinter window
    return file_path


# ############################## Canvas Clearing ######################
def clear_canvas():
    global imgCanvas
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)


def calculate_distance(x1, y1, x2, y2):
    return int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


folderPath = "Header"
mylist = os.listdir(folderPath)
print(mylist)
################
brushThickness = 15
EraserThickness = 50

################
overLay = []
for imPath in mylist:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overLay.append(image)
print(len(overLay))
header = overLay[0]
drawColor = (255, 0, 255)

###################################################################
folderPath2 = "Thickness"
mylist2 = os.listdir(folderPath2)
print(mylist2)
sideLay = []
for imPath2 in mylist2:
    image = cv2.imread(f'{folderPath2}/{imPath2}')
    sideLay.append(image)
print(len(sideLay))

side = sideLay[0]

# ##################################################################################Shapes
folderPath3 = "Shapes"
mylist3 = os.listdir(folderPath3)
print(mylist3)
shapeLay = []
for imPath3 in mylist3:
    image = cv2.imread(f'{folderPath3}/{imPath3}')
    shapeLay.append(image)
print(len(shapeLay))

shape = shapeLay[0]

buttonimage_path: str = "Buttons\\first.jpg"
buttonimage = cv2.imread(buttonimage_path)

# ############################################################################3

# Set the desired window size
window_width = 1280
window_height = 730

# Create a named window with the specified size
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", window_width, window_height)

cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT,screen_height)

cap.set(3, 1280)
cap.set(4, 720)
############################################################################################

detector = htm.HandDetector(detection_confidence=0.85)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

while True:
    # Import image
    success, img, = cap.read()
    frame = cap.read()
    img = cv2.flip(img, 1)

    # ###############################################################2 find hand landmarks
    img = detector.find_hands(img)
    lmList = detector.find_position(img, draw=False)

    if len(lmList) != 0:

        print(lmList)

        # tip of index and middle finger
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3 Checking which finger is up
        fingers = detector.fingersUp()
        print(fingers)

        # 4 If Selection mode_ two finger are up
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0

            print("Selection mode ")

            # checking for the click

            if y1 < 125:

                if 10 < x1 < 150:
                    header = overLay[1]
                    drawColor = (0, 255, 0)  # green

                elif 160 < x1 < 250:
                    header = overLay[2]
                    drawColor = (0, 0, 255)  # red

                elif 260 < x1 < 450:
                    header = overLay[3]
                    drawColor = (255, 255, 255)  # white

                elif 460 < x1 < 600:
                    header = overLay[4]
                    drawColor = (42, 42, 165)  # Brown

                elif 620 < x1 < 800:
                    header = overLay[5]
                    drawColor = (255, 0, 0)  # blue

                elif 820 < x1 < 1000:
                    header = overLay[6]  # TextBox

                    userText = take_user_input()

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    fontScale = 1
                    textsize = cv2.getTextSize(userText, font, fontScale, thickness=1)[0]
                    text_x = (600 + 500) // 2 - textsize[0] // 2
                    text_y = (600 + 500) // 2 + textsize[1] // 2
                    cv2.putText(img, userText, (text_x, text_y), font, fontScale, (255, 255, 255), thickness=2)
                    cv2.putText(imgCanvas, userText, (text_x, text_y), font, fontScale, (255, 255, 255), thickness=2)
                    dist = calculate_distance(text_x, text_y, x1, x2)

                    if fingers[1] and fingers[2] and dist <= text_x and dist <= text_y:
                        text_x, text_y = x1, y1

                    cv2.putText(img, userText, (text_x, text_y), font, fontScale, (255, 255, 255), thickness=2)
                    cv2.putText(imgCanvas, userText, (text_x, text_y), font, fontScale, (255, 255, 255), thickness=2)

                    # if fingers[1] and fingers[2]:
                    #  dx = x1 - xp-50
                    #  dy = y1 - yp+100
                    #  text_x = dx
                    #  text_y = dy

                    # Display the text on the canvas
                #  cv2.putText(img, userText, (text_x, text_y), font, fontScale, (255, 255, 255), thickness=2)
                # cv2.putText(imgCanvas, userText, (text_x, text_y), font, fontScale, (255, 255, 255), thickness=2)

                # Reset finger positions if fingers are not raised
                # if not fingers[1] and not fingers[2]:
                # xp, yp = 0,0

                ################################################################################

                #####################################################################
                elif 1020 < x1 < 1250:
                    header = overLay[7]
                    drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
        # Thickness
        if x1 < 120 and 120 <= y1 < 595:
            if 125 < y1 < 225:  # Adjusted range for the first option
                side = sideLay[0]
                brushThickness = 5
            elif 227 < y1 < 327:  # Adjusted range for the second option
                side = sideLay[1]
                brushThickness = 15
            elif 337 < y1 < 425:
                side = sideLay[2]
                brushThickness = 25
            elif 437 < y1 < 590:
                side = sideLay[3]
                brushThickness = 35
        # ###################################################################### Shapes
        #  cv2.rectangle(img, pt1=(600, 600), pt2=(500, 500), color=(255, 255, 255), thickness=2)
        # cv2.circle(img, center=(50, 50), radius=50, color=(0, 255, 0), thickness=-1)
        if x1 > 1160 and 125 <= y1 < 595:
            if 125 < y1 < 245:
                shape = shapeLay[1]

                # Set shape to circle (adjust if needed)
            elif 325 < y1 < 425:
                shape = shapeLay[2]
            elif 425 < y1 < 595:
                shape = shapeLay[3]

        if np.array_equal(shape, shapeLay[3]) and fingers[1] and not fingers[2]:
            # Drawing mode
            center_x = 500
            center_y = 500  # Track circle center
            radius = 50
            # index1 = int(lmList[8] * frame.shape[1])
            # middle1 = int(lmList[12] * frame.shape[0])
            index1 = x1
            middle1 = x2
            distCircle = calculate_distance(center_x, center_y, index1, middle1)

            cv2.circle(img, (center_x, center_y), radius, drawColor, brushThickness)
            cv2.circle(imgCanvas, (center_x, center_y), radius, drawColor, brushThickness)

            if distCircle < radius:
                circle_x, circle_y = index1, middle1
                cv2.circle(img, (center_x, center_y), radius, drawColor, brushThickness)
                cv2.circle(imgCanvas, (center_x, center_y), radius, drawColor, brushThickness)

        ######################################################################

        # 5 if we have drawing mode -- index finger is up
        if fingers[1] and fingers[2] == False:
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
            print("Drawing Mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1
            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, EraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, EraserThickness)

            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1

    key = cv2.waitKey(1)

    if key == ord('f'):  # Press 'f' to select a file
        # dialogImage = select_file()
        dialogImage = cv2.imread(select_file())
        if dialogImage is not None:
            # Resize the image to fit the screen

            aspect_ratio = dialogImage.shape[1] / dialogImage.shape[0]  # width / height

            # Resize the image based on the desired width while maintaining the aspect ratio
            window_width = 300
            window_height = int(window_width / aspect_ratio)
            dialogImage_resized = cv2.resize(dialogImage, (window_width, window_height))

            start_x = 130
            start_y = 130
            end_x = start_x + dialogImage_resized.shape[1]  # width
            end_y = start_y + dialogImage_resized.shape[0]  # height

            # Assign the resized image to the correct area
            img[start_y:end_y, start_x:end_x] = dialogImage_resized
            imgCanvas[start_y:end_y, start_x:end_x] = dialogImage_resized

    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite("canvas_frame.png", imgCanvas)
        print("Canvas frame saved as canvas_frame.png")

    # ############  FOR CANVAS CLEARING #######################################
    if key == ord('c'):  # Press 'c' to clear the canvas
        clear_canvas()

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # Setting the header image
    img[0:125, 0:1280] = header
    side_resized = cv2.resize(side, (120, 470))
    img[125:595, 0:120] = side_resized
    shape_resized = cv2.resize(shape, (120, 470))
    img[125:595, 1160:1280] = shape_resized
    button_resized = cv2.resize(buttonimage, (120, 120))
    img[596:596 + 120, 0:120] = button_resized
    # img_resized = cv2.resize(Image, (screen_width, screen_height), interpolation=cv2.INTER_AREA)

    cv2.imshow("Image", img)
    cv2.imshow("Canvas", imgCanvas)
    cv2.waitKey(1)
