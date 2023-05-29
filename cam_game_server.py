import socket
import threading
import time
import random
words = ["alligator","america"",""angle"",""ant"",""applause"",""apple"",""arch","arm","army","artist","avocado","baby","backbone","bag","baker","ball","band","baseball","basin","basket","bath","bathroom","battery","bed","bedbug","bee","beehive","bell","berry","bicycle","bird","birthday cake","birthday","blade","bleach","board","boat","bomb","bone","bonnet","book","boot","bottle","bow tie","box","boy","brain","brake","branch","brick","bridge","bruise","brush","bucket","bulb","button","cabin","cake","camera","card","cardboard","carriage","cart","cat","ceiling","chain","chalk","chameleon","charger","cheerleader","cheese","chef","chess","chime","chin","church","circle","circus","cliff","cloak","clock","cloud","coach","coal","coat","collar","comb","comedian","computer","convertible","cord","cow","cowboy","cruise","crust","cup","cupcake","curtain","cushion","darts","deep","dent","dentist","diving","dog","doghouse","door","doormat","drain","drawer","dream","dress","drip","drop","dust","ear","egg","electricity","engine","extension cord","eye","face","farm","feather","finger","firefighter","fireman","fish","fizz","flag","flagpole","floor","flute","fly","fog","foot","fork","fowl","frame","french fries","frog","garbage","garden","garfield","gate","giant","girl","glove","goat","goblin","golden retriever","gun","hair dryer","hair","hammer","hand","handle","hat","head","headphones","heart","hockey","hook","hopscotch","horn","horse","hospital","hot dog","hot tub","house","houseboat","hurdle","internet","island","jewel","joke","kettle","key","knee","kneel","knife","knight","knot","koala","lace","lap","lawnmower","leaf","leak","leg","light bulb","lighthouse","line","lip","lock","mailman","map","mascot","match","mattress","money","monkey","moon","mouth","muscle","mushroom","music","nail","nature","neck","needle","neet","nerve","net","newspaper","nightmare","nose","nut","oar","office","orange","outside","oven","owl","pajamas","parcel","park","password","peach","pen","pencil","pharmacist","photograph","picnic","picture","pig","pilot","pin","pineapple","ping pong","pinwheel","pipe","pirate","plane","plank","plate","plough","pocket","pool","popsicle","post office","pot","potato","prison","pump","puppet","purse","queen","quilt","raft","rail","raincoat","rat","ray","receipt","ring","rod","roof","root","rug","safe","sail","salmon","salt and pepper","sandbox","scale","school","scissors","screw","season","seed","shallow","shampoo","sheep","sheets","shelf","ship","shirt","shoe","shrink","skate","ski","skin","skirt","sleep","snake","sneeze","snowball","sock","song","spade","speakers","sponge","spoon","spring","sprinkler","square","stamp","star","state","station","stem","stick","stingray","stocking","stomach","store","street","suitcase","sun","sunburn","sushi","swamp","sweater","table","tail","teapot","thief","think","thread","throat","thumb","ticket","time machine","tiptoe","toe","tongue","tooth","town","train","tray","treasure","tree","trip","trousers","turtle","tusk","tv","umbrella","violin","wall","watch","watering can","wax","wedding dress","wheel","whip","whistle","wig","window","wing","wire","worm","yardstick","zoo"]
allAddres = []
ready = []
clients = []
playing = False
points = []
currect = []
currentword = ''
timer = 0
def handle_client(conn, addr):
    global timer, currentword,currect,points,playing,ready,allAddres
    allAddres.append(addr)
    ready.append(False)
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        msg = conn.recv(1024).decode('utf-8')
        if not msg:
            break
        print(f"{addr} : {msg}")
        count = 0
        if(msg == "!test"):
            broadcast("#you are watching",None,"server")
            broadcast("@width - 500,height - 600", None , "server")
            broadcast("@px - 105,py - 405,color - red", None , "server")
            broadcast("@px2 - 200,py2 - 200,color2 - green", None , "server")
            #broadcast("@done", None , "server")
        if(playing == True):
            print("playing is true")
            if(msg == currentword):
                broadcast(str(addr) + " got the word!", None, 'server')
                for i in range(len(allAddres)):
                    if(allAddres[i] == addr):
                        points[i] += 50 * timer
                        currect[i] == True
                        if currect.index(False) == -1:
                            timer = 0
        if(msg == "!ready"):
            for i in allAddres:
                if(i == addr):
                    broadcast(f"{i} is ready", conn, addr)
                    print(f"player {count} is ready - {i}")
                    ready[count] = True
                    readycount = 0
                    for i in ready:
                        if(i == True):
                            readycount += 1
                    broadcast(f"{readycount}/{len(ready)} are ready", None, "server")
                    if(readycount >= len(ready)):
                        broadcast(f"starting game!", None, "server")
                        thread = threading.Thread(target=game)
                        thread.start()
                count += 1
        else: 
            broadcast(msg, conn, addr)
    conn.close()

def game():
    global timer, points, currect,currentword,words,playing
    for i in range(len(clients)):
        points.append(0)
        currect.append(False)
    playing = True
    for i in range(len(clients)):
        currentword = words[random.randint(0,len(words)-1)]
        print(str(clients[i]) + " is drawing")
        sendto(("#you are drawing the word : " + currentword),clients[i])
        broadcast("#you are watching",clients[i],"server")
        currect[i] = True
        endtime = int(time.time()) + 90
        timer = endtime - int(time.time())
        while timer > 1:
            timer = endtime - int(time.time())
            time.sleep(1)
        broadcast("@done",None,"server")
        
    
def broadcast(msg, conn, addr):
    for client in clients:
        if client != conn:
            sending = f"{addr}: {msg}\n"
            client.send(sending.encode('utf-8'))

def sendto(msg, addr):    
    sending = f"server: {msg}"
    addr.send(sending.encode('utf-8'))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('10.99.240.127', 5555))
server.listen()
print("[RUNNING] Server is running")
while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()