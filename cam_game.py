import math
import tkinter as tk
import cv2
import mediapipe as mp
import random
import time
import threading
from PIL import Image
import socket



dotsX = [0,0]
dotsY = [0,0]
color = ['black','black']
dotsX2 = [0,0]
dotsY2 = [0,0]
color2 = ['black','black']


PREV_DOT = 0
PREV_DOT2 = 0
now = 0
now2 = 0

width = 0
height = 0
playing = False


def testui():
    def add_dot():
        global playing
        global now,now2
        global PREV_DOT,PREV_DOT2
        global dotsX,dotsY,dotsX2,dotsY2,width,height
        #print(dotsX)
        #print(now)
        #print('testui!')
        if not playing:
            print('exiting')
            root.quit()
            dotsX = []
            dotsY = []
            dotsX2 = []
            dotsY2 = []
            height = 0
            width = 0
            return
        if(now < len(dotsX) - 1):
            now += 1

            x = int(dotsX[now])
            y = int(dotsY[now])

            dot = canvas.create_oval(x, y, x + 3, y + 3, fill=color[now],outline=color[now])
            if PREV_DOT == 0:
                PREV_DOT = dot

            if 'PREV_DOT' in globals():
                x1, y1, _, _ = canvas.coords(PREV_DOT)
                distance = math.sqrt(math.pow((x1 - x), 2) + math.pow((y1 - y), 2))
                if(distance < 30.0):
                    canvas.create_line(x, y, x1, y1, width=4,fill=color[now])

            root.after(10, add_dot)
            PREV_DOT = dot
        else:
            #print('dotsx is too short - ' +str(dotsX))
            root.after(100, add_dot)
        if (now2 < len(dotsX2) - 1):
            now2 += 1

            x2 = int(dotsX2[now2])
            y2 = int(dotsY2[now2])

            dot2 = canvas.create_oval(x2, y2, x2 + 3, y2 + 3, fill=color2[now2],outline=color2[now2])
            if PREV_DOT2 == 0:
                PREV_DOT2 = dot2

            if 'PREV_DOT2' in globals():
                x3, y3, _, _ = canvas.coords(PREV_DOT)
                distance = math.sqrt(math.pow((x3 - x2), 2) + math.pow((y3 - y2), 2))
                if (distance < 30.0):
                    canvas.create_line(x2, y2, x3, y3, width=4,fill=color2[now2])

            root.after(10, add_dot)
            PREV_DOT2 = dot2
        else:
            #print('dotsx2 is too short - ' + str(dotsX2))
            root.after(100, add_dot)
    #print('im in the testui and playing is: ' + str(playing))
    global width
    global height
    while(width == 0):
        time.sleep(0.1)
    # Create the window and canvas
    root = tk.Tk()
    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()
    root.after(10, add_dot)

    # Start the main loop
    root.mainloop()



class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5,modelComplexity=1,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils  # it gives small dots onhands total 20 landmark points

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 255, 255), cv2.FILLED)
        return lmlist

    def findPosition2(self, img, handNo=1, draw=True):
        lmlist2 = []
        if(type(self.results.multi_hand_landmarks) != list):
            return lmlist2
        if len(self.results.multi_hand_landmarks) < 2:
            return lmlist2
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist2.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (0, 0, 0), cv2.FILLED)
        return lmlist2

