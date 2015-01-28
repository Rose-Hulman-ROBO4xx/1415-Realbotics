import sys
import socket
import threading
import Queue
import json

class _JsonSocket:

    def __init__(self):
        self.msgQueue = Queue.Queue(64)

        self.countString = ''
        self.messageString = ''
        self.remainingCount = 0

        self.state = 'count'

    def get(self):
        return json.loads(self.msgQueue.get())

    def put(self, message):
        jsonString = json.dumps(message)
        string = str(len(jsonString)) + '#' + jsonString
        self.socket.sendall(string)

    def _process(self):
        while True:
            msg = self.socket.recv(4096)

            if not msg:
                break

            for char in msg:
                self._receive(char)

    def _receive(self, char):
        if(self.state == 'count'):
            if(char == '#'):
                self.remainingCount = int(self.countString)
                self.countString = ''
                self.state = 'message'
            else:
                self.countString += char
        elif(self.state == 'message'):
            self.messageString += char
            self.remainingCount -= 1

            if(self.remainingCount == 0):
                self.msgQueue.put(self.messageString)

                self.messageString = ''
                self.state = 'count'    


    def connect(self, address, port):
        self.socket = socket.create_connection(('localhost', 3001))
        self.recvThread = threading.Thread(target=self._process)
        self.recvThread.start()

class RealboticsSocket:

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def connect(self):
        self.socket = _JsonSocket()
        self.socket.connect(self.address, self.port)

    def authenticate(self, token):
        self.socket.put({'type': 'authenticate', 'hardware_token': token})

    def next(self):
        return self.socket.get()

def connect(address, port, token):
    s = RealboticsSocket(address, port)
    s.connect()
    s.authenticate(token)
    return s

