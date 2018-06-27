# -*- coding: utf-8 -*-
import networkx as nx
import random
from nltk.corpus import wordnet as wn

class MemoryGraph:
	def __init__(self):
		""" Creating a new event node that keeps track of the previous event and pointers to all things mentioned in this timestep
		"""
		self.graph = nx.DiGraph()
		self.graph.add_node("-")
		self.prev = -1

	def add_event(self, verb, thingsMentioned):
		self.prev+=1
		#create a new event node
		eventString = "E"+str(self.prev)
		newEvent = self.graph.add_node(eventString, verb=verb)
#		self.graph.add_edge(eventString, self.prev)
		#connect all recently-mentioned things to this node
		for (thing, what) in thingsMentioned:
			if not thing in self.graph.nodes():
				self.graph.add_node(thing, att=what)
			self.graph.add_edge(eventString, thing)
			self.graph.add_edge(thing, eventString)	
		

	def connect_location(self, facts):
		#connects spatially-close items together in the graph
		for thing in self.recentlyMentioned:
			if not thing in facts: continue
			for fact in facts[thing]:
				if (not "not(" in fact) and "near(" in fact:
					split = fact.split(",")
					if "near(E" in split[0] or "near(end(E)" in split[0]: #it's during or at the end of the event
						self.graph.add_edge(split[1], split[2][:-1]) #connect the nodes
				elif "not(" in fact and "near(" in fact:
					split = fact.split(",")
					if "not(near(E" in split[0] or "not(near(end(E)" in split[0]: #it's during or at the end of the event
						try: self.graph.remove_edge(split[1], split[2][:-1]) #disconnect the nodes
						except: pass
					

	def find_recent_item(self, category, name=False, NElist=[]):
		#print(category)
		index = self.prev
		neighbors = list()	
		while True:
			if index < 0: return ""
#			if "Sally" in self.graph: #finds something that Sally can reach and was mentioned recently
#				neighbors = list(nx.common_neighbors(self.graph, "E"+str(index), "Sally"))
#			if not neighbors: #just finds something that was mentioned recently
			neighbors = list(set(nx.all_neighbors(self.graph, "E"+str(index))))
			random.shuffle(neighbors)
			att = nx.get_node_attributes(self.graph, "att")
			#print(att)
			for n in neighbors:
				#print("N: "+n)
				if att[n] == "NE" and name:
					if n not in NElist:
						return n
				elif not name and att[n] == "noun":
					try:
						nsyn = wn.synsets(n)[0]
						_, cat, _ = category.split("'")
						csyn = wn.synset(cat)
						lowest = nsyn.lowest_common_hypernyms(csyn)
						#print(str(lowest))
						if category in str(lowest):
							return n
					except:
						continue
			index-=1 #go back a state and look there
		return None
		


