from parta import *
import threading
import socket
from select import select
from logger import *

class AuctionListener(threading.Thread):
	def __init__(self, server, window):
		threading.Thread.__init__(self)
		self.auction = True
		self.server = server
		self.window = window
		print type(self.window)
		if isinstance(self.window, Window):
			print "IT's a window!"

	def run(self):
		while self.auction:
			readReady, writeReady, inError = select([self.server], [], [], 60)
			if readReady:
				message = readReady[0].recv(500)
				if message:
					self.window.addMessage(message)
					self.window.refresh()
	def halt(self):
		self.auction = False

class AuctionClient(Window):
	def __init__(self, (host, port)):
		self.windowLock = threading.Lock()
		Window.__init__(self)
		self.server = None
		self.connect((host, port))
		self.listener = AuctionListener(self.server, self)

	def handleKey(self, key):
		Window.handleKey(self, key)
		if self.inputString != "":
			self.server.sendall(self.inputString)
			self.inputString = ""

	def refresh(self):
		self.windowLock.acquire()
		Window.refresh(self)
		self.windowLock.release()

	def connect(self, (host, port)):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((host, port))

	def run(self):
		self.listener.start()
		try:
			self.setBottomMessage("Enter Bid:")
			self.refresh()

			key = ord("!")

			while True:
				if key == 27:
					break
				self.handleKey(key)
				self.refresh()
				key = self.window.getch()
			
		finally:
			self.stop()

	def stop(self):
		Window.stop(self)
		self.server.close()
		self.listener.halt()

if __name__ == "__main__":
	#host = sys.argv[1]
	#port = sys.argv[2]
	host = "127.0.0.1"
	port = 64000
	client = AuctionClient((host, port))
	client.run()

