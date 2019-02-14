# Author : Henri Toussaint
# Latest revision : 01/19/2017

# Class that identifies the metaphors among the candidates and provides a confidence percentage

class MetaphorLabeler:

	def __init__(self, candidates):
		self.candidates = candidates
		self.metaphors = []

	def LabelMetaphors(self, identificationFunction):
		self.metaphors = identificationFunction(self.candidates)

	def getMetaphors(self):
		return self.metaphors

	def getCandidates(self):
		return self.candidates