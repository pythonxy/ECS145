


class Logger:
	def __init__(self, logfilename):
		self.logfilename = logfilename

	def write(self, stmnt):
		self.logfile = open(self.logfilename, "a")
		self.logfile.write(stmnt + "\n")
		self.logfile.close()
	
	def close(self):
		pass