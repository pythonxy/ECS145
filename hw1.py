
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
				for patternList in vals:
					printBits = ""
					for bitPattern in patternList:
						printBits += str(bitPattern)
					printList.append(printBits)
			except KeyError:
				pass
		for elt in printList:
			print elt

	def bpadd(self, bp):
		bitSum = 0
		for i in range(self.n):
			bitSum += bp[i]
		if bitSum in self.bps:
 			self.bps[bitSum].append(bp[:])
		else:
			self.bps[bitSum] = []
			self.bps[bitSum].append(bp[:])

	def bpdel(self, bp):
		bitSum = 0
		for i in range(self.n):
			bitSum += bp[i]
		self.bps[bitSum].remove(bp)
		
#Checks whether a given assignment satisfies the given expression		
def evaluateAssignment(assignment):
	orVal = False
	for andTerm in assignment[0]:
		andVal = True
		for b in andTerm:
			andVal = b and andVal
		orVal = orVal or andVal
	return orVal


#Returns the binary equivalent of the given number as a list
def getBinary(num, n):
	output = []
	for i in range(n):
		if num % 2 == 0:
			output.append(0)
		else:
			output.append(1)
		num /= 2
	output.reverse()
	return output


#Creates all possible bit-assignments for an n-bit expression
def createAssignments(expression, n):
	out = []
	for i in range(2**(n)):
		out.append(getBinary(i, n))
	return out


#Maps bits to correct positions (as given in the expression) 
def mapBits(mapping, truePatterns):
	bitList = []
	for row in bitList:
		print row
	for row in range(len(truePatterns)):	
		bitRow = [0 for i in range(len(truePatterns[row]))]
		for elt in range(len(mapping)):
			bitRow.pop(mapping[elt])
			bitRow.insert(mapping[elt], truePatterns[row][elt])
		bitList.append(bitRow)
	return bitList
	
#Determines the bit-mapping (based on indices given in the expression)
def createMapping(expression, n):
	mapping = []
	for j in range(len(expression)):
		mapping = mapping + expression[j]	
	for i in range(n):
		if i not in mapping:
			mapping.append(i)
	return mapping


#Collects and-terms of an expression
def collectExpressions(possible, expLens):
	listyList = []
	place = 0
	for i in expLens:
		if place == 0:
			listyList.append(possible[:i])
			place = i
		else:
			listyList.append(possible[place:place + i])
			place += i
	return listyList


#Returns a bpcoll object containing all satrisfying bit patterns for a given expression
def getpatts(expression, n):

	expression = [list(set(a)) for a in expression]
	for a in expression:
		print a

	# create all possible bit assignments
	possibles = createAssignments(expression, n)
	
	# create bit mapping based on expression 
	mapping = createMapping(expression, n)	
	truePatterns = []	



	expLens = map(len, expression)
	totalLen = reduce(lambda x, y: x+y, expLens)

	# Collect assignment into and-terms 
	assignment = map(collectExpressions, possibles, [expLens]*len(possibles))
	
	# Filter for valid assignments, return corresponding bit patterns
	tempPatterns = filter(evaluateAssignment, zip(assignment, possibles))
	truePatterns = [b for (a, b) in tempPatterns]


	# map bits to correct positions
	mappedPatterns = mapBits(mapping, truePatterns)	

	bitCollection = bpcoll(n)
	for i in range(len(mappedPatterns)):
		print mappedPatterns[i]
		bitCollection.bpadd(mappedPatterns[i])

	return bitCollection
		
def main():
	b = getpatts([[2, 1, 0], [4]], 5)
	b.bpsprint()

if __name__ == "__main__":
	main()
