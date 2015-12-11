import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time

class ReadThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue, screenQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.nickname = ""
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

    def show(self, data):
        screenQueue.put(data)
    def showInfo(self, data):
        self.show("-Server- " + data)

    def incoming_parser(self, data):
        if len(data) == 0:
            return

        if len(data) > 3 and not data[3] == " ":
            print "Error in server message"
            print data
            return
        rest = data[4:]

        if data[0:3] == "HEL":
            self.nickname = rest
            self.showInfo("Registered as " + self.nickname)

        if data[0:3] == "BYE":
            # TODO
            self.csoc.close()
            return True

        if data[0:3] == "ERL":
            self.showInfo("Error: Must register nick first")
            pass

        if data[0:3] == "MSG":
            # TODO
            print "<<nick>> " + rest

        if data[0:3] == "SAY":
            self.show(rest)

        if data[0:3] == "LSA":
            splitted = rest.split(":")
            msg = "Registered nicks: "
            for i in splitted:
                msg += i + ","
                msg = msg[:-1]
            # TODO
            self.showInfo(msg)
            #self.app.cprint(msg)
            print msg

    def run(self):
        while True:
            try:
                data = self.csoc.recv(1024)
                if self.incoming_parser(data):
                    break
            except socket.error:
                # TODO: Report error?
                self.csoc.close()
                break

class WriteThread (threading.Thread):
    def __init__(self, name, csoc, threadQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.threadQueue = threadQueue

    def run(self):
        while True:
            queue_message = self.threadQueue.get()
            print queue_message
            if queue_message == None:
                break
            try:
                # TODO: Send newline
                sent = self.csoc.send(queue_message)
                print sent
            except socket.error:
                self.csoc.close()
                break

class ClientDialog(QDialog):
    ''' An example application for PyQt. Instantiate
    and call the run method to run. '''
    def __init__(self, threadQueue, screenQueue):
        self.threadQueue = threadQueue
        self.screenQueue = screenQueue

        # create a Qt application --- every PyQt app needs one
        self.qt_app = QApplication(sys.argv)

        # Call the parent constructor on the current object
        QDialog.__init__(self, None)

        # Set up the window
        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500, 200)
        self.resize(640, 480)

        # Add a vertical layout
        self.vbox = QVBoxLayout()
        self.vbox.setGeometry(QRect(10, 10, 621, 461))

        # Add a horizontal layout
        self.hbox = QHBoxLayout()

        # The sender textbox
        self.sender = QLineEdit("", self)

        # The channel region
        self.channel = QTextBrowser()
        self.channel.setMinimumSize(QSize(480, 0))

        # The send button
        self.send_button = QPushButton('&Send')

        # The users' section
        self.userList = QListView()

        # Connect the Go button to its callback
        self.send_button.clicked.connect(self.outgoing_parser)

        # Add the controls to the vertical layout
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)
        self.hbox.addWidget(self.channel)
        self.hbox.addWidget(self.userList)

        # start timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateChannelWindow)
        # update every 10 ms
        self.timer.start(1000)

        # Use the vertical layout for the current window
        self.setLayout(self.vbox)

    def cprint(self, data):
        # TODO
        self.channel.append(data)

    def updateChannelWindow(self):
        if self.screenQueue.qsize() > 0:
            queue_message = self.screenQueue.get()
            # TODO
            self.channel.append(queue_message)

    def outgoing_parser(self):
        data = self.sender.text()
        data = str(data)
        if len(data) == 0:
            return
        if data[0] == "/":
            command, rest = data[1:].split(None, 1)
            if command == "nick":
                self.threadQueue.put(str("USR " + rest))
            elif command == "list":
                pass
            elif command == "quit":
                pass
            elif command == "msg":
                dest, msg = rest.split(None, 1)
                self.threadQueue.put(str("MSG " + ":".join((dest, msg))))
            else:
                self.cprint("Local: Command Error.")
        else:
            self.threadQueue.put(str("SAY " + data))
        self.sender.clear()

    def run(self):
        ''' Run the app and show the main form. '''
        self.show()
        self.qt_app.exec_()

# connect to the server
s = None
s = socket.socket()
host = sys.argv[1]
port = int(sys.argv[2])
s.connect((host,port))

sendQueue = Queue.Queue()
screenQueue = Queue.Queue()

app = ClientDialog(sendQueue, screenQueue)

# start threads
rt = ReadThread("ReadThread", s, sendQueue, screenQueue)
rt.start()

wt = WriteThread("WriteThread", s, sendQueue)
wt.start()

app.run()

sendQueue.put("QUI")
sendQueue.put(None)
wt.join()
s.close()
rt.join()
