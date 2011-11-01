from SimPy.Simulation import *
import math
import random


curJob = 0
avgList = []
ct = 0.1
rt = 10.0
mean_kv = 20.0
max_req = 2
mean_arriv = 5.0
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

			yield hold, self, random.expovariate(mean_arriv)


class UserJob(Process):
	def __init__(self, numNodes):
		global curJob
		curJob += 1
		Process.__init__(self, name = str(curJob))
		self.nodes = Resource(capacity = numNodes, name = "nodes")
		print "Assigned ", self.nodes.n, " nodes to job", str(curJob)
		self.numNodes = numNodes
		self.numPairs = self.getInputPairs()
		self.totalPairs = self.numPairs*numNodes


	def Run(self):
		global avgList

		for i in range(self.numNodes-1):
			mnode = MapNode(self.numPairs, self)
			activate(mnode, mnode.Run())
		
		self.rnode = ReduceNode(self.totalPairs, self)
		activate(self.rnode, self.rnode.Run())

		dummy = Resource(1)
		yield request, self, dummy

		print "activeQ length", len(self.nodes.activeQ)
		while True:
			if len((self.nodes.activeQ)) == 0:

				avgList.append(size - Cloud.availableNodes)
				Cloud.activeJobs.remove(self)
				Cloud.availableNodes += self.numNodes
				break
			yield passivate, self
		print "Sleeping job", self.name

	def getInputPairs(self):
		''' Gives the number of input pairs per map node '''
		numPairs = math.ceil(self.geomvariate()*self.numNodes)
		
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
		yield request, self, self.job.nodes
		print "Requested a node from", self.job.name

		while len(self.workList) != 0:
			pair = self.workList.pop(0)
			print "Processing work item, completion time = ", pair
			yield hold, self, pair
			self.job.rnode.workList.append(pair)
			if self.job.rnode.passive():
				reactivate(self.job.rnode)
		yield release, self, self.job.nodes
		yield passivate, self


class ReduceNode(Process):
	def __init__(self, numPairs, job):

		Process.__init__(self)
		self.job = job #associated job- "parent process"
		self.numPairs = numPairs # number of work items assigned to this node
		self.workList = [] # queue of pending work items
	
	def Run(self):
		global rt
		yield request, self, self.job.nodes # grab one node resource

		while self.numPairs > 0:
			if len(self.workList) > 0:
				self.workList.pop(0)
				completionTime = random.uniform(.5*rt, 1.5*rt)
				yield hold, self, completionTime
				self.numPairs -= 1
			if self.numPairs != 0:
				yield passivate, self

		if self.job.passive():
			print "reactivating job", self.job.name
			reactivate(self.job)
		yield release, self, self.job.nodes
		yield passivate, self


def main():
	initialize()

	cloud = Cloud()

	activate(cloud, cloud.Run())
	simulate(until = 1000)
	print "Total rejections:", Cloud.rejections / float(Cloud.requests)
	print "Avg busy nodes:", (float(sum(avgList))/float(len(avgList)))
if __name__ == "__main__":
	main()