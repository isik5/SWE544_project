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

sessions = {}

class ChatSession (threading.Thread):
    def __init__(self, name, csoc):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        #self.threadQueue = threadQueue
        #self.screenQueue = screenQueue

    def send(self, data):
        self.csoc.send(data)

    def incoming_parser(self, data):
        if len(data) == 0:
            self.csoc.close()
            return True

        if len(data) > 3 and not data[3] == " ":
            response = "ERR"
            self.send(response)
            return
        rest = data[4:]

        if data[0:3] == "USR":
            # TODO: Check/REJ
            if self.nickname != "":
                del sessions[self.nickname]
            self.nickname = rest
            sessions[self.nickname] = self
            self.send("HEL " + self.nickname)

        if data[0:3] == "QUI":
            self.send("BYE")
            self.csoc.close()
            return True

        # Baglanti testi
        if data[0:3] == "TIC":
            self.send("TOC")

        if self.nickname == "":
            self.send("ERL")
            return

        if data[0:3] == "LSQ":
            self.send("LSA " + ":".join(sessions.keys()))

        if data[0:3] == "SAY":
            message = rest
            print "<" + self.nickname + "> " + message
            # TODO: Don't send to self
            for other in sessions.values():
                other.send("SAY " + "<" + self.nickname + "> " + message)
            self.send("SOK")

        if data[0:3] == "MSG":
            dest, msg = rest.split(":", 1)
            print "message: " + dest + " " + msg
            other = sessions.get(dest, None)
            if other == None:
                self.send("MNO")
            else:
                other.send("MSG " + "*" + self.nickname + "* " + msg)
                self.send("MOK")

    def run(self):
        while True:
            data = self.csoc.recv(1024)
            if self.incoming_parser(data):
                break
        if self.nickname != "":
            del sessions[self.nickname]
        print "client disconnected"

while True:
    csoc, addr = s.accept()
    print 'Got connection from', addr
    csoc.send('Thank you for connecting!')

    # start thread
    cs = ChatSession("ChatSession", csoc)
    cs.start()
