import socket
import threading
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 4040))

def listen():
    try:
        while True:
            print sock.recv(512)
    except KeyboardInterrupt:
        return

listenThread = threading.Thread(target=listen)
listenThread.start()

sock.sendall('Greetings!')

while True:
    sock.sendall(raw_input())
