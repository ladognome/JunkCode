 # -*- coding: utf-8 -*-
#!/usr/bin/env python3
from __future__ import print_function
import argparse, os, copy, random, subprocess
from getEventandSpecificsPersistence import digestSentence
from nltk.corpus import wordnet as wn
from collections import defaultdict 
import decode
from memoryGraph import MemoryGraph


#noun_dict = defaultdict(list)
memory = MemoryGraph()


def pickRandoName(nameList):
	directory = os.path.join(os.getcwd(), "names")
	f = os.path.join(directory, random.choice(os.listdir(directory)))
	names = [w.split(",")[0] for w in open(f, 'r').readlines()]
	random.shuffle(names)
	name_select = ""
	index = 0
	while True:
		if name_select not in nameList:
			return names[index]
		index+=1

def appendToFile(filename, string):
	openFile = open(filename, "a")
	openFile.write(string)
	openFile.close()

def pickNoun(cat):
	#print(cat)
	#TODO: change "he" to sometimes be "him"/"his", etc. from position
	if cat == "Synset('male.n.02')":
		return "he"
	if cat == "Synset('female.n.02')":
		return "she"
	if cat == "Synset('physical_entity.n.01')":
		return "they"
	if cat == "Synset('entity.n.01')":
		return "it"
	if cat == "Synset('person.n.01')":
		return "I"
	try:
		_,category,_ = cat.split("'")
		category = category.split(".")[0]
	except:
		return cat
	try:
		synset = wn.synsets(category)
		#print(synset)
		for syn in synset:
			if str(syn) == cat:				
				hypo = list(syn.hyponyms())
				break			
		#print(hypo)
		random.shuffle(hypo)
		_,selection,_ = str(hypo.pop()).split("'")
		return selection.split(".")[0].replace("_"," ")
	except:
		return category


def checkFirstWord(sentence):
	words = sentence.split(" ")
	if words[0].lower() in ["that", "while", "which", "when", "who", "since", "because", "meanwhile"]:
		words = words[1:]
	words[0] = words[0][0].upper()+words[0][1:]
	return " ".join(words)


#TODO: assign consistent numbers to NEs?
def fillIn(emptySent):
	global memory
	event_nouns = []
	filledSent = []
	NEdictionary = defaultdict(str)
	NElist = []
	for i, category in enumerate(emptySent.split(" ")):
		#print(category)
		if category == ".":
			break
		if category == "Synset('entity.n.01')":
			filledSent.append("that")
		elif "<NE>" in category: #if it's a named entity
			if category in NEdictionary: #if this <NE> is in the dictionary already, use the same name
				filledSent.append(NEdictionary[category])
				event_nouns.append((NEdictionary[category], "NE"))
			else:
				newName = memory.find_recent_item(category, name=True, NElist=NElist)
				if not newName: #nothing in memory
					newName = pickRandoName(NElist)
				filledSent.append(newName)
				NEdictionary[category] = newName
				NElist.append(newName)
				event_nouns.append((newName, "NE"))
		elif "Synset(" in category: #it's a synset
			word = memory.find_recent_item(category)
			if word:
				filledSent.append(word)
				event_nouns.append((word, "noun"))
			else:
				picked = pickNoun(category)
				filledSent.append(picked)
				event_nouns.append((picked, "noun"))
		else: #regular word
			filledSent.append(category)
			
	final_sent = " ".join(filledSent)+"."
	final_sent = final_sent[0].upper() + final_sent[1:]
	return final_sent, event_nouns


print("Let's tell a story! Type \"<quit>\" to quit.")
while(True):
	print("YOU >> ",end="")
	next_event = str(input()) #raw_input for python2
	if "<quit>" in next_event:
		quit()
	else:
		if next_event[-1] != ".":
			next_event+="."
		#appendToFile(args.output,"User: "+next_event+"\n")
		#get noun dictionary & event
		digested = digestSentence(next_event)
		v, ns = digested.eventAndNoun()
		memory.add_event(v,ns)
		event = " ".join([tok for evt in digested.events for tok in evt])

		print("#########EVENT 1#########")
		print(event)
		quit()
		#appendToFile(args.output, "Event1: "+event+"\n")

		#give event to event2event RNN
		event2 = decode.pipeline_predict(event, "config_genEvt_to_genEvt.json", "dummy")[0]
		print("#########EVENT 2#########")
		#print(event2)
#		e2 = " ".join(event2.split(" ")[:4])
		e2 = event2
		event2 = event2.split(" ")
		print(e2)
		#appendToFile(args.output, "Event2: "+event2+"\n")


		print("########SENTENCE 2########")
		#give event to event2sentence RNN
		sentence = decode.pipeline_predict(e2, "config_genEvt_to_condensedSent.json", "dummy")[0]
		sentence = checkFirstWord(sentence)
		#sentence = decode.pipeline_predict(' '.join(event2), "config_allgenevts_to_gensents.json", "dummy")[0]
		print(sentence)

		#agent's response
		agentTurn, agent_nouns = fillIn(sentence) #agentTurn,newNouns = fillIn(sentence, noun_dict)
		memory.add_event(event2[1],agent_nouns)
		print("AI >> " +agentTurn)
		print("############################################")

