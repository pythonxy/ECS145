import curses
from logger import *

log = Logger()

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
	i = 2;
	def __init__(self, boxLocation, scrollLocation, boxSize):
		(self.boxLocY, self.boxLocX) = boxLocation
		(self.scrollY, self.scrollX) = scrollLocation
		(self.boxY, self.boxX) = (sum(pair) for pair in zip(boxSize, boxLocation))

		self.pad = curses.newpad(1000, 10000)

		self.minY = self.boxLocY

		self.cursor = Cursor(0, 0, (self.boxLocY, self.boxLocX))

	def setText(self, text):
		self.pad.clear()

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
#Out of bounds
		if y + self.scrollY > self.maxY:
			self.cursor.setX(0)
			self.cursor.setY(0)
			raise Exception #next page!

		if y < self.minY:
			self.cursor.setY(0)
			return

		if x < 0:
			self.cursor.setX(0)
			return

		if x + self.scrollX > self.maxX:
			self.cursor.setX(0)
			self.cursor.moveY(1)
			self.scrollX = 0
			self.checkCursor(self.cursor.absy, self.cursor.absx)
			return

#Needs scrolling
		if y > self.boxLocY + self.boxY:
			log.write("Caught scroll down event")
			self.scrollY += 1
			self.cursor.moveY(-1)
		if x > self.boxLocX + self.boxX:
			log.write("Caught scroll right event")
			self.scrollX += 1
			self.cursor.moveX(-1)
		if y < self.boxLocY + self.scrollY:
			log.write("Caught scroll up event")
			self.scrollY -= 1
			self.cursor.moveY(1)
		if x < self.boxLocX + self.scrollX:
			log.write("Caught scroll left event")
			self.scrollX -= 1
			self.cursor.moveX(1)

		return

	def refresh(self):
		log.write("Calling pad refresh with scroll = (%d, %d), origin = (%d, %d), size = (%d, %d)" % (self.scrollY, self.scrollX, self.boxLocY, self.boxLocX, self.boxY, self.boxX))
		self.pad.refresh(self.scrollY, self.scrollX, self.boxLocY, self.boxLocX, self.boxY, self.boxX)





class Window:
	def __init__(self):
		self.window = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.window.keypad(1)
		
		(maxY, maxX) = self.window.getmaxyx()
		self.width = maxX - 1
		self.center = int((maxY - 1)/ 2)
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
			self.topPad.handleKey(key)
		else: 
			self.bottomPad.handleKey(key)
			
		

	def refresh(self):
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
	window.topPad.setText("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nA\nA\nA\nA\n\nA\nA\nA\nA\n\nA\nA\nA\nA\n\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nA\nAAAAAA\nBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\nc" + str(window.center * 2) + "\nj\nk\nl\m")
	window.bottomPad.setText("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\nc\nm")
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