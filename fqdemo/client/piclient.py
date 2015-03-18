import time

from ws4py.client.threadedclient import WebSocketClient
import RPi.GPIO as io

io.setmode(io.BCM)
io.setup(16, io.OUT)

class DummyClient(WebSocketClient):
    def opened(self):
        self.send('identity testclient')
        self.send('token testclienttoken')

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
	if(m.data == 'on'):
		io.output(16, 1)
	elif(m.data == 'off'):
		io.output(16, 0)
        print m

if __name__ == '__main__':
    try:
        ws = DummyClient('ws://192.168.0.110:5581/', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
	io.cleanup()
