import os
import sys
import subprocess


#pdfname = sys.argv[1]
#indexfilename = sys.argv[2]
#wordfilename = ""
if len(sys.argv) > 2:
	wordfilename = sys.argv[3]



class Page:
	num = 0
	def __init__(self, text):
		Page.num += 1
		self.text = text
		self.pagenum = Page.num

	def findWord(self, word):
		location = []
		index = self.text[:].find(word)
		location.append((index, index + len(word)))
	
		while index != -1:
			index = self.text.find(word, index +len(word))
			location.append((index, index + len(word)))

		location.pop()
		return location


class Document:
	
	def __init__(self, pdfname):
		subprocess.call("pdftotext %s temp.txt -layout" % (pdfname), shell=True)
		text = open("temp.txt", 'r')		
		self.paginate(text)

	def paginate(self, textfile):
		self.body = textfile.readlines()
		self.body = reduce(lambda x, y: x + y, self.body[:])			
		self.tmppages = self.body.split('\x0c')
		self.pages = {}
		for text in self.tmppages:
			newPg = Page(text)
			self.pages[newPg.pagenum] = newPg


class Index:
	def __init__(self, document, filename):
		self.location = {}
		self.words = []
		self.file = open(filename, 'r')
		temp = self.file.readlines()
		temp = map(lambda x: x.rstrip('\n'), temp)
		
		try:
			pgnums = range(len(temp))
			self.wordtext = range(len(temp))
			for i in range(len(temp)):
				[self.wordtext[i], pgnums[i]] = temp[i].split(" ")	

			self.words = map(lambda x: tuple(x.split("/")), self.wordtext)
			pgnumList = map(lambda x: x.split(","), pgnums)
			pgnumList = reduce(lambda x, y: x + y, pgnumList)
			pgnumList = map(lambda x: int(x), pgnumList)

		except ValueError:
			self.wordtext = temp[:]
			self.words = map(lambda x: tuple(x.split("/")), self.wordtext)
			pgnumList = 0

		self.findWord(document, pgnumList)
		self.writeOut()
	
	def parseWordFile(self, wordfilename):
		self.wordfile = open(wordfilename, 'r')
		self.wordtext = self.wordfile.readlines()
		self.wordtext = map(lambda x: x.rstrip('\n'), self.wordtext)

	def findWord(self, document, pageNum = 0):
		if pageNum == 0:
			pageNum = range(1, Page.num + 1)
		print pageNum
		for wordtuple in self.words:
			pagedict = {}
			for num in pageNum:
				print num
				page = document.pages[num]
				wordLocs = []
				for word in wordtuple:
					temp = page.findWord(word)
					wordLocs = wordLocs + temp
				if wordLocs != []:
					print wordLocs
				pagedict[page.pagenum] = wordLocs
			self.location[wordtuple] = pagedict

	def writeOut(self):
		output = []
		for wordtuple in self.words:
			entry = "/".join(wordtuple)
			entry += " "
			for num, val in self.location[wordtuple].items():
				if len(val) != 0:
					entry += str(num) + ","
			output.append(entry[:-1]) 
		print output
#		indexFile = open(indexfilename, 'w')
#		indexFile.writelines(output)

doc = Document("./Syllabus.pdf")
print "created temp.txt"
index = Index(doc, "wordfile.txt")
