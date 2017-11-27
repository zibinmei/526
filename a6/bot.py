import sys
import socket



# argv check
try:
    hostname= sys.argv[1]
    port = sys.argv[2]
    channel = sys.argv[3]
    sphrase = sys.argv[4]
except:
    print("invalid arguments: python3 bot.py <hostname> <port> <channel> <secret-phrase>")
    sys.exit()

def connect:
    global irc
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((hostname, port))
    return
