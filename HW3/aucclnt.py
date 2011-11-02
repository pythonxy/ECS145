import sys
from parta import *
import socket
from select import select
from logger import *


log = Logger("clientlog.txt")

class AuctionClient(Window):
	def __init__(self, (host, port)):
		Window.__init__(self)
		self.window.nodelay(1)
		self.server = None
		self.connect((host, port))
		
	def handleKey(self, key):
		if key == -1:
			return
		Window.handleKey(self, key)
		if self.inputString != "":
			self.server.sendall(self.inputString)
			self.inputString = ""

	def refresh(self):
		Window.refresh(self)

	def connect(self, (host, port)):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((host, port))

	def run(self):

		try:
			self.setBottomMessage("Enter Bid:")
			self.refresh()

			key = -1

			while True:
				readReady, writeReady, inError = select([self.server], [], [], 0)

				if readReady:
					message = readReady[0].recv(500)
					if message:
						self.addMessage(message)

				if key == 27:
					break
				else:
					self.handleKey(key)
				self.refresh()
				key = self.window.getch()

			
		finally:
			self.stop()

	def stop(self):
		Window.stop(self)
		self.server.close()

if __name__ == "__main__":
	host = sys.argv[1]
	port = int(sys.argv[2])
	client = AuctionClient((host, port))
	client.run()

