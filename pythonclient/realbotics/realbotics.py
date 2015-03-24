import sys
import socket
import threading
import Queue
import json
import re

WakeInterval = 0.1

class Closed(Exception):
    pass
class AuthFailure(Exception):
    pass

class _JsonSocket:
    """
    This is an implementation of the JSON socket protocol, wherein each
    message is prefixed by the length of the message, then a #. For example: [1,
    2, 3] encodes to "7#[1,2,3]"
    """

    def __init__(self):
        self.msgQueue = Queue.Queue(64)

        self.countString = ''
        self.messageString = ''
        self.remainingCount = 0

        self.state = 'count'

        self.open = False

    def get(self):
        """Gets the next complete message, blocking until it is available"""
        if(self.open or (not self.msgQueue.empty())):
            return json.loads(self.msgQueue.get(True, WakeInterval))
        else: raise Closed()

    def put(self, message):
        """Sends a python object across the socket"""
        if(self.open):
            jsonString = json.dumps(message)
            string = str(len(jsonString)) + '#' + jsonString
            self.socket.sendall(string)
        else: raise Closed()

    def _process(self):
        while True:
            msg = self.socket.recv(4096)

            if not msg:
                break

            for char in msg:
                self._receive(char)

        self.open = False

    def _receive(self, char):
        """State machine for interpereting data from socket"""
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
        """Connect this socket to an address and port"""
        self.socket = socket.create_connection(('localhost', port))
        self.open = True
        self.recvThread = threading.Thread(target=self._process)
        self.recvThread.start()
        self.running = True

    def close(self):
        """Close this socket"""
        self.open = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.running = False
        self.recvThread.join()

class RealboticsSocket:
    """
    A socket for connecting to the realbotics server. This is the lower level
    interface, wherein incoming messages are retrieved by invoking next() on
    this object.
    """

    def __init__(self, address, port):
        self.address = address
        self.port = port

    def connect(self):
        """Open the connection"""
        self.socket = _JsonSocket()
        self.socket.connect(self.address, self.port)

    def authenticate(self, token):
        """Authenticate with the server, using the token as the hardware authentication token"""
        self.socket.put({'type': 'authenticate', 'hardware_token': token})
        r = self._nextAuth(5)
        if(not r):
            self.socket.close()
            raise AuthFailure()

    def say(self, value):
        """Send value to the server"""
        self.socket.put({'type': 'device_response', 'message': value})

    def _nextAuth(self, tries):
        if(tries <= 0):
            return False
        try: 
            a = self.socket.get()
        except Queue.Empty:
            return self._nextAuth(tries - 1)

        if(a['type'] == 'authentication_success'):
            return True
        elif(a['type'] == 'authentication_failure'):
            return False
        else:
            return self._nextAuth(tries - 1)


    def next(self):
        """Returns the next message from the server, blocking until it is available."""
        try:
            a = self.socket.get()
        except Queue.Empty:
            return None

        if(a['type'] == 'command'):
            return a['data']['commandData']
        else:
            return None

    def close(self):
        self.socket.close()

class RealboticsConnection:
    """
    A higher level interface, which uses callbacks to handle incoming messages
    """

    def __init__(self, token, address='localhost', port=3001):
        self.commands = []
        self.commandLock = threading.Lock()
        self.socket = RealboticsSocket(address, port)
        self.token = token
        self._running = False
        self.closed = True
        self.onCloseFunc = None

    def _process_messages(self):

        try:
            while(self._running):
                message = self.socket.next()
                if(message == None):
                    continue
                matchResult = self._match_command(message)
                if(matchResult):
                    self._execute_command(matchResult)
        except Closed:
            self.closed = True
            if(self.onCloseFunc):
                self.onCloseFunc()

    def _match_command(self, message):
        with self.commandLock:
            for command in self.commands:
                match = re.match(command[0], message)
                if match:
                    return (command[1], match)

    def _execute_command(self, matchResult):
        args = list(matchResult[1].groups())
        matchResult[0](*args)

    def on(self, regex, command):
        """
        Register a method command to be executed on any message matcing a
        regular expression. If the regex has groups, they will be passed as
        arguments to the method.
        """
        self.commandLock.acquire(True)
        self.commands.append((regex, command))
        self.commandLock.release()

    def onClose(self, command):
        """
        Register a method command to be executed when the connection is closed.
        """
        self.onCloseFunc = command

    def start(self):
        """
        Open the connection and send the authentication.
        """
        self.socket.connect()
        self.socket.authenticate(self.token)

        self.msgThread = threading.Thread(target=self._process_messages)
        self._running = True
        self.msgThread.start()


    def close(self):
        """Close the connection"""
        self._running = False
        self.socket.close()
        self.msgThread.join()

    def say(self, val):
        """Send a message to the server"""
        self.socket.say(val)


def connect(address, port, token):
    """
    Opens and returns an authenticated RealboticsConnecion
    """
    s = RealboticsConnection(token, address, port)
    s.start()
    return s

