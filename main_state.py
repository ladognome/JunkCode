from sentSim import EventCluster
from corpus import Corpus
from improvEvent import ImprovEvent
from tempimprovGenerator import ImprovGenerator
from manipulateState import *
from objectMemory import ObjectMemory
import copy
import networkx as nx
from operator import itemgetter

# read in clusters for word2vec sentence matching
#cluster_files = [("modbank", "./data/modernBankRobbery/modernBankRobbery.gold"), ("oldbank", "./data/oldWesternRobbery/oldWesternRobbery.gold")]
cluster_files = [("oldbank", "./data/oldWesternRobberyCombinedReduced/oldWesternRobberyCombinedReduced.gold")]
#cluster_files = [("airport", "./data/airport/airportGold.gold")]
eventCluster = EventCluster(cluster_files)


# read in exhaustive stories for hmm processing
#corpus_files = [("fastfood", "./data/fastfood_stories.txt"), ("sitdown", "./data/sitdown_stories.txt"), ("modbank", "./data/modern_bank_stories.txt"), ("oldbank", "./data/western_bank_stories.txt")] #, "./data/plane_stories.txt", "./data/train_stories.txt"]
corpus_files = [("oldbank", "./data/combined_reduced_bank_stories.txt")]
#corpus_files = [("airport", "./data/plane_stories_small.txt")]
corpus = Corpus(corpus_files)



improv_gen = ImprovGenerator(corpus)
improv_event = ImprovEvent()

user_input = ["STORY_INIT"]
previously_state_cal = {}
####State Information####
memoryGraph = ObjectMemory()
states = []
state_track = ["STORY_INIT"]  #this is for constituency testing


def updateState(next_event):
	newState = None
	
	if not states:
		newState = ManipulateState(next_event)
	else:
		newState = ManipulateState(next_event, facts=copy.deepcopy(states[-1].facts))
	states.append(newState)
	memoryGraph.add_event(newState.currentlyMentioned)
	memoryGraph.connect_location(newState.currentlyMentioned) #update the graph with new spatial edges ##TODO make sure that it's just the most recent
	print()
	print("GRAPH")
	for node in memoryGraph.graph.nodes():
		print(node +": "+str(list(nx.all_neighbors(memoryGraph.graph, node))))
	print()


def pickConstituent(event):
	constituents = improv_gen.getConstituents(event.lower())
	const = random.choice(constituents)
	sents = [item for item in eventCluster.originals[0][1] if const in item[0]]#pick a sentence from this constituent; 0 is "oldbank", 1 is the list of things for "oldbank"
	sents = sents[0][1]
	newsent = random.choice(sents)
	newsent = newsent[0].upper()+newsent[1:]
	return const, newsent


def createResponse():
	print()
	found = ""
	while not found:
		found = states[-1].generate_response(memoryGraph) #mode can be relevant or random, relevant as default
	print("AI TURN: "+found)
	updateState(found)
	state_track.append(found)

def antiException(user_turn, cons):
	#exception is if you cannot take the following states without making some logical error
	#(i.e. not all the items necessary for this state are accessible and/or near)
	curr_facts = states[-1].facts
	#print(curr_facts)
	for con in cons:
		_, picked_sentence = pickConstituent(con)
		print(picked_sentence)
		newState = ManipulateState(picked_sentence).facts
		previously_state_cal[con] = newState
		exception = False
		#if there is something that is not in curr_facts that is in the memory && that is in newState
		for fact in newState.keys():
			if fact in memoryGraph.graph.nodes() and not fact in curr_facts: #it used to exist but is now not accessible
				exception = True
				break
		if not exception:
			return con #this one works, return it
	return None

def newSentence(prev, user_event):
	constituents = improv_gen.getConstituents(prev) #get the last added state's name and find its constitutents
	print("Constituents:")
	print(constituents)
	#check for exception
	solution = antiException(user_event, constituents)
	print("Anti-Exception:")
	print(solution)
	if not solution: #exception
		#update the plot graph to plan your way back
		#pick a new sentence in this plot graph
		#or just complain for now

		print("Exception found.")
		createResponse()
		return False

	#consistent
	print("Consistent")
	createResponse()
	sents = [item for item in eventCluster.originals[0][1] if solution in item[0]]#pick a sentence from this constituent; 0 is "oldbank", 1 is the list of things for "oldbank"
	sents = sents[0][1]
	newsent = random.choice(sents)
	newsent = newsent[0].upper()+newsent[1:]
	print()
	print("AI TURN: "+newsent)
	print()
	updateState(newsent)
	state_track.append(solution)
	return True



for counter in range(30):
	next_event = input("What are you going to do?\n>> ")
	user_input.append(next_event)

	#cluster comparison
	prev_event = state_track[-1] #AI turn
	event_dist = eventCluster.find_max_cluster(next_event)
	filtered_event = improv_event.push_event(event_dist) #possible plot points
	updateState(next_event) #add to state

	if filtered_event is not None:
		sort = sorted(list(filtered_event), key=itemgetter(1), reverse=True)
		#print(sort[0][1])
		event = sort[0][0][0].upper()+sort[0][0][1:] #always pick the highest-ranked sentence
		#print(event)
		if improv_gen.isConstituent(prev_event,event.lower()): #is a constitutent
			print("Constituent")
			cons = improv_gen.getConstituents(event)
			#if not antiException(prev_event, cons): #not "STORY_INIT" in prev_event and
			#	newSentence(prev_event,next_event)
			#	state_track.append(next_event)
			#	print("Past exception found.")
			#	quit()
			state_track.append(event) #this is for constituency testing

			#AI			
			const, newsent = pickConstituent(event) #pick a constituent
			print()
			print("AI TURN: "+newsent)
			print()
			updateState(newsent)
			state_track.append(const)
		else: #not a constituent
			newSentence(prev_event,next_event)
			state_track.append(next_event)
	else: #no matching sentences in graph
		newSentence(prev_event,next_event)
		state_track.append(next_event)

	#for state in states:
	#	print(state.facts)
	print(states[-1].facts)

		
		
