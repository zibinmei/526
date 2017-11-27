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
        botnum = str(random.randint(0,999999))
        irc.connect((hostname, port))
        msg = "NICK bot" + botnum + "\r\n"
        irc.send(msg.encode())
        msg = "USER bot * * : bot " + botnum +"\r\n"
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

def joinChannel(name):
    # join channel
    msg = "JOIN #" +name+" \r\n"
    irc.send(msg.encode())
    indata = irc.recv(1024)
    inmsg = indata.decode("utf-8").split("\r\n")
    for s in inmsg:
        print(s)
    if inmsg[0].split()[1] == "JOIN":
        print("connected")
        return True
    return False
#handles Ping msg
def ping(pingmsg):
    msg = "PONG "+pingmsg+"\r\n"
    irc.send(msg.encode())
    return


# use the listen to chat
def listen():
    while True:
        indata = irc.recv(1024)
        inmsg = indata.decode("utf-8").split()
        print(inmsg)

        if inmsg[0] == sphrase:
            print ("serving master!")
        else:
            pass
    return

# main=========================================================================

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
connect()
listen()
