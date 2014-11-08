from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

import re
import threading

Auth = {'testclient': 'testclienttoken'}

class DeviceServer:

    def __init__(self):

        print('Device server starting')
        self.clients = dict()

        class MockSocket(WebSocket):


            def received_message(self2, message):
                try:
                    parts = re.match(r'^(\w*) (.*)$', message.data)
                    messageType = parts.group(1)
                    messageRest = parts.group(2)
                except Exception as e:
                    self2.close(1008, 'invalid message: ' + message.data)
                    return

                if(messageType == 'identity'):
                    self2.identity = messageRest
                    return self2.register()
                elif(messageType == 'token'):
                    self2.token = messageRest
                    return self2.register()
                else:
                    self2.close(1002, 'invalid message type ' + messageType)
                    return

            def opened(self2):
                self2.identity = None
                self2.token = None
                self2.registered = False
                print('Client connected from ' + str(self2.peer_address))

            def closed(self2, code, reason=None):
                if self2.registered and self2.identity in self.clients:
                    del self.clients[self2.identity]
                print('Client disconnected, code ' + str(code) + ', reason ' + str(reason))

            def register(self2):
                if self2.identity == None:
                    return
                if self2.token == None:
                    return

                if not(self2.identity in Auth):
                    return self2.close(1008, 'No such identity')

                if self2.identity in self.clients:
                    return self2.close(1008, 'That client is already logged in')

                if Auth[self2.identity] != self2.token:
                    return self2.close(1008, 'Invalid token')

                self2.registered = True
                self.clients[self2.identity] = self2

                print('Client ' + self2.identity + ' ready')

        self.server = make_server('', 5581, server_class=WSGIServer,
                handler_class=WebSocketWSGIRequestHandler,
                app = WebSocketWSGIApplication(handler_cls=MockSocket))
        self.server.initialize_websockets_manager()

        def runner():
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                return

        self.runThread = threading.Thread(target=runner)
        self.runThread.start()

server = DeviceServer()
