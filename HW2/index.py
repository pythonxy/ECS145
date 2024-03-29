import curses
import Exc
from document import *
import sys

class Cursor:
	
	def __init__(self, init_y, init_x, offset):
		self.offset = offset[:]
		self.x = init_x
		self.y = init_y
		self.absx = init_x + self.offset[1]
		self.absy = init_y + self.offset[0]

	def moveX(self, val):
		self.x += val
		self.absx += val

	def moveY(self, val):
		self.y += val
		self.absy += val

	def setX(self, val):
		self.x = val
		self.absx = val + self.offset[1]

	def setY(self, val):
		self.y = val
		self.absy = val + self.offset[0]

	def updatePosition(self, key):
		if key == ord('l'):
			self.moveX(-1)
		elif key == ord('r'):
			self.moveX(1)		
		elif key == ord('u'):
			self.moveY(-1)
		elif key == ord('d'):
			self.moveY(1)
		return (self.absy, self.absx)

	def getAbsPosition(self):
		return (self.absy, self.absx)

	def getRelPosition(self):
		return (self.y, self.x)

class Pad:
	def __init__(self, boxLocation, scrollLocation, boxSize):
		(self.boxLocY, self.boxLocX) = boxLocation
		(self.scrollY, self.scrollX) = scrollLocation
		(self.boxY, self.boxX) = (sum(pair) for pair in zip(boxSize, boxLocation))

		self.pad = curses.newpad(1000, 10000)

		self.minY = self.boxLocY

		self.cursor = Cursor(0, 0, (self.boxLocY, self.boxLocX))
	
	def chgat(self, y, x, n, attr=curses.A_STANDOUT):
		for i in range(n):
			if y < len(self.lines) and x+i < len(self.lines[y]):
				char = self.lines[y][x+i]
				self.pad.addch(y,x+i,char,attr)
				self.pad.touchline(y, 1, 1)
		self.refresh()


	def setText(self, text):
		self.pad.clear()

		self.text = text

		self.lines = text.split('\n')
		self.maxY = len(self.lines) + self.boxLocY
		self.maxX = max(map(len, self.lines))

		self.pad.addstr(text)

		self.scrollY, self.scrollX = 0, 0

		self.cursor = Cursor(0, 0, (self.boxLocY, self.boxLocX))

		self.refresh()

	def handleKey(self, key):
		(y, x) = self.cursor.updatePosition(key)
		self.checkCursor(y, x)

		
	def checkCursor(self, y, x):
		if self.checkBounds(y, x):
			return
		else:
			self.checkScroll(y, x)
		

	def checkBounds(self, y, x):
		if y + self.scrollY > self.maxY:
			self.cursor.setY(0)
			raise Exc.PageDown() #next page!

		if y < self.minY and self.scrollY == 0:
			self.cursor.setY(0)
			raise Exc.PageUp()

		if x < 0 and self.scrollX == 0:
			self.cursor.setX(0)
			return True

		if x + self.scrollX > self.maxX:
			self.cursor.setX(0)
			self.cursor.moveY(1)
			self.scrollX = 0
			self.checkCursor(self.cursor.absy, self.cursor.absx)
			return True
		return False

	def checkScroll(self, y, x):
		if y > self.boxY:
			self.scrollY += 1
			self.cursor.moveY(-1)
		elif y < self.boxLocY and self.scrollY > 0:

			self.scrollY -= 1
			self.cursor.moveY(1)
		elif x > self.boxLocX + self.boxX:
			self.scrollX += 1
			self.cursor.moveX(-1)
		elif x < self.boxLocX and self.scrollX > 0:
			self.scrollX -= 1
			self.cursor.moveX(1)


	def refresh(self):
		self.pad.refresh(self.scrollY, self.scrollX, self.boxLocY, self.boxLocX, self.boxY, self.boxX)



