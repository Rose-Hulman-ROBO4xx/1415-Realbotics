import sys
import socket
import threading
import Queue
import json
import re

WakeInterval = 0.1

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

    def close():
        raise Exception()

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

    def close():
        raise Exception()

class RealboticsConnection:

    def __init__(self, address='localhost', port=3001):
        self.commands = []
        self.commandLock = threading.Lock()
        self.socket = RealboticsSocket(address, port)
        self._running = False

    def _proccess_messages(self):
        while(True):
            message = self.socket.next()
            command = self._matchCommand(message)
            self._execute_command(message, command)

    def _matchCommand(message):
        with self.commandLock:
            for command in self.commands:
                if re.match(command[0], message):
                    return command[1]

    def _execute_command(message, command):
        command()

    def on(self, regex, command):
        self.commandLock.acquire(True)
        self.commands.append((regex, command))
        self.commandLock.release()

    def start():
        self.msgThread - threading.Thread(target=self._process_messages)
        self._running = True
        self.msgThread.start()

    def stop():
        self._running = False
        self.socket.close()
        self.msgThread.join()






def connect(address, port, token):
    s = RealboticsSocket(address, port)
    s.connect()
    s.authenticate(token)
    return s

