from SimPy.Simulation import *
import random



class Cloud(Process):
	availableNodes = 400
	rejections = 0
	def Run(self):
		while True:
			job = JobGenerator.queue.pop(0)
			if job.nodes > availableNodes:
				rejections += 1
			else:
				availableNodes -= job.nodes
				activate(job, job.Run())

			yield passivate, self

			#calculate stats

class UserJob():
	def __init__(self, curTime):
		pass
	def Run(self):
		#calculate all the timing stuff
		yield hold, self, self.jobTime
		if stats.passive():
			reactivate(stats)

class Stats():

	def Run(self):
		#calculate
		yield passivate, self

class JobGenerator(Process):
	queue = []
	def Run(self):
		while True:
			queue.append(UserJob(now()))
			if cloud.passive():
				reactivate(cloud)
			yield hold, self, random.expovariate()


def main():
	cloud = Cloud()
	jobGen = JobGenerator()
	stats = Stats()
	activate(stats, stats.Run())
	activate(jobGen, jobGen.Run())
	activate(cloud, cloud.Run())
	simulate(until = 1000)