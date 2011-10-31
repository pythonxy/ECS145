from SimPy.Simulation import *
import random

avgList = []

class Cloud(Process):
	availableNodes = 400
	rejections = 0
	activeJobs = []

	def Run(self):
		while True:
			job = UserJob()
			if job.nodes > availableNodes:
				rejections += 1
			else:
				availableNodes -= job.nodes
				activate(job, job.Run())
				activeJobs.append(job)

			yield hold, self, random.expovariate()


class UserJob(Process):
	def __init__(self, numNodes):
		nodes = Resource(capacity = numNodes, name = "nodes")

		numPairs = self.getInputPairs()
		totalPairs = numPairs*numNodes

		for i in range(numNodes-1):
			mnode = MapNode(numPairs, self)
			activate(mnode, mnode.Run())
		
		rnode = ReduceNode(totalPairs, self)
		activate(rnode, rnode.Run())

	def Run(self):
		while True:
			if len((nodes.activeQ)) == 0:
				if stats.passive():
					reactivate(stats)
				Cloud.activeJobs.remove(self)
				self.cancel()
			yield passivate, self

	def getInputPairs(self):
		''' Gives the number of input pairs per map node '''
		numPairs = self.geomvariate()
		if numPairs < numNodes:
			 numPairs = 1
		elif (numPairs % numNodes) == 0 
			numPairs = (numPairs / numNodes)
		else:
			numPairs = (numPairs / numNodes) + 1
		return numPairs

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

		self.job = job #associated job- "parent process"
		self.numPairs = numPairs # number of work items assigned to this node
		self.workList = [] # queue of pending work items
		for i in range(numPairs):
			completionTime = random.uniform(.5*ct, 1.5*ct)
			self.workList.append(completionTime)
	
	def Run(self):
		yield request, self, self.job.nodes

		while len(self.workList) != 0:
			pair = self.workList.pop(0)
			yield hold, self, pair
			job.rnode.queue.append(pair)

		yield release, self, nodes
		self.cancel()


class ReduceNode(Process):
	def __init__(self, numPairs, job):

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

		if self.job.passive():
			reactivate(self.job)
		yield release, self, nodes
		self.cancel()


class Stats(Process):
	def Run(self):
		for job in Cloud.activeJobs:
			busyNodes += len(job.activeQ)	
		yield passivate, self

def main():
	cloud = Cloud()
	jobGen = JobGenerator()
	stats = Stats()

	activate(stats, stats.Run())
	activate(jobGen, jobGen.Run())
	activate(cloud, cloud.Run())
	
	simulate(until = 1000)