import itertools

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
				for i in vals:
					printList.append(i)
			except KeyError:
				pass
		for i in range(len(printList)):
			print printList[i]

	def bpadd(self, bp):
		bitSum = 0
		for i in range(self.n):
			bitSum += bp[i]
		if bitSum in self.bps:
			print "bp: " + str(bp)
 			self.bps[bitSum].append(bp[:])
			print self.bps[bitSum]
		else:
			self.bps[bitSum] = []
			self.bps[bitSum].append(bp[:])

	def bpdel(self, bp):
		bitSum = 0
		for i in range(self.n):
			bitSum += bp[i]
		self.bps[bitSum].remove(bp)
		
#Works!		
def evaluateAssignment(assignment):
	print "Assignment: " + str(assignment)
	orVal = False
	for andTerm in assignment:
		andVal = True
		for b in andTerm:
			if b == 0:
				andVal = False
		orVal = orVal or andVal
	return orVal

#Works!
def createAssignments(expression, n):
	out = []
	for i in itertools.product((0, 1), repeat = n):
		out.append(list(i))
	return out

def mapBits(mapping, truePatterns):
	bitList = truePatterns[:]
	for j in range(len(truePatterns)):	
		for i in range(len(mapping)):
			print i, j
			print len(truePatterns)
			print len(bitList)
			print mapping
			bitList[j][mapping[i]] = truePatterns[j][i]	 	
	return bitList


#Works! maybe....
def createMapping(expression, n):
	mapping = []
	for j in range(len(expression)):
		mapping = mapping + expression[j]	
	for i in range(n):
		if i not in mapping:
			mapping.append(i)
	return mapping

def getpatts(expression, n):

	# create all possible bit assignments
	possibles = createAssignments(expression, n)
	
	# create bit mapping based on expression 
	mapping = createMapping(expression, n)	
	truePatterns = []	

	totalLen = 0
	expLens = []
	for i in expression:
		totalLen += len(i)
		expLens.append(len(i))
	print "expLens: " + str(expLens)

	# Check for valid assignments

	for assignment in possibles:
		listyList = []
		place = 0
		for i in range(len(expLens)):
			if i == 0:
				listyList.append(assignment[:expLens[i]])
				place = expLens[i]
			else:
				listyList.append(assignment[place:place + expLens[i]])
				place += expLens[i]


		boolVal = evaluateAssignment(listyList)
		print boolVal
		if boolVal:			
			truePatterns.append(assignment[:])

	# map bits to correct positions
	mappedPatterns = mapBits(mapping, truePatterns)	
	
	bitCollection = bpcoll(n)
	for i in range(len(mappedPatterns)):
		mappedPatterns[i].reverse()
		bitCollection.bpadd(mappedPatterns[i])

	return bitCollection
			

b = getpatts([[0, 1], [2]], 4)
print str(b.bps)
b.bpsprint()
