import os
import sys
import subprocess
import Exc


#pdfname = sys.argv[1]
#indexfilename = sys.argv[2]
#wordfilename = ""


class SysGlobals:
	indexfilename = ""
	wordfilename = ""
	pdfname = ""


class Page:
	num = 0
	def __init__(self, text):
		Page.num += 1
		self.text = text
		self.pagenum = Page.num

	def findWord(self, word):
		location = []
		index = self.text[:].lower().find(word)
		location.append((index, index + len(word)))
	
		while index != -1 and len(word) > 0:
			index = self.text.find(word, index +len(word))
			location.append((index, index + len(word)))

		location.pop()
		return location


class Document:
	curPage = 0
	def __init__(self, pdfname):
		subprocess.call("pdftotext %s temp.txt -layout" % (pdfname), shell=True)
		text = open("temp.txt", 'r')		
		self.paginate(text)
		text.close()

	def paginate(self, textfile):
		self.body = textfile.readlines()
		self.body = reduce(lambda x, y: x + y, self.body[:])			
		self.tmppages = self.body.split('\x0c')
		self.pages = {}
		for text in self.tmppages:
			newPg = Page(text)
			self.pages[newPg.pagenum] = newPg

	def nextPage(self):
		if self.curPage <= len(self.pages):
			self.curPage += 1
			page = self.pages[self.curPage]
			return page
		else:
			raise Exc.EOF()
	def previousPage(self):
		if self.curPage > 1:
			self.curPage -= 1
			page = self.pages[self.curPage]
			return page
		else:
			raise Exc.BOF()

	def getPage(self, num):
		num = int(num)
		self.curPage = num
		return self.pages[num]

class Index:
	def __init__(self, document, filename):
		self.location = {}
		self.words = []
		self.file = open(filename, 'r')
		temp = self.file.readlines()
		self.file.close()
		temp = map(lambda x: x.rstrip('\n'), temp)
		temp = map(lambda x: x.lower(), temp)
		
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
	

	def findWord(self, document, pageNum = 0):
		if pageNum == 0:
			pageNum = range(1, Page.num + 1)
		for wordtuple in self.words:
			pagedict = {}
			for num in pageNum:
				page = document.pages[num]
				wordLocs = []
				for word in wordtuple:
					temp = page.findWord(word)
					wordLocs = wordLocs + temp
				pagedict[page.pagenum] = wordLocs
			self.location[wordtuple] = pagedict
			

	def writeOut(self):
		output = []
		for wordtuple in self.words:
			entry = "/".join(wordtuple)
			entry += " "
			numberyList = []

			for num, val in self.location[wordtuple].items():
				if len(val) != 0:
					numberyList.append(num)
			numberyList.sort()
			for num in numberyList: 		
				entry += str(num) + ","
			output.append(entry[:-1])			 
		self.IW = reduce(lambda x, y: x + "\n" + y, output)
		indexFile = open(SysGlobals.indexfilename, 'w+')
		indexFile.write(self.IW)
		indexFile.close()
		return self.IW

	def indexIW(self):
		self.iwIndex = {}
		lines = self.IW.split("\n")
		tuplesNnums = map(lambda x: x.split(" "), lines)

		badWords = filter(lambda x: len(x) != 2, tuplesNnums)
		tuplesNnums = filter(lambda x: len(x) == 2, tuplesNnums)

		for word in badWords:
			self.words.remove(tuple(word))

		nums = [b[1] for b in tuplesNnums]
		
		nums = map(lambda x: x.split(","), nums)

		for i in range(len(self.words)): #for line in IW
			self.iwIndex[self.words[i]] = {}
			offset = self.calcOffset(lines[i])
			offset2 = offset[:]
			offset2.pop(0)
			offset2.append(len(lines[i]))
		
			byteRange = map(range, offset, offset2)
			for k in range(len(byteRange)):
				for j in byteRange[k]:
					self.iwIndex[self.words[i]][j] = nums[i][k]


	def calcOffset(self, lineText):
		(words, nums) = lineText.split(" ")
		baseOffset = len(words) + 1
		nums = nums.split(",")

		offset = nums[:]

		offset[0] = baseOffset
		for i in range(1, len(nums)):
			offset[i] = 1 + offset[i-1] + len(nums[i-1])

		return offset





