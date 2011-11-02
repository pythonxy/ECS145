''' Auctioneer is a dumb view; AuctionServer is the controller, also containing
the model, for it'''

from parta import *
from logger import *

log = Logger("auctioneerlog.txt")

class Auctioneer(Window):
	def __init__(self, clients):
		Window.__init__(self) # initialize window
		self.clients = clients
		self.curItem = 0
		self.isOver = False
		self.biddingOpen = False
		self.setBottomMessage("Enter Message:")
		self.window.nodelay(1)
		self.refresh()

	def run(self):	
		try:
			key = self.window.getch()

			if key == 27: # ESC
				self.isOver = True
				self.biddingOpen = False
			elif key == 14: # ctrl + n
				log.write("Ctrl + n pressed!")
				self.biddingOpen = True
				log.write("Bidding Open!")
			elif key == 5: # ctrl + e
				log.write("Ctrl + e pressed!")
				self.biddingOpen = False
				self.postMessage("Bidding for current item has ended!")
				log.write("Bidding closed!")
			else:
				self.handleKey(key)
				self.refresh()

		except:
			self.stop()
	
	def handleKey(self, key):
		if key == -1:
			return
		Window.handleKey(self, key)
		if self.inputString != "":
			self.postMessage(self.inputString)
			self.inputString = ""

	def postMessage(self, message):
		for client in self.clients:
			client.sendall(message)
		self.addMessage(message)
		Window.refresh(self)

	def isAuctionOver(self):
		return self.isOver
	def biddingIsOpen(self):
		return self.biddingOpen