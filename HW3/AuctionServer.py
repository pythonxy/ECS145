import sys
import traceback
import socket
from Auctioneer import *
from select import select
from random import choice
from logger import *
import subprocess, os
import smtplib
from email.mime.text import MIMEText

log = Logger("serverlog.txt")


def getNumClients(filename):
	clientList = open(filename, "r")
	text = clientList.readlines()
	return len(text) 

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
	global curBid
	curBid = int(bid)
	neer.postMessage(clients[bidder] + ' ' + bid)

def announceWinner(item, price, winner):
	global neer
	global clients
	announcement = 'Client ' + clients[winner] + ' won item ' + str(item) + ' at price ' + str(price)
	neer.postMessage(announcement)

def emailWinners(winners, prices):
	s = smtplib.SMTP("smtp.gmail.com", 587)
	for name in winners.keys():
		bill = "Congratulations, you won: "
		items = []
		for item in winners[name]:
			items.append(str(item) + " " + str(prices[item]))
		body = bill + "\n" + "\n".join(items)

		msg = MIMEText(body)
		msg["Subject"] = "Your auction results"
		msg["From"] = "ecsmailserver145@gmail.com"
		msg["To"] = name
		s.ehlo()
		s.starttls()
		s.login("ecsmailserver145", "moneymoneymoney")
		s.sendmail("ecsmailserver145@gmail.com", [name], msg.as_string())
	s.quit()


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



kNumClients = getNumClients(sys.argv[1])
kPort = int(sys.argv[2])
kByteMax = 100

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
	log.write("Auctioneer started")

	# winner variables initialization
	winner = None
	winners = dict.fromkeys(clients.values(), []) # takes the form email:list of itemNums
	winPrices = {} # takes the form itemNum:winning bid


	curItem = 0

	# while the auctioneer wants to hold the auction
	while not neer.isAuctionOver():
		neer.run()
		winner = bidder = None
		bid = ''
		curBid = 0

		# while we have clients
		loopItem = -1
		while neer.biddingIsOpen():
			neer.run()

			if loopItem != curItem:
				neer.postMessage("Now bidding on item: " + str(curItem))
				loopItem = curItem

			readReady, writeReady, inError = select(clients.keys(), [], [], 0)

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

					log.write("Current high bidder " + str(clients[bidder]))

					# post the bidder's bid to screens
					(item, bid) = parseBid(bidStr) 

					neer.run()
					if neer.biddingIsOpen() and not neer.isAuctionOver():
						postBid(bid, bidder)
						readReady.remove(bidder)
					else:
						bidder = None
						
				# inform others that they weren't selected
				map(reject, readReady)
		#End bidding round
						
		if bidder:
			winner = bidder
			winners[ clients[bidder] ].append(curItem)

			winPrices[curItem] = bid
			
			announceWinner(curItem, bid, winner)
			curItem += 1
	#End entire auction

	# email all the winners
	log.write(str(winPrices))
	if winPrices:
		emailWinners(winners, winPrices)

	neer.postMessage("That's all for today!")

except:
	log.write("Hit an exception")
	traceback.print_exc(file = open("serverexception.txt", 'a'))
finally:
	neer.stop()
	for client in clients.keys():
		client.close()
	listener.shutdown(socket.SHUT_RD)
	listener.close()