import socket
import time
import threading
import random
from Crypto.Util import number
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib


HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chatlog_update_func = None  # Set from GUI

def getkeys():
    params_data = client.recv(1024).decode(FORMAT)
    m, b = map(int, params_data.split(','))

    c = random.randint(2,m-2)

    new = pow(b,c,m)

    client.sendall(str(new).encode(FORMAT))

    # Receive server's public value
    server_new_data = client.recv(1024).decode(FORMAT)
    server_new = int(server_new_data)

    # Compute shared key
    global shared_key
    shared_key = pow(server_new, c, m)
    print(f"[CLIENT] Shared Key Established: {shared_key}")

    global aes_key
    shared_key_bytes = str(shared_key).encode()
    aes_key = hashlib.sha256(shared_key_bytes).digest()  # 32 bytes



def connect(on_connected=None):
    i = 0
    while i < 15:
        try:
            client.connect(ADDR)
            getkeys()
            print("\n Connected Successfully!")

            if on_connected:
                on_connected()

            threading.Thread(target=recieve, daemon=True).start()
            return
        except ConnectionRefusedError:
            print("Searching for Host...")
            i += 1
            time.sleep(5)
    else:
        print("No Host Found")


def send(msg):

    message = msg.encode(FORMAT)
    iv = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message, AES.block_size))

    sending = iv + ciphertext
    
    msg_length = len(sending)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(sending)

def recv_exactly(sock, n):
    """recieving exact bytes """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recieve():
    connected = True
    while connected:
        # Receive header
        msg_length_data = recv_exactly(client, HEADER)
        if not msg_length_data:
            break

        msg_length = int(msg_length_data.decode(FORMAT).strip())

        # Receive the iv + ciphertext
        encrypted_data = recv_exactly(client, msg_length)
        if not encrypted_data:
            break

        # Extract IV and ciphertext
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Decrypt
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        plaintext_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        msg = plaintext_bytes.decode(FORMAT)

        # Check for disconnect message
        if msg == DISCONNECT_MESSAGE:
            connected = False

        print(f"Server: {msg}")
        if chatlog_update_func:
            chatlog_update_func(f"Server: {msg}\n")

    client.close()
