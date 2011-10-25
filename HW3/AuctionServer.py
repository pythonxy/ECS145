import sys
import os
import traceback
import socket
from Auctioneer import *
from select import select
from random import choice
from logger import *
import traceback


log = Logger("serverlog.txt")

kNumClients = 1
kPort = 64000
kByteMax = 100

def getEmail(client):
	global neer
	global clients
	client.sendall("Enter your email please.")
	return client.recv(kByteMax)

def reject(client): 
	client.sendall("Your bid has been rejected")

def postBid(bid, bidder):
	global neer
	global clients
	curBid = int(bid)
	neer.postMessage(clients[bidder] + ' ' + bid)

def announceWinner(item, price, winner):
	global neer
	global clients
	announcement = 'Client ' + clients[winner] + ' won item ' + str(item) + ' at price ' + str(price)
	neer.postMessage(announcement)

def emailWinners(winners): pass

def parseBid(bidStr):
	(item, bid) = bidStr.split(" ")
	return (item, bid)

def checkBid(bidPair):
	global curItem
	global curBid
	(client, bidStr) = bidPair
	log.write(bidStr)
	(item, bid) = parseBid(bidStr)
	if int(bid) <= curBid:
		return False
	if int(item) != curItem:
		return False
	return True

neer = None
clients = None
# set up and initialize listening socket
try:
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
	log.write("Spawning Auctioneer")
	neer = Auctioneer(clients.keys())
	neer.start()
	log.write("Auctioneer started")

	# winner variables initialization
	winner = None
	winners = dict.fromkeys(clients.values(), []) # takes the form email:list of itemNums
	winPrices = {} # takes the form itemNum:winning bid

	# while the auctioneer wants to hold the auction

	neer.auctionLock.acquire()
	curItem = 0

	while not neer.isAuctionOver():
		try:
			neer.auctionLock.release()
		except Exception:
			pass
		winner = bidder = None
		bid = ''
		curBid = 0

		# while we have clients
		neer.auctionLock.acquire()
		loopItem = -1
		while neer.biddingIsOpen():
			neer.auctionLock.release()

			if loopItem != curItem:
				neer.postMessage("Now bidding on item: " + str(curItem))
				loopItem = curItem

			readReady, writeReady, inError = select(clients.keys(), [], [], 1)
			log.write("after select")

			# get bids from all clients
			bidPairs = []
			for readClient in readReady:
				bidPairs.append((readClient, readClient.recv(kByteMax)))
				log.write(clients[bidPairs[0][0]] + " bid " + bidPairs[0][1])

			# if we have bids randomly select one bid from those bids, reject others
			if(readReady):
				validBids = filter(checkBid, bidPairs)
				if validBids:
					(bidder, bidStr) = choice(validBids)
					readReady.remove(bidder)

					log.write("Current high bidder " + str(clients[bidder]))

					# post the bidder's bid to screens
					(item, bid) = parseBid(bidStr) 
					postBid(bid, bidder)

				# inform others that they weren't selected
				map(reject, readReady)
				
			neer.auctionLock.acquire()
		try:
			neer.auctionLock.release()
		except:
			pass

		if bidder:
			winner = bidder
			winners[ clients[bidder] ].append(curItem)

			winPrices[curItem] = bid
			
			announceWinner(curItem, bid, winner)
			curItem += 1

		neer.auctionLock.acquire()
	# email all the winners
	emailWinners(winners, winPrices)

	try:
		neer.auctionLock.release()
	except:
		pass
	neer.postMessage("That's all for today!")

except:
	log.write("Hit an exception")
	traceback.print_exc(file = open("serverexception.txt", 'a'))
finally:
	if neer != None:
		neer.displayUI = False
	for client in clients.keys():
		client.close()
	listener.close()