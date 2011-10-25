''' Auctioneer is a dumb view; AuctionServer is the controller, also containing
the model, for it'''

from parta import *
import threading
from logger import *

log = Logger("auctioneerlog.txt")

class Auctioneer(Window, threading.Thread):
	def __init__(self, clients):
		Window.__init__(self) # initialize window
		threading.Thread.__init__(self)
		self.clients = clients
		self.curItem = 0
		self.isOver = False
		self.biddingOpen = False
		self.displayUI = True
		self.auctionLock = threading.Lock()

	def run(self):	
		try:
			self.setBottomMessage("Enter Message:")
			self.refresh()

			key = ord("!")

			while self.displayUI:
				if key == 27: # ESC
					self.auctionLock.acquire()
					self.isOver = True
					self.auctionLock.release()
					break
				if key == 14: # ctrl + n
					log.write("Ctrl + n pressed!")
					self.auctionLock.acquire()
					self.biddingOpen = True
					log.write("Bidding Open!")
					self.auctionLock.release()
				if key == 5: # ctrl + e
					log.write("Ctrl + e pressed!")
					self.auctionLock.acquire()
					self.biddingOpen = False
					self.postMessage("Bidding for current item has ended!")
					log.write("Bidding closed!")
					self.auctionLock.release()
				else:
					self.handleKey(key)
				self.refresh()
				key = self.window.getch()
		except:
			self.stop()
	
	def handleKey(self, key):
		Window.handleKey(self, key)
		if self.inputString != "":
			self.postMessage(self.inputString)
			self.inputString = ""

	def halt(self):
		self.displayUI = False
		self.stop()
		
	def postMessage(self, message):
		for client in self.clients:
			client.sendall(message)
		self.addMessage(message)
		Window.refresh(self)

	def isAuctionOver(self):
		return self.isOver
	def biddingIsOpen(self):
		return self.biddingOpen