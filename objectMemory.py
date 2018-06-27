# -*- coding: utf-8 -*-
import networkx as nx
import random

class ObjectMemory:
	def __init__(self):
		""" Creating a new event node that keeps track of the previous event and pointers to all things mentioned in this timestep
		"""
		self.graph = nx.Graph()
		self.index = 0
		self.recentlyMentioned = {}

	def add_event(self, thingsMentioned):
		self.recentlyMentioned = thingsMentioned
		#create a new event node
		eventString = "E"+str(self.index)
		newEvent = self.graph.add_node(eventString)
		#connect all recently-mentioned things to this node
		for thing in thingsMentioned:
			if not thing in self.graph.nodes():
				self.graph.add_node(thing)
			self.graph.add_edge(eventString, thing)
			self.graph.add_edge(thing, eventString)		
		self.index+=1

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
					

	def find_recent_item(self, facts):
		
		if not facts: return ""
		lookup_word = ""
		found = False
		index = self.index-1
		neighbors = list()	
		while not found:
			if index < 0: return ""
			if "Sally" in self.graph: #finds something that Sally can reach and was mentioned recently
				neighbors = list(nx.common_neighbors(self.graph, "E"+str(index), "Sally"))
			if not neighbors: #just finds something that was mentioned recently
				neighbors = list(nx.all_neighbors(self.graph, "E"+str(index)))
			random.shuffle(neighbors)
			for n in neighbors:
				if n in facts:
					lookup_word = n
					found = True
					break
			index-=1 #go back a state and look there
		return lookup_word
		

