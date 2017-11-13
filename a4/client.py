import socket
import sys
import random
import string
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


#start a socket
def socket_init(host,port):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect((host,port))
    return client;
#do challenge
def Authentication_challenge(conn):
    #get challenge
    challenge = conn.recv(1024).decode("utf-8")
    l = challenge.split("|")
    numlist =[]
    for e in l:
        numlist.append(int(e))
    #generate answer
    answer = hashlib.sha256((str((numlist[0]+numlist[4]-numlist[1])*numlist[2]) + secret_key).encode()).digest()
    #send the answer
    conn.send(answer)
    #get status
    status = conn.recv(1024).decode('utf-8')
    if status == "True":
        status = True
    else:
        status = False
    return status;
#upload to write
def uploadfile(conn):

    if cipher == "aes128" or cipher =="aes256":
        while True:
            #read data
            data = sys.stdin.buffer.read(256)
            if not data:
                print("EOF")
                break;
            #pad_data
            if len(data) < 256:
                data = data_padder(data)
            #encrypt_data
            data = encrypt_data(sk,iv,data)
            #send_data
            conn.send(data)

    elif cipher == "null":
        while True:
            #send file by block
            inStream = sys.stdin.buffer.read(256)
            if not inStream:
                print("EOF")
                break;
            conn.send(inStream)

    return;
#download readed
def downloadfile(conn):

    if cipher == "aes128" or cipher == "aes256":
        inStream= conn.recv(256)
        while True:
            if not inStream: break;
            padded_data = decrypt_data(sk,iv,inStream)
            next_inStream = conn.recv(256)
            data = b''
            if not next_inStream:
                #unpad data if this is last data
                data = data_unpadder(padded_data)
            else: data = padded_data
            sys.stdout.buffer.write(data)
            inStream = next_inStream

    elif cipher == "null":
        while True:
            inStream= conn.recv(256)
            if not inStream: break;
            sys.stdout.buffer.write(inStream)

    return;

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
#generate keys
def key_init ():
    if cipher not in ["aes128","aes256","null"]:
        sys.stderr.write("selected cipher is not supported")
        s.close()
        sys.exit()
    key = secret_key+nonce+"SK"
    vector = secret_key+nonce+"IV"
    sk256 = hashlib.sha256(key.encode("utf-8")).digest()
    sk128 = (hashlib.sha256(key.encode("utf-8")).digest()) [:16]
    iv = (hashlib.sha256(vector.encode("utf-8")).digest())[:16]
    if cipher == "aes128":
        return (sk128,iv)
    elif cipher =="aes256":
        return (sk256,iv)
    else:
        return (0,0)
#===============================================================================
#setting up arg
try:
    command = sys.argv[1]
    filename = sys.argv[2]
    hostname = (sys.argv[3].split(':'))[0]
    port = int((sys.argv[3].split(':'))[1])
    cipher = sys.argv[4]
    secret_key = sys.argv[5]

except:
    print ("Invalid arguments: client.py [command] [filename] [hostname:port] [cipher] [key]")
    sys.exit()

#setup socket
backend =default_backend()
nonce = ''.join(random.choices(string.ascii_uppercase+string.digits, k=16))

s = socket_init(hostname,port)
#send cipher and nonce
s.send(str.encode(cipher+","+nonce))
#setup sk,iv
sk,iv = key_init()
#complete the challenge
if Authentication_challenge(s) == True:
    #request operation
    s.send(str.encode(command+','+filename))
    #getting ack
    data = s.recv(64).decode("utf-8")
    if data == "OK":
        sys.stderr.write(data+"\n")
        if command =="write":
            uploadfile(s)
        elif command =="read":
            downloadfile(s)
    else:
        print(data)
else:
    #decline
    print ("Authentication Fail")

sys.exit()
