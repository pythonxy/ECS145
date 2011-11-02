from SimPy.Simulation import *
import math
import random


curJob = 0
avgList = []
ct = 0.1
rt = .1
mean_kv = 2.0
max_req = 2
mean_arriv = 2.0
size = 100

class Cloud(Process):
	global size
	global max_req

	availableNodes = size
	requests = 0
	rejections = 0
	activeJobs = []

	def Run(self):
		global mean_arriv

		while True:
			job = UserJob(random.choice(range(2, max_req + 1)))
			if job.numNodes > Cloud.availableNodes:
				Cloud.requests += 1
				Cloud.rejections += 1
			else:
				Cloud.requests +=1
				Cloud.availableNodes -= job.numNodes
				activate(job, job.Run())
				Cloud.activeJobs.append(job)
			
			yield hold, self, random.expovariate(1.0/mean_arriv)


class UserJob(Process):
	def __init__(self, numNodes):
		global curJob
		curJob += 1
		Process.__init__(self, name = str(curJob))
		self.nodes = numNodes
		self.numNodes = numNodes
		self.totalPairs = self.getInputPairs()
		self.numPairs =  self.totalPairs / (self.numNodes-1) 

		print "Pairs per node:", self.numPairs

	def Run(self):
		global avgList

		print "Assigned ", self.numNodes - 1, " map nodes to job", str(curJob)
		for i in range(self.numNodes-1):
			mnode = MapNode(self.numPairs, self)
			activate(mnode, mnode.Run())
			self.nodes -= 1
		
		self.rnode = ReduceNode(self.totalPairs, self)
		activate(self.rnode, self.rnode.Run())
		self.nodes -=1

		print "nodes = ", self.nodes, "numnodes =", self.numNodes
		while True:
			if self.nodes == self.numNodes:
				Cloud.availableNodes += self.numNodes
				avgList.append(size - Cloud.availableNodes)
				Cloud.activeJobs.remove(self)
				break
			else:
				print "Sleeping job", self.name
				yield passivate, self
		print "Ending job", self.name

	def getInputPairs(self):
		''' Gives the number of input pairs per map node '''
		numPairs = math.ceil(self.geomvariate()*(self.numNodes - 1))
		
		print "Total number of input pairs:", numPairs

		return int(numPairs)

	def geomvariate(self):
		global mean_kv
		q = 1.0/mean_kv
		n = 1
		while 1:
			if random.uniform(0,1) < q: 
				return n
			n += 1


class MapNode(Process):
	def __init__(self, numPairs, job):
		global ct

		Process.__init__(self)
		self.job = job #associated job- "parent process"
		self.numPairs = numPairs # number of work items assigned to this node
		self.workList = [] # queue of pending work items
		for i in range(numPairs):
			completionTime = random.uniform(.5*ct, 1.5*ct)
			self.workList.append(completionTime)

	
	def Run(self):
		print "Requested a map node from", self.job.name, "with", self.numPairs, "pairs"


		while len(self.workList) != 0:
			pair = self.workList.pop(0)
			print "Processing work item, completion time = ", pair, "Job number", self.job.name
			yield hold, self, pair
			self.job.rnode.workList.append(pair)
			if self.job.rnode.passive():

				reactivate(self.job.rnode)
		print "updating nodes from map"
		self.job.nodes += 1
		print "passivating map node from job", self.job.name
		yield passivate, self


class ReduceNode(Process):
	def __init__(self, numPairs, job):

		Process.__init__(self)
		self.job = job #associated job- "parent process"
		self.numPairs = numPairs # number of work items assigned to this node
		self.workList = [] # queue of pending work items
	
	def Run(self):
		global rt

		while self.numPairs > 0:
			print "output pairs remaining", self.numPairs, " from job", self.job.name
			while len(self.workList) > 0:
				print "Reduce:", str(self.workList)
				self.workList.pop(0)
				print "Reducing pair from job number", self.job.name
				completionTime = random.uniform(.5*rt, 1.5*rt)
				self.numPairs -= 1
				yield hold, self, completionTime
			
			if self.numPairs != 0:
				yield passivate, self

		print "updating nodes from reduce"
		self.job.nodes += 1
		
		if self.job.passive():
			print "reactivating job", self.job.name
			reactivate(self.job)
		yield passivate, self


def main():
	initialize()

	cloud = Cloud()

	activate(cloud, cloud.Run())
	simulate(until = 10000)
	print "Total rejections:", Cloud.rejections / float(Cloud.requests)
	print "Avg busy nodes:", (float(sum(avgList))/float(len(avgList)))
if __name__ == "__main__":
	main()