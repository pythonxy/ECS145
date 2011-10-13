


class Logger:
	def __init__(self):
		pass

	def write(self, stmnt):
		self.logfile = open("log.txt", "a")
		self.logfile.write(stmnt + "\n")
		self.logfile.close()
	
	def close(self):
		pass