import curses


class Cursor:
	
	def __init__(self, init_y, init_x, offset):
		self.offset = offset
		self.x = init_x
		self.y = init_y
		self.absx = init_x + offset[1]
		self.absy = init_y + offset[0]

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
			self.moveX(-1)
		elif key == ord('v'):
			self.moveX(1)
		return (y, x)


class Pad:
	
	def __init__(self, boxLocation, scrollLocation, boxSize):
		(self.boxLocY, self.boxLocX) = boxLocation
		(self.scrollY, self.scrollX) = scrollLocation
		(self.boxY, self.boxX) = boxSize

		self.pad = curses.newpad(1000, 10000)

		self.cursor = Cursor(self.boxLocY, self.boxLocX)

	def setText(self, text):
		self.pad.clear()

		lines = text.split('\n')
		self.maxY = len(lines)
		self.maxX = max(map(len, lines))

		self.topPad.addstr(text)

		self.scrollY, self.scrollX = 0, 0

		self.cursor = Cursor(self.boxLocY, self.boxLocX)

		self.refresh()

	def handleKey(self, key):
		(y, x) = self.cursor.updatePosition(key)
		self.checkCursor(y, x)

		
	def checkCursor(self, y, x):
#Out of bounds
		if y > self.maxY:
			self.cursor.setX(0)
			self.cursor.setY(0)
			raise Exception #next page!

		if y < 0:
			self.cursor.setY(0)

		if x < 0:
			self.cursor.setX(0)

		if x > self.maxX:
			self.cursor.setX(0)
			self.cursor.moveY(1)
			self.checkCursor(self.cursor.y, self.cursor.x)

#Needs scrolling
		if y > self.boxLocY + self.boxY:
			self.scrollY += 1
		if x > self.boxX + self.boxX:
			self.scrollX += 1
		if y <= self.boxLocY + self.scrollY:
			self.scrollY -= 1
		if x <= self.boxLocX + self.scrollX:
			self.scrollX -= 1

		return

	def refresh(self):
		self.pad.refresh(self.scrollY, self.scrollX, self.boxLocY, self.boxLocX, self.boxY, self.boxX)





class Window:
	def __init__(self):
		self.window = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.window.keypad(1)
		
		(maxY, maxX) = self.window.getmaxyx()
		self.width = maxX
		self.center = int(maxY / 2)
		self.topPad = Pad((0, 0), (self.center -1, self.width))
		self.bottomPad = Pad((self.center + 1, 0), (maxY, self.width))
		self.topPadActive = True

	def refresh(self):
		if self.topPadActive:
			self.window.move(self.topPad.cursor.absy, self.topPad.cursor.absx)
		else:
			self.window.move(self.bottomPad.cursor.absy, self.bottomPad.cursor.absx)			

		self.topPad.refresh()
		self.bottomPad.refresh()

	def stop():
		curses.echo()
		curses.nocbreak()
		self.window.keypad(0)
		self.window.endwin()




























