import socket
import sys
import datetime
import random
import string
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


#get current time
def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S");
#do read operation
def readfile(conn, filename):

    print("%s: command:read, filename:%s" %(timestamp(),filename))
    try:
        fd = open(filename, "rb")
    except:
        print ("%s: open %s failed" %(timestamp(),filename))
        conn.send(str.encode("Error: File %s does not exist" %filename))
        conn.close()
        return;

    #ack the process
    conn.send(str.encode("OK"))
    #send file by block
    while True:
        #read
        data = fd.read(256)

        if data == b"":
            break;
        if cipher == "aes128" or cipher == "aes256":
            #padding
            if len(data) < 256:
                data = data_padder(data)
            #encrypt_data
            data= encrypt_data(sk,iv,data)
        else:
            pass
        #send
        conn.send(data)

    return;
#do write operation
def writefile(conn,filename):

    print("%s: command:write, filename:%s" %(timestamp(),filename))
    try:
        fd = open(filename,"wb")
    except:
        print ("%s: Error: create file %s failed" %(timestamp(),filename))
        conn.send(str.encode("Error: can not create file, %s" %filename))
        conn.close()
        return;

    #ack the process
    conn.send(str.encode("OK"))
    #write file by block
    if cipher == "aes128" or cipher == "aes256":
        inStream = conn.recv(256)
        while True:
            if not inStream: break;
            #decrypt_data
            padded_data = decrypt_data(sk,iv,inStream)
            next_inStream = conn.recv(256)
            data = b''

            if not next_inStream:
                #unpad data if this is last data
                data = data_unpadder(padded_data)
            else: data = padded_data
            #write to file
            fd.write(data)
            inStream = next_inStream
    elif cipher == "null":
        while True:
            data = conn.recv(256)
            if not data: break;
            fd.write(data)



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
#do Authentication
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
#get new connection
def new_connections(conn):
    data = conn.recv(1024)
    msg = data.decode('utf-8').rstrip()
    #get the cipher type and nonce
    cipher, nonce = msg.split(",")
    print ("%s: new connection from %s cipher=%s" %(timestamp(),str(addr),cipher))

    #check for cipher compatibility
    key = secret_key+nonce+"SK"
    vector = secret_key+nonce+"IV"

    sk256 = hashlib.sha256(key.encode("utf-8")).digest()
    sk128 = (hashlib.sha256(key.encode("utf-8")).digest()) [:16]
    iv = (hashlib.sha256(vector.encode("utf-8")).digest())[:16]
    iv_p = (hashlib.sha256(vector.encode("utf-8")).hexdigest()) [:32]
    sk_p = 0
    if cipher == "aes128":
        sk = sk128
        sk_p = (hashlib.sha256(key.encode("utf-8")).hexdigest())[:32]
    elif cipher == "aes256":
        sk = sk256
        sk_p = hashlib.sha256(key.encode("utf-8")).hexdigest()
    elif cipher == "null":
        sk = 0
        iv = 0
        iv_p = 0

    else:
        raise Exception("%s: Error - unsupported cipher" %timestamp())
    print ("%s: nonce=%s" %(timestamp(), nonce))
    print ("%s: IV=%s" %(timestamp(),iv_p))
    print ("%s: SK=%s" %(timestamp(),sk_p))
    return (cipher, sk, iv);

def encrypt_data(sk,iv,data):

    cip = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
    encryptor = cip.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()

    return ct;
def decrypt_data(sk, iv, ct):

    cip = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
    decryptor = cip.decryptor()
    padded_data = decryptor.update(ct) +decryptor.finalize()

    return padded_data;



def data_padder (data):
    padded_data = bytearray(data)
    for x in range(len(data),256):
        padded_data.append(256-len(data))
    result = bytes(padded_data)
    return result;

def data_unpadder(padded_data):
    temp =bytearray(padded_data)
    padding_counts = 0
    padded_value = temp[255]
    for x in range(256-padded_value,256):
        if temp[x] == padded_value:
            padding_counts += 1
        else: break;
    if padding_counts == padded_value:
        del temp[(256-padded_value):]

    data = bytes(temp)
    return data;

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
except Exception as e:
    print(e)

while True:
    try :
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
            raise Exception("%s: Error - Authentication fail" %timestamp())

        conn.close()
        print ("%s: connection with %s ended" %(timestamp(), str(addr)))
    except Exception as e:
        print (e)
        conn.close()
        print ("%s: connection with %s ended" %(timestamp(), str(addr)))
        continue;
