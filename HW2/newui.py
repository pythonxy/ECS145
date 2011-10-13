import curses
from logger import *
import Exc
from index import *

log = Logger("uilog.txt")

document = Document("./Syllabus.pdf")
index = Index(document, "wordfile.txt")

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
		log.write("Cursor moved to: %d, %d" % (self.absy, self.absx))

	def moveY(self, val):
		self.y += val
		self.absy += val
		log.write("Cursor moved to: %d, %d" % (self.absy, self.absx))

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


class Pad:
	def __init__(self, boxLocation, scrollLocation, boxSize):
		(self.boxLocY, self.boxLocX) = boxLocation
		(self.scrollY, self.scrollX) = scrollLocation
		(self.boxY, self.boxX) = (sum(pair) for pair in zip(boxSize, boxLocation))

		self.pad = curses.newpad(1000, 10000)

		self.minY = self.boxLocY

		self.cursor = Cursor(0, 0, (self.boxLocY, self.boxLocX))


	def setText(self, text):
		self.pad.clear()

		self.text = text

		lines = text.split('\n')
		self.maxY = len(lines) + self.boxLocY
		self.maxX = max(map(len, lines))

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
		log.write("Checking scrolling")
		log.write("boxLocY, boxY: %d, %d" % (self.boxLocY, self.boxY))
		if y > self.boxY:
			log.write("Caught scroll down event")
			self.scrollY += 1
			self.cursor.moveY(-1)
		elif y < self.boxLocY and self.scrollY > 0:
			log.write("Caught scroll up event")
			log.write("MaxY, MaxX: %d, %d" % (self.maxY, self.maxX))
			self.scrollY -= 1
			self.cursor.moveY(1)
		elif x > self.boxLocX + self.boxX:
			log.write("Caught scroll right event")
			self.scrollX += 1
			self.cursor.moveX(-1)
		elif x < self.boxLocX and self.scrollX > 0:
			log.write("Caught scroll left event")
			self.scrollX -= 1
			self.cursor.moveX(1)


	def refresh(self):
		log.write("Calling pad refresh with scroll = (%d, %d), origin = (%d, %d), size = (%d, %d)" % (self.scrollY, self.scrollX, self.boxLocY, self.boxLocX, self.boxY, self.boxX))
		self.pad.refresh(self.scrollY, self.scrollX, self.boxLocY, self.boxLocX, self.boxY, self.boxX)





class Window:
	def __init__(self):
		self.window = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.window.keypad(1)
		
		(self.maxY, self.maxX) = self.window.getmaxyx()
		self.width = self.maxX - 1
		self.center = int((self.maxY - 1)/ 2)
		self.window.hline(self.center, 0, curses.ACS_HLINE, self.width)
		
		log.write("width, center: %d, %d" % (self.width, self.center))

		self.topPad = Pad((0, 0), (0, 0), (self.center - 1, self.width))
		self.bottomPad = Pad((self.center + 1, 0), (0, 0), (self.center - 1, self.width))
		self.topPadActive = True
		self.refresh();


	def handleKey(self, key):
		if key == ord('o'):
			self.topPadActive = ~self.topPadActive
			log.write("Top pad active? " + str(self.topPadActive))
		elif self.topPadActive == True:
			try:
				self.topPad.handleKey(key)
			except Exception as e:
				if type(e) is Exc.PageDown:
					try:
						self.topPad.setText(document.nextPage().text)
					except Exception:
						pass
				elif type(e) is Exc.PageUp:
					try:
						self.topPad.setText(document.previousPage().text)
					except Exception:
						pass
		else: 
			self.bottomPad.handleKey(key)
			
	
	def resize(self):
		log.write("Resizing pads")

		(self.maxY, self.maxX) = self.window.getmaxyx()
		self.width = self.maxX - 1
		self.center = int((self.maxY - 1)/ 2)
		self.window.hline(self.center, 0, curses.ACS_HLINE, self.width)
		
		log.write("width, center: %d, %d" % (self.width, self.center))

		topText = self.topPad.text
		self.topPad = Pad((0, 0), (0, 0), (self.center - 1, self.width))
		self.topPad.setText(topText)

		bottomText = self.bottomPad.text
		self.bottomPad = Pad((self.center + 1, 0), (0, 0), (self.center - 1, self.width))
		self.bottomPad.setText(bottomText)

		#self.topPadActive = True

	def refresh(self):
		if (self.maxY, self.maxX) != self.window.getmaxyx():
			self.resize()

		self.window.refresh()

		if self.topPadActive == True:
			self.window.move(self.topPad.cursor.absy, self.topPad.cursor.absx)
			log.write("Setting window cursor: %d, %d" % (self.topPad.cursor.absy, self.topPad.cursor.absx))
		else: 
			self.window.move(self.bottomPad.cursor.absy, self.bottomPad.cursor.absx)			
			log.write("Setting window cursor: %d, %d" % (self.bottomPad.cursor.absy, self.bottomPad.cursor.absx))


		self.topPad.refresh()
		self.bottomPad.refresh()

	def stop(self):
		curses.echo()
		curses.nocbreak()
		self.window.keypad(0)
		curses.endwin()

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
	log.close()