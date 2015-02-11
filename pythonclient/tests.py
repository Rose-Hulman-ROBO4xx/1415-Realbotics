import unittest
import testserver
import realbotics
import time

global globalPort
globalPort = 26055

class Tests(unittest.TestCase):

    def setUp(self):
        self.address = 'localhost'
        self.port = globalPort
        global globalPort
        globalPort += 1
        self.token = 'some_hardware_token'
        self.server = testserver.TestServer(self.address, self.port)
        self.server.respondMessage = {'type':'authentication_success'}
        self.client = None

    def tearDown(self):
        if(self.client):
            self.client.close()

    def testConnection(self):
        self.assertFalse(self.server.connected)
        self.client = realbotics.connect(self.address, self.port, self.token)
        time.sleep(0.2)
        self.assertTrue(self.server.connected)

    def testAuth(self):
        self.client = realbotics.connect(self.address, self.port, self.token)
        time.sleep(0.2)
        self.assertEqual({"type":"authenticate", "hardware_token":self.token}, self.server.received[0])

    def testAuthFailed(self):
        self.server.respondMessage = {'type':'authentication_failure', 'reason':'no reason'}
        failed = False
        try:
            self.client = realbotics.connect(self.address, self.port, self.token)
            self.assertFalse(True)
        except realbotics.AuthFailure:
            pass

    def testCallback(self):
        exp = []
        self.client = realbotics.connect(self.address, self.port, self.token)
        def lam(v = exp):
            v.append(1)
        self.client.on('meowCommand', lam)
        time.sleep(0.2)
        self.server.command('meowCommand')
        time.sleep(0.2)
        self.assertEquals(exp, [1])

    def testCorrectCallback(self):
        exp = []
        self.client = realbotics.connect(self.address, self.port, self.token)
        def lam(v = exp):
            v.append(1)
        self.client.on('meowCommand', lam)
        time.sleep(0.2)
        self.server.command('otherCommand')
        time.sleep(0.2)
        self.assertEquals(exp, [])

    def testParameterCallback(self):
        exp = []
        self.client = realbotics.connect(self.address, self.port, self.token)
        def lam(x, v=exp):
            v.append(int(x))
        self.client.on('meowCommand:(\d*)', lam)
        time.sleep(0.2)
        self.server.command('meowCommand:17')
        time.sleep(0.2)
        self.assertEquals(exp, [17])

    def testCloseCallback(self):
        exp = []
        self.client = realbotics.connect(self.address, self.port, self.token)
        def lam(v=exp):
            v.append(1)
        self.client.onClose(lam)
        time.sleep(0.2)
        self.server.close()
        time.sleep(0.2)
        self.assertEquals(exp, [1])

if __name__ == '__main__':
    unittest.main()
