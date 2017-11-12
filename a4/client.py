import socket
import sys
import random
import string
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


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

def socket_init(host,port):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect((host,port))
    return client;

def nonce():
    random_str = ''.join(random.choices(string.ascii_uppercase+string.digits, k=16))
    return random_str;

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

def uploadfile(conn):
    #send file by block
    while True:

        inputs = sys.stdin.buffer.read(1024)
        if not inputs :
            print("EOF")
            break;
        conn.send(inputs)

    return;

def downloadfile(conn):
    while True:
        inStream= conn.recv(1024)
        if not inStream: break;
        sys.stdout.buffer.write(inStream)

    return;

def encrypt_data(sk,iv,msg):
    cip = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
    encryptor = cip.encryptor()
    ct = encryptor.update(msg.encode()) + encryptor.finalize()
    return ct;

def decrypt_data(sk, iv, ct):
    cip = Cipher(algorithms.AES(sk),modes.CBC(iv), backend = backend)
    decryptor = cip.decryptor()
    msg = decryptor.update(ct) +decryptor.finalize()
    return msg;

#===============================================================================
#setup socket
s = socket_init(hostname,port)
#setup sk,iv
sk = secret_key+nonce()+"SK"
iv = secret_key+nonce()+"IV"
if cipher == "aes128" or cipher =="aes256":
    sk = hashlib.sha256(sk.encode("utf-8")).hexdigest()
    iv = hashlib.sha256(iv.encode("utf-8")).hexdigest()
elif cipher == "null":
    pass
else:
    sys.stderr.write("selected cipher is not supported")
    sys.exit()
#send cipher and nonce
s.send(str.encode(cipher+","+nonce()))
#complete the challenge
if Authentication_challenge(s) == True:
    #request operation
    s.send(str.encode(command+','+filename))
    #getting ack
    data = s.recv(64).decode("utf-8")
    if data == "OK":
        sys.stderr.write(data)
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
