import socket
import sys
import datetime
import random
import string
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S");

def readfile(conn, filename):
    #ack the process
    conn.send(str.encode("OK"))
    print("%s: command:read, filename:%s" %(timestamp(),filename))
    try:
        fd = open(filename, "rb")
    except:
        print ("open %s failed" %filename)
        conn.send(str.encode("no such file, %s" %filename))
        conn.close()
    #send file by block
    while True:

        data = fd.read(1024)
        if data == b"":
            break;
        if cipher == "aes128":
            data= encrypt_data(sk,iv,data)
        elif cipher == "aes256":
            data= encrypt_data(sk,iv,data)

        conn.send(data)

    return;

def writefile(conn,filename):
    #ack the process
    conn.send(str.encode("OK"))
    print("%s: command:write, filename:%s" %(timestamp(),filename))
    try:
        fd = open(filename,"wb")
    except:
        print ("create file error")
        conn.close()
    #write file by block
    while True:
        data = conn.recv(1024)
        if not data:
            break;
        if cipher == "aes128":
            data = decrypt_data(sk,iv,data)
        elif cipher == "aes123":
            data = decrypt_data(sk,iv,data)

        fd.write(data);

    print("%s: status: success" %timestamp())
    conn.close();
    return;

#socket setup
def socket_init(host,port):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host,port))
    server.listen(1)
    print ("Listening on port %d" %port)
    print ("Using sercret key: %s" %secret_key)
    return server;

def Authentication(conn):
    #send challenge
    status = False;
    s= ""
    numlist = []

    n = random.randint(1,100)
    for i in range(0,4):
        s += str(n) + "|"
        numlist.append(n)
        n = random.randint(1,100)
    s+= str(n)
    numlist.append(n)
    expected = hashlib.sha256((str((numlist[0]+numlist[4]-numlist[1])*numlist[2]) + secret_key).encode()).digest()
    conn.send(s.encode())
    #recv the answer
    answer=conn.recv(1024)
    #send status
    if answer == expected:
        status = True
    else:
        pass
    conn.send(str(status).encode())
    return status;
def new_connections(conn):
    data = conn.recv(1024)
    msg = data.decode('utf-8').rstrip()
    #get the cipher type and nonce
    cipher, nonce = msg.split(",")
    #check for cipher compatibility
    sk = secret_key+nonce+"SK"
    iv = secret_key+nonce+"IV"
    if cipher == "aes128" or cipher =="aes256":
        sk = hashlib.sha256(sk.encode("utf-8")).hexdigest()
        iv = hashlib.sha256(iv.encode("utf-8")).hexdigest()
    elif cipher == "null":
        pass
    print ("%s: new connection from %s cipher=%s" %(timestamp(),str(addr),cipher))
    print ("%s: nonce=%s" %(timestamp(), nonce))
    print ("%s: IV=%s" %(timestamp(),iv))
    print ("%s: SK=%s" %(timestamp(),sk))
    return (cipher, sk, iv);

def encrypt_data(sk,iv,data):
    cip = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
    encryptor = cip.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    return ct;

def decrypt_data(sk, iv, ct):
    cip = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
    decryptor = cip.decryptor()
    msg = decryptor.update(ct) +decryptor.finalize()
    return msg;



#===============================================================================

#arguments check
try:
    port = int(sys.argv[1])
    secret_key = sys.argv[2]
except:
    print ("Invalid arguments: server.py [port] [key]")
    sys.exit()

try:
    backend =default_backend()
    s = socket_init('',port)
    while True:
        #accept new connection
        conn,addr = s.accept()
        cipher, sk, iv = new_connections(conn)
        if Authentication(conn):
            #get the command
            data = conn.recv(1024)
            operation,filename = data.decode('utf-8').rstrip().split(',')
            if operation == "write":
                writefile(conn,filename)
            elif operation == "read":
                readfile(conn,filename)
            else:
                conn.send(str.encode("operation not supported!"))
        else:
            print ("%s: Error - Authentication fail" %timestamp())

        conn.close()
        print ("%s: connection with %s ended" %(timestamp(), str(addr)))
except Exception as e:
    print(e)
