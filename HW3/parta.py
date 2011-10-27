import curses
import string
import Exc
from logger import *


log = Logger("uilog.txt")


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

		self.pad = curses.newpad(2000, 2000)
		self.topLine = 0

		self.setText("")

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
			self.cursor.setY(self.boxLocY)
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


	def insertLine(self, line):
		self.pad.insstr(self.topLine, 0, line)
		if self.topLine > self.boxY:
			self.scrollY += 1
			self.cursor.setY(self.boxLocY)
		if self.topLine > len(self.text):
			self.maxY += 1
		self.topLine += 1



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
		self.inputChars = []
		self.inputString = ""

		self.topPad = Pad((0, 0), (0, 0), (self.center - 1, self.width))
		
		self.bottomPad = Pad((self.center + 1, 0), (0, 0), (self.center - 1, self.width))
		self.bottomPad.cursor.moveY(1)
		self.bottomMessage = ""

		self.topText = ""
		self.addMessage("Welcome to AuctionProLitester.ly")
		self.addMessage("Fuck this")

		self.bottomPad.setText(self.bottomMessage + "\n" + "".join(self.inputChars))

		log.write("bottom cursor at: %d, %d" % self.bottomPad.cursor.getAbsPosition())

		self.topPadActive = False
		self.refresh();


	def highlightWord(self):  #NEEDS ADJUSTING- NO INDEX (POSSIBLY USE CLIENT NAME?)
		if self.curWord != None:
			
			# highlight all instances of the words on the indexPage
			for loc in index.location[self.curWord][int(self.indexPage)]:
				(beginY, beginX) = BytetoYX(loc[0],document.getPage(self.indexPage).text)
				(endY, endX) = BytetoYX(loc[1],document.getPage(self.indexPage).text)
				
				#if self.sequenceInTopBounds(beginY, beginX, endY, endX):
				self.topPad.chgat(beginY, beginX, endX - beginX, curses.A_REVERSE)


	def handleKey(self, key):
		if key == curses.KEY_MOUSE:
			pass

		elif key == curses.KEY_HOME:
			self.topPadActive = not self.topPadActive


		elif self.topPadActive == True:
			try:
				self.topPad.handleKey(key)
			except Exception as e:
				pass

		elif key == curses.KEY_ENTER or key == 10:
			log.write("Pressed Enter")
			self.inputString = "".join(self.inputChars)
			self.inputChars = []
			self.bottomPad.cursor.setY(1)
			self.bottomPad.cursor.setX(0)
			log.write("inputString = " + self.inputString)

		elif key == curses.KEY_BACKSPACE:
			try:
				self.inputChars.pop()
				self.bottomPad.cursor.moveX(-1)
			except IndexError:
				pass

		else:
			try:
				log.write("Pressed " + chr(key))
				self.inputChars.append(chr(key))
				self.bottomPad.cursor.moveX(1)
			except:
				pass

	def resize(self):
		self.setDimensions()		

		self.topPad = Pad((0, 0), (0, 0), (self.center - 1, self.width))
		lines = self.topText.split("\n")
		self.topText = ""
		
		for line in lines:
			self.addMessage(line)

		bottomText = self.bottomPad.text
		self.bottomPad = Pad((self.center + 1, 0), (0, 0), (self.center - 1, self.width))
		self.bottomPad.cursor.moveY(1)
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
			self.bottomPad.setText(self.bottomMessage + "\n" + "".join(self.inputChars))

		self.topPad.refresh()
		self.window.refresh()

	def addMessage(self, text):
		self.topPad.insertLine(text)
		self.topText += text + "\n"


	def stop(self):
		curses.echo()
		curses.nocbreak()
		self.window.keypad(0)
		curses.endwin()

	def setBottomMessage(self, text):
		self.bottomMessage = text

def main():

	window = Window()		
	try:
		window.setBottomMessage("Enter Bid:")
		window.refresh()

		key = ord("!")

		while True:
			if key == ord('q'):
				break
			window.handleKey(key)
			window.refresh()
			key = window.window.getch()
		
	finally:
		window.stop()

if __name__ == "__main__":
	main()

