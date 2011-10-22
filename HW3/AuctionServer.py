import sys
import os
import traceback
import socket
import Auctioneer
from select import select
from random import choice

kNumClients = 5
kPort = 6400
kByteMax = 100

def getEmail(client): pass
def reject(client): pass
def postBid(bid, bidder):
	global neer
	global clients
def announceWinner(item, price, winner):
	global neer
	global clients
def emailWinners(winners): pass

# set up and initialize listening socket
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(('', kPort))
listener.listen(kNumClients)

# grab kNumClients clients, request email: THIS BLOCKS UNTIL ALL CLIENT SPOTS ARE FILLED
clients = {}
for i in range(kNumClients):
	(client, addr) = listener.accept()
	clients[client] = getEmail(client)
	client.setblocking(0)

# launch auctioneer window
neer = Auctioneer(clients.keys())

# winner variables initialization
winner = None
winners = fromkeys(clients.values(), []) # takes the form email:list of itemNums
winPrices = {} # takes the form itemNum:winning bid

# while the auctioneer wants to hold the auction
while not neer.isOver():
	winner = bidder = None
	bid = ''

	# while we have clients
	while neer.biddingOpen():
		readReady, writeReady, inError = select(clients.keys(), [], [], 60)

		# if we have bids randomly select one bid from those bids, reject others
		if(readReady):
			bidder = choice(readReady)

			# inform others that they weren't selected
			for other in readReady:
				if other != bidder:
					other.recv(kByteMax) # empty its buffer
					reject(other)
			
			# post the bidder's bid to screens
			bid = bidder.recv(kByteMax)
			postBid(bid, bidder)
	
	if bidder:
		winner = bidder
		winners[ clients[bidder] ] += neer.getCurItem()
		winPrices[neer.getCurItem()] = bid
		
		announceWinner(neer.getCurItem(), bid, winner)
		curItem += 1

# email all the winners
emailWinners(winners, winPrices)

		