class Window:
	def __init__(self):
		self.moved = True
		self.window = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.window.keypad(1)
		
		self.setDimensions()		
		self.curWord = None
		self.displayPage = 1
		self.indexPage = -1 



		self.topPad = Pad((0, 0), (0, 0), (self.center - 1, self.width))
		self.bottomPad = Pad((self.center + 1, 0), (0, 0), (self.center - 1, self.width))
		self.topPadActive = True
		self.refresh();

	def highlightWord(self):
		if self.curWord != None:
			
			# highlight all instances of the words on the indexPage
			for loc in index.location[self.curWord][int(self.indexPage)]:
				(beginY, beginX) = BytetoYX(loc[0],document.getPage(self.indexPage).text)
				(endY, endX) = BytetoYX(loc[1],document.getPage(self.indexPage).text)
				
				#if self.sequenceInTopBounds(beginY, beginX, endY, endX):
				self.topPad.chgat(beginY, beginX, endX - beginX, curses.A_REVERSE)


	
	def sequenceInTopBounds(self, beginY, beginX, endY, endX):
		return  beginY - self.topPad.scrollY >= 0 \
				and  beginX - self.topPad.scrollX >= 0 \
				and endY - self.topPad.scrollY < self.topPad.boxY \
				and endX - self.topPad.scrollX < self.topPad.boxX


	def handleKey(self, key):
		if key == ord('o'):
			self.topPadActive = not self.topPadActive
			self.moved = False

		elif key == ord('v') and (not self.topPadActive or self.curWord != None):
			(y, x) = self.bottomPad.cursor.getRelPosition()
			if y >= len(index.words):
				return
			# New word selected
			if self.curWord != index.words[y] and self.topPadActive == False:
			 	self.curWord = index.words[y]
			 	self.indexPage = min(map(int, index.iwIndex[self.curWord].values())) # First page for current word				 
				self.displayPage = self.indexPage
				try:

					self.indexPage = index.iwIndex[self.curWord][x]
					self.displayPage = self.indexPage
					self.topPad.setText(document.getPage(self.indexPage).text)
				except KeyError:
					self.topPad.setText(document.getPage(self.indexPage).text)
			#Same word as before
			else:
				try:
					tempPage = index.iwIndex[self.curWord][x]
					if int(self.displayPage) == int(tempPage) or self.moved == False:
						raise KeyError
					self.indexPage = tempPage
					self.displayPage = self.indexPage
					self.topPad.setText(document.getPage(self.indexPage).text)
				except KeyError:
					nums = index.iwIndex[self.curWord].values()
					nums = map(lambda x: int(x), nums)
					nums = list(set(nums))
					nums.sort()
					i = nums.index(int(self.indexPage)) + 1
					if i < len(nums):
						self.indexPage = nums[i]
						self.displayPage = self.indexPage 
					else:
						self.indexPage = nums[0]
						self.displayPage = self.indexPage
					self.topPad.setText(document.getPage(self.indexPage).text)
			self.moved = False

		elif self.topPadActive == True:
			try:
				self.moved = True
				self.topPad.handleKey(key)
			except Exception as e:
				if type(e) is Exc.PageDown:
					try:
						self.topPad.setText(document.nextPage().text)
						self.displayPage += 1
					except Exception:
						pass
				elif type(e) is Exc.PageUp:
					try:
						self.topPad.setText(document.previousPage().text)
						self.displayPage -= 1
					except Exception:
						pass

		else: 
			try:
				self.moved = True
				self.bottomPad.handleKey(key)
			except (Exc.PageUp, Exc.PageDown):
				pass	
	
	def resize(self):

		self.setDimensions()		
		

		topText = self.topPad.text
		self.topPad = Pad((0, 0), (0, 0), (self.center - 1, self.width))
		self.topPad.setText(topText)

		bottomText = self.bottomPad.text
		self.bottomPad = Pad((self.center + 1, 0), (0, 0), (self.center - 1, self.width))
		self.bottomPad.setText(bottomText)
		

	def setDimensions(self):
		(self.maxY, self.maxX) = self.window.getmaxyx()
		self.width = self.maxX - 1
		self.center = int((self.maxY - 1)/ 2)
		self.window.hline(self.center, 0, curses.ACS_HLINE, self.width)

	def refresh(self):
		if (self.maxY, self.maxX) != self.window.getmaxyx():
			self.resize()

		if self.topPadActive == True:
			self.window.move(self.topPad.cursor.absy, self.topPad.cursor.absx)
		else: 
			self.window.move(self.bottomPad.cursor.absy, self.bottomPad.cursor.absx)			
		
		if int(self.displayPage) == int(self.indexPage):
			self.highlightWord()
		self.bottomPad.refresh()
		self.topPad.refresh()
		self.window.refresh()

	def stop(self):
		curses.echo()
		curses.nocbreak()
		self.window.keypad(0)
		curses.endwin()


def YXtoByte(y, x, text):
	lines = text.split('\n')
	curByte = 0
	i = 0
	while i < y:
		curByte += len(lines[i]) + 1
		i += 1
	curByte += x
	return curByte

def BytetoYX(theByte, text):
	lines = text.split('\n')
	curByte = theByte
	i = -1
	while curByte >= 0:
		i+=1
		curByte -= len(lines[i]) + 1
	curByte += len(lines[i]) + 1
	return (i, curByte)

def main():

	window = Window()		
	try:
		window.topPad.setText(document.nextPage().text)
		window.bottomPad.setText(index.writeOut())
		window.refresh()

		key = ord('x')
		while True:
			if key == ord('q'):
				break
			window.handleKey(key)
			window.refresh()
			key = window.window.getch()

		
	finally:
		window.stop()

SysGlobals.pdfname = sys.argv[1]
SysGlobals.indexfilename = sys.argv[2]
SysGlobals.wordfilename = ""

if len(sys.argv) > 3:
	SysGlobals.wordfilename = sys.argv[3]

document = Document(SysGlobals.pdfname)
index = None

if len(sys.argv) > 3:
	index = Index(document, SysGlobals.wordfilename)
else:
	index = Index(document, SysGlobals.indexfilename)
index.indexIW()

if __name__ == "__main__":
	main()

