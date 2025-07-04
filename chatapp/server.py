import threading
import socket
import random
import math
from Crypto.Util import number
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import time

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

conn = None  # Single client only
chatlog_update_func = None  # Set from GUI

aes_key = None  # Will set after key exchange

def recv_exactly(sock, n):
    """Utility to receive exactly n bytes from a socket."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def recieve():
    global conn
    connected = True
    while connected:
        # Receive header
        msg_length_data = recv_exactly(conn, HEADER)
        if not msg_length_data:
            break

        msg_length = int(msg_length_data.decode(FORMAT).strip())

        # Receive encrypted data
        encrypted_data = recv_exactly(conn, msg_length)
        if not encrypted_data:
            break

        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Decrypt
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        plaintext_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        msg = plaintext_bytes.decode(FORMAT)

        if msg == DISCONNECT_MESSAGE:
            connected = False

        print(f"Client: {msg}")
        if chatlog_update_func:
            chatlog_update_func(f"Client: {msg}\n")

    conn.close()

def send(msg):
    global conn
    message = msg.encode(FORMAT)

    # Generate random IV
    iv = get_random_bytes(16)

    # Encrypt with AES-CBC
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message, AES.block_size))

    # Combine IV and ciphertext
    sending = iv + ciphertext

    # Prepare header
    msg_length = len(sending)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    # Send header and message
    conn.send(send_length)
    conn.send(sending)


def keygen():
    m = number.getStrongPrime(512)
    b = 2
    c = random.randint(2,m-2) #if C becomes (m-1) it will equate to 1
    new = pow(b,c,m)
    return m,b,c,new

def start(on_connect=None):
    print('Starting Server')
    server.listen()
    print(f'Server is Listening on {SERVER}')

    global conn
    conn, addr = server.accept()
    print(f'NEW CONNECTION {addr} established')

    m, b, c, new = keygen()
    params_msg = f"{m},{b}"
    conn.sendall(params_msg.encode(FORMAT))

    time.sleep(2)

    # Receive client's public value
    client_new_data = conn.recv(1024).decode(FORMAT)
    client_new = int(client_new_data)

    # Send our public value
    conn.sendall(str(new).encode(FORMAT))

    # Compute shared key
    shared_key = pow(client_new, c, m)
    print(f"[SERVER] Shared Key Established: {shared_key}")

    # Derive AES key
    global aes_key
    shared_key_bytes = str(shared_key).encode()
    aes_key = hashlib.sha256(shared_key_bytes).digest()

    if on_connect:
        on_connect()

    threading.Thread(target=recieve, daemon=True).start()
