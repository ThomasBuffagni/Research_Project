# Author : Thomas Buffagni
# Latest revision : 02/14/2019

from new_structure.modules.utils import parseCommandLine, getText
from new_structure.modules.sample_functions import posFunction, lemmatizingFunction
from new_structure.modules.sample_functions import verbNounFinder, adjNounFinder #Candidate finding functions
from new_structure.modules.darkthoughts import darkthoughtsFunction #Metaphor labeling function
from new_structure.modules.cluster_module import clusteringFunction #Metaphor labeling function
from new_structure.modules.registry import Registry
from new_structure.modules.MetaphorIdentification import MetaphorIdentification

if __name__ == "__main__":

	args = parseCommandLine()

	#Hash table creation
	metaphorRegistry = Registry()
	metaphorRegistry.addMLabeler("darkthoughts", darkthoughtsFunction)
	metaphorRegistry.addMLabeler("cluster", clusteringFunction)
	metaphorRegistry.addCFinder("verbNoun", verbNounFinder)
	metaphorRegistry.addCFinder("adjNoun", adjNounFinder)


	text = getText(args)
	cFinderFunction = metaphorRegistry.getCFinder(args.cfinder)
	mLabelerFunction = metaphorRegistry.getMLabeler(args.mlabeler)

	#Object declaration
	object = MetaphorIdentification(text)

	#Annotating the text
	object.annotateText()
	object.annotTextAddColumn("POS", posFunction)  # Set a part-of-speech to each word of the string
	object.annotTextAddColumn("lemma", lemmatizingFunction)  # Set a lemma to each word of the string
	if args.verbose:
		print(object.getAnnotatedText())

	#Finding candidates
	object.findCandidates(cFinderFunction)
	if args.verbose:
		print(object.getCandidates())

	#labeling Metaphors
	object.labelMetaphors(mLabelerFunction, args.verbose)
	if args.verbose:
		print(object.getMetaphors())