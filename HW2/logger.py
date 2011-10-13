


class Logger:
	def __init__(self):
		self.logfile = open("log.txt", "a")

	def write(self, stmnt):
		self.logfile.write(stmnt + "\n")

	def close(self):
		self.logfile.close()