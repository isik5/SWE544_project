#!/usr/bin/env python

import socket
import threading

s = socket.socket()
# https://stackoverflow.com/questions/4465959/python-errno-98-address-already-in-use
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#host = socket.gethostname()
host = 'localhost'

port = 12345
s.bind((host, port))

s.listen(5)

class ChatSession (threading.Thread):
    def __init__(self, name, csoc):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        #self.nickname = ""
        #self.threadQueue = threadQueue
        #self.screenQueue = screenQueue

    def send(self, data):
        self.csoc.send(data)

    def incoming_parser(self, data):
        if len(data) == 0:
            return

        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.send(response)
            return
        rest = data[4:]

        if data[0:3] == "USR":
            nickname = rest
            # TODO
            self.send("HEL")

        if data[0:3] == "QUI":
            self.send("BYE")
            self.csoc.close()

        if data[0:3] == "LSQ":
            self.send("LSA " + ":".join(self.users))

        # Baglanti testi
        if data[0:3] == "TIC":
            self.send("TOC")

        if data[0:3] == "SAY":
            message = rest
            print "<nick> " + message
            # TODO
            self.send("SOK")

        if data[0:3] == "MSG":
            # TODO
            self.send("MOK")
            #self.send("MNO")

        # TODO: ERL cevap

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            self.incoming_parser(data)

while True:
    csoc, addr = s.accept()
    print 'Got connection from', addr
    csoc.send('Thank you for connecting!')

    # start thread
    cs = ChatSession("ChatSession", csoc)
    cs.start()
