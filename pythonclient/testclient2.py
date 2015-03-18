import realbotics
import time

connection = realbotics.connect('localhost', 3001, 'meeeeow')

def p(x):
    print x

connection.on(r'(.*)', p)

try:
    while(True):
        time.sleep(1)
except KeyboardInterrupt:
    connection.close()

