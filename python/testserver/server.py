from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

import time
import threading

class MockSocket(WebSocket):

    def received_message(self, message):
        print('Recieved message: ')
        print(message)

        print 1
        if(message.data == 'getCommands'):
            print 2
            print('Starting command sending')
            print 3
            self.commandThread = threading.Thread(target=self.sendCommands)
            print 4
            self.commandThread.start()
            print 5
        print 6

    def sendCommands(self):
        while True:
            print 'doop!'
            self.send('Look a command')
            time.sleep(3)


server = make_server('', 9000, server_class=WSGIServer,
                     handler_class=WebSocketWSGIRequestHandler,
                     app=WebSocketWSGIApplication(handler_cls=MockSocket))
server.initialize_websockets_manager()
server.serve_forever()
