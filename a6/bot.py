import sys
import socket
import random


# argv check
try:
    hostname= sys.argv[1]
    port = sys.argv[2]
    channel = sys.argv[3]
    sphrase = sys.argv[4]
except:
    print("invalid arguments: python3 bot.py <hostname> <port> <channel> <secret-phrase>")
    sys.exit()




def connect():
    botnum = str(random.random*99999)
    irc.connect((hostname, port))
    msg = "NICK bot" + botnum
    irc.send(msg.encode())
    msg = "USER bot * * : bot " + botnum
    irc.send(msg.encode())
    indata = irc.recv(1024)
    print(indata)
    return

def ping:
    msg = "PING"
    irc.send(msg.encode())
    return



# main=========================================================================

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
