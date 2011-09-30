

class bpcoll:
	def __init__(self, lenPatterns):
		self.n = lenPatterns
		self.bps = {}
	def bpsprint(self):
		printList = []
		for j in range(1, self.n + 1):
			try:
				vals = self.bps[j]
				vals.sort()
				printList.append(vals)
			except KeyError:
				pass
		for i in range(len(printList)):
			print printList[i]

	def bpadd(self, bp):
		bitSum = 0
		for i in range(self.n):
			bitSum += bp[i]
		if bitSum in bps:
 			bps[bitSum].append(bp[:])
		else:
			bps[bitSum] = bp[:]

	def bpdel(self, bp):
		bitSum = 0
		for i in range(self.n):
			bitSum += bp[i]
		bps[bitSum].remove(bp)
				

