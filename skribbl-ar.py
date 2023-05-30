import math
import tkinter as tk
import cv2
import mediapipe as mp
import random
import time
import threading
from PIL import Image
import socket

dotsX = [10, 10]
dotsY = [10, 20]
color = ['black', 'red']
dotsX2 = [10, 10]
dotsY2 = [10, 10]
color2 = ['black', 'black']

PREV_DOT = 0
PREV_DOT2 = 0
now = 0
now2 = 0

width = 0
height = 0
playing = False

timer = 90


class showdrawing():
    def __init__(self):
        # print('im in the testui and playing is: ' + str(playing))
        global width
        global height
        while (width == 0):
            time.sleep(0.1)

        self.start = time.time()
        self.root2 = tk.Tk()
        self.root2.title("scribble ar")
        self.label = tk.Label(self.root2)
        self.label.pack()

        self.canvas2 = tk.Canvas(self.root2, width=width, height=height)
        self.canvas2.pack()
        self.root2.after(10, self.add_dot)
        self.root2.mainloop()

    def add_dot(self):
        self.label.config(text="time left: " + str(timer - int(time.time() - self.start)))

        global playing
        global now, now2
        global PREV_DOT, PREV_DOT2
        global dotsX, dotsY, dotsX2, dotsY2, width, height
        if not playing:
            print('exiting')
            self.root2.quit()
            dotsX = []
            dotsY = []
            dotsX2 = []
            dotsY2 = []
            height = 0
            width = 0
            return
        if (now < len(dotsX) - 1):
            now += 1

            x = int(dotsX[now])
            y = int(dotsY[now])

            dot = self.canvas2.create_oval(x, y, x + 3, y + 3, fill=color[now], outline=color[now])
            if PREV_DOT == 0:
                PREV_DOT = dot

            if 'PREV_DOT' in globals():
                x1, y1, _, _ = self.canvas2.coords(PREV_DOT)
                distance = math.sqrt(math.pow((x1 - x), 2) + math.pow((y1 - y), 2))
                if (distance < 30.0):
                    self.canvas2.create_line(x, y, x1, y1, width=4, fill=color[now])

            self.root2.after(10, self.add_dot)
            PREV_DOT = dot
        elif (now2 < len(dotsX2) - 1):
            now2 += 1

            x2 = int(dotsX2[now2])
            y2 = int(dotsY2[now2])

            dot2 = self.canvas2.create_oval(x2, y2, x2 + 3, y2 + 3, fill=color2[now2], outline=color2[now2])
            if PREV_DOT2 == 0:
                PREV_DOT2 = dot2

            if 'PREV_DOT2' in globals():
                x3, y3, _, _ = self.canvas2.coords(PREV_DOT)
                distance = math.sqrt(math.pow((x3 - x2), 2) + math.pow((y3 - y2), 2))
                if (distance < 30.0):
                    self.canvas2.create_line(x2, y2, x3, y3, width=4, fill=color2[now2])

            self.root2.after(10, self.add_dot)
            PREV_DOT2 = dot2
        else:
            # print('dotsx2 is too short - ' + str(dotsX2))
            self.root2.after(10, self.add_dot)


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, modelComplexity=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

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
        if (type(self.results.multi_hand_landmarks) != list):
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
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmlist = detector.findPosition(img)
        lmlist2 = detector.findPosition2(img)

        if len(lmlist) != 0:
            a = str(lmlist[4])
            a = a.split(', ', 1)[1]
            a = a[:a.find(']')].strip()
            a = '(' + a + ')'
            # print('a :' + a)

            b = str(lmlist[8])
            b = b.split(', ', 1)[1]
            b = b[:b.find(']')].strip()
            b = '(' + b + ')'
            # print('b :' + b)

            c = str(lmlist[12])
            c = c.split(', ', 1)[1]
            c = c[:c.find(']')].strip()
            c = '(' + c + ')'
            # print('c :' + c)

            d = str(lmlist[16])
            d = d.split(', ', 1)[1]
            d = d[:d.find(']')].strip()
            d = '(' + d + ')'
            # print('d :' + d)

            e = str(lmlist[20])
            e = e.split(', ', 1)[1]
            e = e[:e.find(']')].strip()
            e = '(' + e + ')'
            # print('e :' + e)

            if (lmlist2 != []):
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
                if distance2 < 30.0:
                    dotsX2.append(midpointX2)
                    dotsY2.append(midpointY2)
                    color2.append(currentcolor)
                    points2 = f'@px2 - {midpointX2},py2 - {midpointY2},color2 - {currentcolor}'
                    client.send(points2.encode('utf-8'))
                    if xB2 < (width / 5) and yB2 < (height / 5):
                        currentcolor = 'black'
                    elif ((width / 5) < xB2 < (width / 5) * 2) and yB2 < (height / 5):
                        currentcolor = 'red'
                    elif ((width / 5) * 2 < xB2 < (width / 5) * 3) and yB2 < (height / 5):
                        currentcolor = 'green'
                    elif ((width / 5) * 3 < xB2 < (width / 5) * 4) and yB2 < (height / 5):
                        currentcolor = 'blue'
                    elif ((width / 5) * 4 < xB2 < width) and yB2 < (height / 5):
                        currentcolor = 'yellow'
                    if xB2 > (width - (width / 6)) and yB2 > (height - (height / 6)):
                        client.send('@reset'.encode('utf-8'))
                        dotsX = []
                        dotsY = []
                        dotsX2 = []
                        dotsY2 = []
                # cv2.line(img, (xB2, yB2), (xA2, yA2), (0, 0, 0), 2)

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
            distance = math.sqrt(math.pow((xA - x), 2) + math.pow((yA - y), 2))
            # print('distance = ' + str(distance))

            midpointX = int((xA + x) / 2)
            midpointY = int((yA + y) / 2)

            # cv2.drawMarker(img, (midpointX , midpointY), (0, 0, 255))
            # cv2.line(img,(x,y),(xA,yA),(255,255,255),2)
            if distance < 30.0:
                dotsX.append(midpointX)
                dotsY.append(midpointY)
                color.append(currentcolor)
                points1 = f'@px - {midpointX},py - {midpointY},color - {currentcolor}'
                client.send(points1.encode('utf-8'))
                # print('x = ' + str(x))
                # print('y = ' + str(y))
                if x < (width / 5) and y < (height / 5):
                    currentcolor = 'black'
                elif ((width / 5) < x < (width / 5) * 2) and y < (height / 5):
                    currentcolor = 'red'
                elif ((width / 5) * 2 < x < (width / 5) * 3) and y < (height / 5):
                    currentcolor = 'green'
                elif ((width / 5) * 3 < x < (width / 5) * 4) and y < (height / 5):
                    currentcolor = 'blue'
                elif ((width / 5) * 4 < x < width) and y < (height / 5):
                    currentcolor = 'yellow'
                if x > (width - (width / 6)) and y > (height - (height / 6)):
                    client.send('@reset'.encode('utf-8'))
                    dotsX = []
                    dotsY = []
                    dotsX2 = []
                    dotsY2 = []

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # cv2.putText(img, 'fps: ' + str(int(fps)), (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)
        cv2.putText(img, 'time left: ' + str(timer - int(cTime - start)), (10, int(width / 5)), cv2.FONT_HERSHEY_PLAIN,1,(0, 0, 0), 2)
        cv2.putText(img, 'color : ' + currentcolor, (10, int(width / 5) + 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

        for i in range(len(dotsX) - 1):
            if color[i] == 'black':
                cv2.circle(img, (dotsX[i], dotsY[i]), 3, (0, 0, 0), cv2.FILLED)
            elif color[i] == 'red':
                cv2.circle(img, (dotsX[i], dotsY[i]), 3, (0, 0, 255), cv2.FILLED)
            elif color[i] == 'green':
                cv2.circle(img, (dotsX[i], dotsY[i]), 3, (0, 255, 0), cv2.FILLED)
            elif color[i] == 'blue':
                cv2.circle(img, (dotsX[i], dotsY[i]), 3, (255, 0, 0), cv2.FILLED)
            elif color[i] == 'yellow':
                cv2.circle(img, (dotsX[i], dotsY[i]), 3, (0, 255, 255), cv2.FILLED)
            distance1 = math.sqrt(math.pow((dotsX[i + 1] - dotsX[i]), 2) + math.pow((dotsY[i + 1] - dotsY[i]), 2))
            if distance1 < 20:
                if color[i] == 'black':
                    cv2.line(img, (dotsX[i], dotsY[i]), (dotsX[i + 1], dotsY[i + 1]), (0, 0, 0), 2)
                elif color[i] == 'red':
                    cv2.line(img, (dotsX[i], dotsY[i]), (dotsX[i + 1], dotsY[i + 1]), (0, 0, 255), 2)
                elif color[i] == 'green':
                    cv2.line(img, (dotsX[i], dotsY[i]), (dotsX[i + 1], dotsY[i + 1]), (0, 255, 0), 2)
                elif color[i] == 'blue':
                    cv2.line(img, (dotsX[i], dotsY[i]), (dotsX[i + 1], dotsY[i + 1]), (255, 0, 0), 2)
                elif color[i] == 'yellow':
                    cv2.line(img, (dotsX[i], dotsY[i]), (dotsX[i + 1], dotsY[i + 1]), (0, 255, 255), 2)

        for i in range(len(dotsX2) - 1):
            if color2[i] == 'black':
                cv2.circle(img, (dotsX2[i], dotsY2[i]), 3, (0, 0, 0), cv2.FILLED)
            elif color2[i] == 'red':
                cv2.circle(img, (dotsX2[i], dotsY2[i]), 3, (0, 0, 255), cv2.FILLED)
            elif color2[i] == 'green':
                cv2.circle(img, (dotsX2[i], dotsY2[i]), 3, (0, 255, 0), cv2.FILLED)
            elif color2[i] == 'blue':
                cv2.circle(img, (dotsX2[i], dotsY2[i]), 3, (255, 0, 0), cv2.FILLED)
            elif color2[i] == 'yellow':
                cv2.circle(img, (dotsX2[i], dotsY2[i]), 3, (0, 255, 255), cv2.FILLED)
            distance1 = math.sqrt(math.pow((dotsX2[i + 1] - dotsX2[i]), 2) + math.pow((dotsY2[i + 1] - dotsY2[i]), 2))
            if distance1 < 20:
                if color2[i] == 'black':
                    cv2.line(img, (dotsX2[i], dotsY2[i]), (dotsX2[i + 1], dotsY2[i + 1]), (0, 0, 0), 2)
                elif color2[i] == 'red':
                    cv2.line(img, (dotsX2[i], dotsY2[i]), (dotsX2[i + 1], dotsY2[i + 1]), (0, 0, 255), 2)
                elif color2[i] == 'green':
                    cv2.line(img, (dotsX2[i], dotsY2[i]), (dotsX2[i + 1], dotsY2[i + 1]), (0, 255, 0), 2)
                elif color2[i] == 'blue':
                    cv2.line(img, (dotsX2[i], dotsY2[i]), (dotsX2[i + 1], dotsY2[i + 1]), (255, 0, 0), 2)
                elif color2[i] == 'yellow':
                    cv2.line(img, (dotsX2[i], dotsY2[i]), (dotsX2[i + 1], dotsY2[i + 1]), (0, 255, 255), 2)

        cv2.putText(img, 'clear', (int(width - (width / 8)), int(height - (height / 8))), cv2.FONT_HERSHEY_PLAIN, 1,
                    (0, 0, 255), 2)
        cv2.rectangle(img, (int(width - (width / 6)), int(height - (height / 6))), (width - 1, height - 1), (0, 0, 255),
                      2)
        cv2.rectangle(img, (0, 0), (int(width / 5), int(height / 5)), (0, 0, 0), 2)
        cv2.rectangle(img, (int(width / 5), 0), (int((width / 5) * 2), int((height / 5))), (0, 0, 255), 2)
        cv2.rectangle(img, (int((width / 5) * 2), 0), (int((width / 5) * 3), int((height / 5))), (0, 255, 0), 2)
        cv2.rectangle(img, (int((width / 5) * 3), 0), (int((width / 5) * 4), int((height / 5))), (255, 0, 0), 2)
        cv2.rectangle(img, (int((width / 5) * 4), 0), (width, int((height / 5))), (0, 255, 255), 2)

        cv2.imshow("Image", img)
        cv2.waitKey(1)
    dotsX = []
    dotsY = []
    dotsX2 = []
    dotsY2 = []


def game(msg):
    global playing, width, height, timer
    msglst = []
    msglst = msg.split('\n')
    Imsg = ""
    # print(msglst)
    for msgg in msglst:
        Imsg = msgg[msgg.find(":") + 1:]
        Imsg.replace('\n', '')
        # print(Imsg)
        if msgg.find("server: #you are drawing") == 0:
            print("drawing")
            playing = True
            thread = threading.Thread(target=trackhands)
            thread.start()
        if msgg.find("server: #you are watching") == 0:
            print("watching")
            playing = True
            threadd = threading.Thread(target=showdrawing)
            threadd.start()
        if Imsg.find('@px2') == 1:
            msg2 = Imsg[Imsg.find('-') + 1:]
            dotsX2.append(msg2[1:msg2.find(',')])
            dotsY2.append(msg2[msg2.find('-') + 2:msg2.find(',color')])
            color2.append(msg[msg.find('color2 - ') + 9:msg.find('\n')])
        elif Imsg.find('@px') == 1:
            msg2 = Imsg[Imsg.find('-') + 1:]
            dotsX.append(msg2[1:msg2.find(',')])
            dotsY.append(msg2[msg2.find('-') + 2:msg2.find(',color')])
            color.append(msg[msg.find('color - ') + 8:msg.find('\n')])
        elif Imsg == " @done":
            playing = False
            add_message_to_ui("playing = " + str(playing))
        elif Imsg.find("@width") == 1:
            msg2 = Imsg[Imsg.find('-') + 1:]
            width = msg2[1:msg2.find(',')]
            height = msg2[msg2.find('-') + 2:]
        elif Imsg.find("@reset") == 1:
            playing = False
            time.sleep(1)
            playing = True
            threadd = threading.Thread(target=showdrawing)
            threadd.start()
        elif Imsg.find("@time") == 1:
            timer = int(Imsg[str(Imsg).find("= ") + 1:])
        elif Imsg == ("@hello!!"):
            print('connected to the server')
        elif Imsg != '':
            add_message_to_ui(msgg)


def receive_messages():
    while True:
        msg = client.recv(1024).decode('utf-8')
        if not msg:
            break
        game(msg)

write_ip = False

def send_message():
    global findingip,client,serverip, ips, choose,ip,write_ip
    message = message_entry.get()
    add_message_to_ui("You: " + message)
    message_entry.delete(0, tk.END)

    if choose:
        if str(message).lower() == 'yes':
            add_message_to_ui("finding servers... (might take some time)")
            findservers()
            choose = False
        elif str(message).lower() == 'no':
            add_message_to_ui('write the server ip:')
            choose = False
            write_ip = True
        else:
            add_message_to_ui('write yes or no only')
    elif write_ip:
        try:
            ip = str(message)
            print(ip)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, 7835))
            if result == 0:
                msg = '!join'
                sock.send(msg.encode('utf-8'))
                data = sock.recv(1024).decode('utf-8')
                if data == "@hello!!":
                    msg = '!exit'
                    sock.send(msg.encode('utf-8'))
                    serverip = ip
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((serverip, 7835))
                    add_message_to_ui(f"connected to - ('{serverip}', 7835), write !ready to start and !help for more commands")
                    thread = threading.Thread(target=receive_messages)
                    thread.start()
                    write_ip = False
        except:
            add_message_to_ui("couldn't connect to the server, check the ip and try again")
    elif findingip:
        if str(message).isdigit():
            if int(message) < len(ips):
                findingip = False
                serverip = ips[int(message) - 1]
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((serverip, 7835))
                add_message_to_ui(f"connected to - ('{serverip}', 7835), write !ready to start and !help for more commands")
                thread = threading.Thread(target=receive_messages)
                thread.start()
            else:
                add_message_to_ui('too big')
        else:
            add_message_to_ui('this is not a int')
    else:
        if message.find('@') == 0:
            message = message[1:]
        if message == "!help":
            add_message_to_ui("commands help:")
            add_message_to_ui("- !ready : start the game")
            add_message_to_ui("- !time ___ : set the time for each turn")
            add_message_to_ui("- !rounds ___ : set the number of rounds")
            add_message_to_ui("- !exit : exit the program")
        else:
            client.send(message.encode('utf-8'))
        if message == "!exit":
            client.close()
            exit()

