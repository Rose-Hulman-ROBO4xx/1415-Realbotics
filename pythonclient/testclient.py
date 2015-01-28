import realbotics

connection = realbotics.connect('localhost', 3001, 'meow')
while True:
    print connection.next()
