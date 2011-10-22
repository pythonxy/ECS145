''' Auctioneer is a dumb view; AuctionServer is the controller, also containing
the model, for it'''

import Window

class Auctioneer(Window):
	def __init__(self, clients):
		super(Auctioneer, self).__init__() # initialize window
		self.clients = clients
		self.curItem = 0
		self.isOver = False
		self.biddingOpen = False
		self.__run()
	
	def __run(self):	
		try:
			self.setBottomMessage("Enter Message:")
			self.refresh()

			key = ord("!")

			while True:
				if key == ord('q'):
					self.isOver = True
					break
				self.__handleKey(key)
				self.refresh()
				key = self.window.getch()
		finally:
			self.stop()
	
	def __handleKey(key): pass
		# if auctioneer enters some special key, a new auction will begin, biddingOpen
		# is set to false. prompting them to announce the new item
		# should there be one
		
	def __postMessage(message): pass
		# this will be called upon KEY_ENTER to send all clients the message
	def getCurItem:
		return self.curItem
	def isOver():
		return self.isOver
	def biddingOpen():
		return self.biddingOpen