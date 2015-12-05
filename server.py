#!/usr/bin/env python

import socket

s = socket.socket()
#host = socket.gethostname()
host = 'localhost'

port = 12345
s.bind((host, port))

s.listen(5)

def parser(csocket, data, state):
    data = data.strip()
    if data == None:
        response = "ERR"
        csocket.send(response)
        return 0
    if data[0:3] == "HEL":
        csocket.send("SLT")

while True:
    c, addr = s.accept()
    print 'Got connection from', addr
    c.send('Thank you for connecting!')

    while True:
        data = c.recv(1024)
        parser(c,data, None)

    c.close()