def findservers():
    global findingip

    ips = find_ips_on_port(7835)
    serverip = '127.0.0.1'
    findingip = False
    print('server ips: ' + str(ips))
    if len(ips) == 0:
        add_message_to_ui("found 0 servers...")
    elif len(ips) == 1:
        serverip = ips[0]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((serverip, 7835))
        add_message_to_ui(f"connected to - ('{serverip}', 7835), write !ready to start")
        thread = threading.Thread(target=receive_messages)
        thread.start()
    else:
        add_message_to_ui('server ips: (write the server number to choose)')
        for i in range(len(ips)):
            add_message_to_ui(f'{i + 1} - {ips[i]}')
        findingip = True

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


def check_ip(ip, port, ips):
    try:
        print('ip - ' + ip)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        if result == 0:
            msg = '!join'
            sock.send(msg.encode('utf-8'))
            data = sock.recv(1024).decode('utf-8')            
            if data == "@hello!!":
                ips.append(ip)
        msg = '!exit'
        sock.send(msg.encode('utf-8'))
        sock.close()
    except:
        pass

def find_ips_on_port(port):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    octets = local_ip.split('.')

    ips = []
    threads = []
    for i in range(1, 256):
        for j in range(1, 256):
            ip = f'{octets[0]}.{octets[1]}.{i}.{j}'
            t = threading.Thread(target=check_ip, args=(ip, port, ips))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    return ips

chat_ui_thread = threading.Thread(target=run_chat_ui)
chat_ui_thread.start()
time.sleep(1)
add_message_to_ui("find all servers? [yes to find servers,no to write the ip yourself]")
choose = True
findingip = False
client = None
ips = []
