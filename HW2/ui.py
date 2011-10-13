import curses

hmm = []

class Window:
	def __init__(self):
		self.window = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.window.keypad(1)
		
		dim = self.window.getmaxyx()
		self.width = dim[1]
		self.center = int(dim[0] / 2) # even/odd?
		self.botBeg = self.center + 1
		self.botEnd = dim[0]-1

		self.topCursYX = [0,0]
		self.botCursYX = [self.botBeg, 0]
		self.topScrlVH = [0,0]
		self.botScrlVH = [0,0]

		self.isBottom = False

	def initialize(self):
		self.topPadYX = [self.botEnd+1, self.width]
		self.botPadYX = [self.botEnd+1, self.width]
		self.topPad = curses.newpad(self.topPadYX[0], self.topPadYX[1]) # height, width
		self.botPad = curses.newpad(self.botPadYX[0], self.botPadYX[1]) # height, width

		self.window.hline(self.center, 0, curses.ACS_HLINE, self.width)
		self.window.move(self.topCursYX[0], self.topCursYX[1])
		self.topPad.refresh(self.topScrlVH[0], self.topScrlVH[1], 0, 0, self.center-1, self.width)
		self.botPad.refresh(self.botScrlVH[0], self.botScrlVH[1], self.botBeg, 0, self.botEnd, self.width)

	def handle(self):
		key = self.window.getch()
		if key == ord('o'):
			self.isBottom = ~self.isBottom
		elif key == curses.KEY_UP:
			if self.isBottom:
				if self.botCursYX[0] > self.botBeg:
					self.botCursYX[0] -= 1
				elif self.botScrlVH[0] > 0:
					self.botScrlVH[0] -= 1
			else:
				if self.topCursYX[0] > 0:
					self.topCursYX[0] -= 1
				elif self.topScrlVH[0] > 0:
					self.topScrlVH[0] -= 1
		
		elif key == curses.KEY_DOWN:
			if self.isBottom:
				if self.botCursYX[0] < self.botEnd:
					self.botCursYX[0] += 1
				elif self.botScrlVH[0] < self.botPadYX[0]-1:
					self.botScrlVH[0] += 1
			else:
				if self.topCursYX[0] < self.center-1:
					self.topCursYX[0] += 1
				elif self.topPadYX[0]-1 > self.center-1 and self.topScrlVH[0] < self.topPadYX[0]-1:
					self.topScrlVH[0] += 1
		
		elif key == curses.KEY_LEFT:
			if self.isBottom:
				if self.botCursYX[1] > 0:
					self.botCursYX[1] -= 1
				elif self.botScrlVH[1] > 0:
					self.botScrlVH[1] -= 1
			else:
				if self.topCursYX[1] > 0:
					self.topCursYX[1] -= 1
				elif self.topScrlVH[1] > 0:
					self.topScrlVH[1] -= 1

		elif key == curses.KEY_RIGHT:
			if self.isBottom:
				if self.botCursYX[1] < self.width-1:
					self.botCursYX[1] += 1
				elif self.botScrlVH[1] < self.botPadYX[1]-1:
					self.botScrlVH[1] += 1
			else:
				if self.topCursYX[1] < self.width-1:
					self.topCursYX[1] += 1
				elif self.topPadYX[1] > self.width-1 and self.topScrlVH[1] < self.topPadYX[1]-1:
					self.topScrlVH[1] += 1
		return key

	def refresh(self):
		if self.isBottom:
			self.window.move(self.botCursYX[0], self.botCursYX[1])
		else: 
			self.window.move(self.topCursYX[0], self.topCursYX[1])

		self.topPad.refresh(self.topScrlVH[0], self.topScrlVH[1], 0, 0, self.center-1,self.width)
		self.botPad.refresh(self.botScrlVH[0], self.botScrlVH[1], self.botBeg, 0, self.botEnd, self.width)		

	def finish(self):
		self.window.keypad(0) 
		curses.nocbreak()
		curses.echo()
		curses.endwin()

	def isBeg(self):
		return self.topScrlVH[0] <= 0

	def isEnd(self):
		return self.topScrlVH[0] >= self.topPadYX[0]-1
		
	def getCursor(self):
		return [self.botX, self.botY]

	def setTopText(self, text):
		lines = text.split('\n')
		rows = len(lines)		
		cols = max(map(len, lines))
		self.topPadYX = [rows, cols]
		
		rows = max(rows, self.center-1)
		cols = max(cols, self.width)
		self.topPad.resize(rows, cols-1)

		global hmm
		hmm = self.topPad.getmaxyx()

		row = 0
		for line in lines:
			self.topPad.addstr(row, 0, line)
			row += 1

	def setBotText(self, text):
		lines = text.split('\n')
		rows = len(lines)		
		cols = max(map(len, lines))
		self.botPadYX = [rows, cols]

		rows = max(rows, self.botEnd)
		cols = max(cols, self.width)
		self.botPad.resize(rows, cols)

		global hmm
		hmm = self.botPad.getmaxyx()

		row = 0
		for line in lines:
			self.botPad.addstr(row, 0, line)
			row += 1

	# Needs finishing
	def highlight(self, words):
		for word in words:
			self.topPad.chgat(word[1], word[0], curses.A_REVERSE)


window = Window()		
try:
	window.initialize()

	window.setBotText("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
	window.setTopText("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC\nDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")

	while True:
		key = window.handle()
		if key == ord('q'):
			break
		window.refresh()
		
finally:
	window.finish()
	print hmm	
