import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone

#Capturing video
cap = cv2.VideoCapture(0)

#setting width hd resolution
cap.set(3,1280)

#setting height
cap.set(4,720)

#hand detector
detector = HandDetector(detectionCon=0.8)

keys = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', "I", 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', 'CAPS'],
        ['CLR', 'CLRAll', ' ']]

finalText = ""
delayCounter = 0
# def drawALL(img, buttonList):
#     for button in buttonList:
#         x, y = button.pos
#         w, h = button.size
#         cv2.rectangle(img, button.pos, (x + w, y + h), (0, 0, 0), cv2.FILLED)
#         if button.text == 'I':
#             cv2.putText(img, button.text, (x + 30, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
#         else:
#             cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
#     return img

def drawAll(img, buttonList):

    imgNew = np.zeros_like(img, dtype=np.uint8)  # Make sure this line exists first!

    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(imgNew, (x, y, w, h), 20, rt=0)
        cv2.rectangle(imgNew, button.pos, (x + w, y + h), (251, 191, 0), cv2.FILLED)  # ← this line here
        offset = 30 if button.text == 'I' else 20
        cv2.putText(imgNew, button.text, (x + offset, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # alpha blending
    # alpha = 0.5
    # gray = cv2.cvtColor(imgNew, cv2.COLOR_BGR2GRAY)
    # mask = gray > 0
    # blended = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)

    out = img.copy()
    alpha = 0.3
    mask = imgNew.astype(bool)
    print(mask.shape)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1-alpha, 0)[mask]

    return out




class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == ' ':
            buttonList.append(Button([100 * j + 390, 100 * i + 50], key,size=[440, 85]))
            continue
        if key == 'CLR' or key == 'CAPS':
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key, size=[230, 85]))
            continue
        if key == 'CLRAll':
            buttonList.append(Button([100*j+190, 100*i+50], key,[280,85]))
            continue
        if key:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))
capState=0
while True:
    success, img = cap.read()
    #Finding hand and its landmarks(lmlist) and bounding box(bboxInfo)
    if not success or img is None:
        continue
    img = cv2.flip(img,1)
    detector.findHands(img)  # Don’t reassign
    lmList, bboxInfo = detector.findPosition(img)
    img=drawAll(img, buttonList)
    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            _, x1, y1 = lmList[8]
            _, x2, y2 = lmList[12]
            if x < x1 < x + w and y < y1 < y + h:
                cv2.rectangle(img, (x , y), (x + w , y + h), (251, 191, 0), cv2.FILLED)
                offset = 30 if button.text == 'I' else 20
                cv2.putText(img, button.text, (x + offset, y + 70),
                            cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 4)
                l, _, _ = detector.findDistance((x1,y1),(x2,y2), img)
                print(l)
                sleep(0.18)
                if l < 47 and delayCounter == 0:
                    cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    offset = 30 if button.text == 'I' else 20
                    cv2.putText(img, button.text, (x + offset, y + 70),
                                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 4)
                    if button.text == 'CLR':
                        finalText = finalText[:-1]
                    elif button.text == 'CLRAll':
                        finalText = ""
                    elif button.text == 'CAPS':
                        capState=1-capState
                    else:
                        if capState == 1:
                            finalText += button.text
                        else:
                            finalText += button.text.lower()

                    delayCounter = 1

                if delayCounter != 0:
                    delayCounter += 1
                    if delayCounter > 10:  # Adjust to control key repeat delay
                        delayCounter = 0
    cv2.rectangle(img, (50, 460), (740, 540), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, finalText, (60, 523), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