def trackhands():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    start = time.time()

    global playing

    global width
    global height
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = f"@width - {width},height - {height}"
    client.send(size.encode('utf-8'))
    print(f"cam size: {width}x{height}")

    global dotsX
    global dotsY

    global dotsX2
    global dotsY2

    currentcolor = 'black'

    while playing:

        success, img = cap.read()
        img = cv2.flip(img,1)
        img = detector.findHands(img)
        lmlist = detector.findPosition(img)
        lmlist2 = detector.findPosition2(img)

        if len(lmlist) != 0:
            a = str(lmlist[4])
            a = a.split(', ', 1)[1]
            a = a[:a.find(']')].strip()
            a = '(' + a + ')'
            #print('a :' + a)

            b = str(lmlist[8])
            b = b.split(', ', 1)[1]
            b = b[:b.find(']')].strip()
            b = '(' + b + ')'
            #print('b :' + b)

            c = str(lmlist[12])
            c = c.split(', ', 1)[1]
            c = c[:c.find(']')].strip()
            c = '(' + c + ')'
            #print('c :' + c)

            d = str(lmlist[16])
            d = d.split(', ', 1)[1]
            d = d[:d.find(']')].strip()
            d = '(' + d + ')'
            #print('d :' + d)

            e = str(lmlist[20])
            e = e.split(', ', 1)[1]
            e = e[:e.find(']')].strip()
            e = '(' + e + ')'
            #print('e :' + e)



            if(lmlist2 != []):
                a2 = str(lmlist2[4])
                a2 = a2.split(', ', 1)[1]
                a2 = a2[:a2.find(']')].strip()
                a2 = '(' + a2 + ')'
                # print('a2 :' + a2)

                b2 = str(lmlist2[8])
                b2 = b2.split(', ', 1)[1]
                b2 = b2[:b2.find(']')].strip()
                b2 = '(' + b2 + ')'
                # print('b :' + b)

                yA2 = a2.split(', ', 1)[1]
                yA2 = yA2[:yA2.find(')')].strip()
                xA2 = a2.split('(', 1)[1]
                xA2 = xA2[:xA2.find(',')].strip()
                yA2 = int(yA2)
                xA2 = int(xA2)

                yB2 = b2.split(', ', 1)[1]
                yB2 = yB2[:yB2.find(')')].strip()
                xB2 = b2.split('(', 1)[1]
                xB2 = xB2[:xB2.find(',')].strip()
                yB2 = int(yB2)
                xB2 = int(xB2)

                distance2 = math.sqrt(math.pow((xA2 - xB2), 2) + math.pow((yA2 - yB2), 2))
                midpointX2 = int((xA2 + xB2) / 2)
                midpointY2 = int((yA2 + yB2) / 2)
                if (distance2 < 30.0):
                    dotsX2.append(midpointX2)
                    dotsY2.append(midpointY2)
                    points2 = f'@px2 - {midpointX2},py2 - {midpointY2},color2 - {currentcolor}'
                    client.send(points2.encode('utf-8'))
                    if (xB2 > 600 and yB2 > 400):
                        client.send('@reset'.encode('utf-8'))
                        dotsX = []
                        dotsY = []
                        dotsX2 = []
                        dotsY2 = []
                #cv2.line(img, (xB2, yB2), (xA2, yA2), (0, 0, 0), 2)

            yA = a.split(', ', 1)[1]
            yA = yA[:yA.find(')')].strip()
            xA = a.split('(', 1)[1]
            xA = xA[:xA.find(',')].strip()
            yA = int(yA)
            xA = int(xA)

            y = b.split(', ', 1)[1]
            y = y[:y.find(')')].strip()
            x = b.split('(', 1)[1]
            x = x[:x.find(',')].strip()
            y = int(y)
            x = int(x)
            distance = math.sqrt(math.pow((xA - x),2) + math.pow((yA - y),2))
            #print('distance = ' + str(distance))

            midpointX = int((xA + x) / 2)
            midpointY = int((yA + y) / 2)


            #cv2.drawMarker(img, (midpointX , midpointY), (0, 0, 255))
            #cv2.line(img,(x,y),(xA,yA),(255,255,255),2)
            if(distance < 30.0):
                dotsX.append(midpointX)
                dotsY.append(midpointY)
                points1 = f'@px - {midpointX},py - {midpointY},color - {currentcolor}'
                client.send(points1.encode('utf-8'))
                if(x > (width - (width/6)) and y > (height - (height/6))):
                    client.send('@reset'.encode('utf-8'))
                    dotsX = []
                    dotsY = []
                    dotsX2 = []
                    dotsY2 = []



        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        #cv2.putText(img, 'fps: ' + str(int(fps)), (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
        cv2.putText(img, 'time left: ' + str(90 - int(cTime - start)), (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

        for i in range(len(dotsX) - 1):
            cv2.circle(img, (dotsX[i], dotsY[i]), 3, (0, 0, 0), cv2.FILLED)
            distance1 = math.sqrt(math.pow((dotsX[i + 1] - dotsX[i]), 2) + math.pow((dotsY[i + 1] - dotsY[i]), 2))
            if distance1 < 20:
                cv2.line(img, (dotsX[i], dotsY[i]), (dotsX[i+1], dotsY[i+1]), (0, 0, 0), 2)

        for i in range(len(dotsX2) - 1):
            cv2.circle(img, (dotsX2[i], dotsY2[i]), 3, (0, 0, 0), cv2.FILLED)
            distance1 = math.sqrt(math.pow((dotsX2[i + 1] - dotsX2[i]), 2) + math.pow((dotsY2[i + 1] - dotsY2[i]), 2))
            if distance1 < 20:
                cv2.line(img, (dotsX2[i], dotsY2[i]), (dotsX2[i+1], dotsY2[i+1]), (0, 0, 0), 2)

        cv2.putText(img, 'clear', (int(width - (width/8)), int(height - (height/8))), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
        cv2.rectangle(img,(int(width - (width/6)),int(height - (height/6))) ,(width - 1 ,height - 1),(0,0,255),2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
    dotsX = []
    dotsY = []
    dotsX2 = []
    dotsY2 = []

def game(msg):
    global playing,width,height
    msglst = []
    msglst = msg.split('\n')
    Imsg = ""
    #print(msglst)
    for msgg in msglst:
        Imsg = msgg[msgg.find(":") + 1:]
        Imsg.replace('\n', '')
        #print(Imsg)
        if msgg.find("server: #you are drawing") == 0:
            print("drawing")
            playing = True
            thread = threading.Thread(target=trackhands)
            thread.start()
        if msgg.find("server: #you are watching") == 0:
            print("watching")
            playing = True
            threadd = threading.Thread(target=testui)
            threadd.start()
        if (Imsg.find('@px2') == 1):
            msg2 = Imsg[Imsg.find('-') + 1:]
            dotsX2.append(msg2[1:msg2.find(',')])
            dotsY2.append(msg2[msg2.find('-') + 2:msg2.find(',color')])
            color2.append(msg[msg.find('color2 - ') + 9:msg.find('\n')])
        elif (Imsg.find('@px') == 1):
            msg2 = Imsg[Imsg.find('-') + 1:]
            dotsX.append(msg2[1:msg2.find(',')])
            dotsY.append(msg2[msg2.find('-') + 2:msg2.find(',color')])
            color.append(msg[msg.find('color - ') + 8:msg.find('\n')])
        elif (Imsg == " @done"):
            playing = False
            add_message_to_ui("playing = " + str(playing))
        elif (Imsg.find("@width") == 1):
            msg2 = Imsg[Imsg.find('-') + 1:]
            width = msg2[1:msg2.find(',')]
            height = msg2[msg2.find('-') + 2:]
        elif (Imsg.find("@reset") == 1):
            playing = False
            playing = True
            threadd = threading.Thread(target=testui)
            threadd.start()
        elif(Imsg != ''):
            add_message_to_ui(msgg)

def receive_messages():
    while True:
        msg = client.recv(1024).decode('utf-8')
        if not msg:
            break
        game(msg)

def send_message():
    message = message_entry.get()
    if (message.find('@') == 0):
        message = message[1:]
    client.send(message.encode('utf-8'))
    if message == "!exit":
        client.close()
    add_message_to_ui("You: " + message)
    message_entry.delete(0, tk.END)

def run_chat_ui():
    global root, chat_text, message_entry

    root = tk.Tk()
    root.title("Chat UI")

    chat_text = tk.Text(root)
    chat_text.pack()

    message_entry = tk.Entry(root)
    message_entry.pack()

    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack()

    # Add some styling
    root.configure(bg="#F0F0F0")
    chat_text.configure(bg="#FFFFFF", fg="#000000", font=("Helvetica", 12))
    message_entry.configure(bg="#FFFFFF", fg="#000000", font=("Helvetica", 12))
    send_button.configure(bg="#4CAF50", fg="#FFFFFF", font=("Helvetica", 12))

    root.mainloop()

def add_message_to_ui(message):
    chat_text.insert(tk.END, message + "\n")

# Run the chat UI in a separate thread
chat_ui_thread = threading.Thread(target=run_chat_ui)
chat_ui_thread.start()
time.sleep(1)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('10.99.240.127', 5555))
add_message_to_ui("connected to - ('127.0.0.1', 5555)")
thread = threading.Thread(target=receive_messages)
thread.start()
