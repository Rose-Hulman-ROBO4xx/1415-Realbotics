import socket
import threading
import json

class TestServer:

    def __init__(self, host='', port = 55333):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)

        self.received = []
        self.connected = False
        self.respondMessage = None

        threading.Thread(target = self.listen).start()

    def command(self, string):
        self.sayRaw({'type':'command', 'data':{'commandData':string}})

    def sayRaw(self, string):
        string = json.dumps(string)
        string = str(len(string)) + '#' + string
        self.conn.sendall(string)

    def close(self):
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()

    def listen(self):

        self.conn, address = self.socket.accept()
        self.connected = True
        if(self.respondMessage):
            self.sayRaw(self.respondMessage)

        state = 'count'
        remainingCount = 0
        countString = ''
        messageString = ''

        while(True):
            data = self.conn.recv(4096)

            if(not data):
                break

            for char in data:
                
                if(state == 'count'):
                    if(char == '#'):
                        remainingCount = int(countString)
                        countString = ''
                        state = 'message'
                    else:
                        countString += char

                elif(state == 'message'):
                   messageString += char
                   remainingCount -= 1
                   
                   if(remainingCount == 0):
                       self.received.append(json.loads(messageString))

                       messageString = ''
                       state = 'count'
