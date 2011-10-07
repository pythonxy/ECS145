import os
import subprocess

class Document:
	
	def __init__(self, pdfname):
		subprocess.call("pdftotext %s temp.txt -layout" % (pdfname))
		text = open("temp.txt", 'r')		
		self.paginate(text)

	def paginate(self, textfile):
		self.body = textfile.readlines()
		self.tmppages = self.body.split('\x0c')
		self.pages = {}
		for text in self.tmppages:
			newPg = Page(text)
			self.pages[newPg.pagenum] = newPg


class Page:
	num = 0
	def __init__(self, text):
		num += 1
		self.text = text
		self.pagenum = num

	def findWord(self, word):
		index = self.text[index:].find(word)
		location = []
		while index != -1:
			index = page.text[index +len(word):].find(word)
			location.append = (index, index + len(word))
		return location

class Index:
	def __init__(self, document, wordfilename):
		self.location = {}
		self.words = []
		for word in self.words:
			self.wordLocations[word] = {}

		self.parseWordFile(wordfilename)

	def __init(self, index):
		pass

	def parseWordFile(self, wordfilename):
		self.wordfile = open(wordfilename, 'r')
		self.wordtext = wordfile.readlines()
		for line in self.wordtext:
			wordtuple = tuple(line.split('/'))
			self.words.append(wordtuple)
	 	
	def findWord(self, document):
		for wordtuple in self.words:
			for page in document.pages:
				wordLocs = []
				for word in wordtuple:
					wordlocs = wordLocs + page.findWord(word)
				pagedict[page.pagenum] = wordLocs
		locations[wordtuple] = pagedict
