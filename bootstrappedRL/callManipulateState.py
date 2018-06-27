from collections import defaultdict
from manipulateState import ManipulateState

"""
#e="['<ORGANIZATION>4', 'remove-10.1', '<PERSON>0', '<ORGANIZATION>2', 'from']"
#e="[\"Synset('actinic_radiation.n.01')\", 'meander-47.7', 'EmptyParameter', 'EmptyParameter', 'EmptyParameter']"
e="[\"Synset('male.n.02')\", 'comprehend-87.2-1-1-1', 'EmptyParameter', 'EmptyParameter', 'EmptyParameter']"
state = ManipulateState(eval(e),None)
print(str(state.currentlyMentioned))
quit()
"""


events_from_file = [line.strip() for line in open("miniSents-prepEvents_pruned.txt").readlines()]
#print(events_from_file)
story_events = []
prev_state = None
for line in events_from_file:
	if "%%%%%%%%%%%%%%%%%" in line:
		line = line.replace("%%%%%%%%%%%%%%%%%","")
		named_entities = eval(line.replace("<class 'list'>", 'list'))
		for event in story_events:
			eventList = eval(event)
			e = eventList[0]
			if len(eventList) > 1:
				for event in eventList:
					if not "-" in event[2]:
						break
					e = event						
			cur_state = ManipulateState(e,named_entities)
			cur_state_obj = new_state.changePredicateObject
			new_state = cur_state_obj.canBeNext(prev_state)
			if new_state: #canBeNext will return None if it can't
				print(str(e)+";;;"+str(new_state))
			#print(str(e)+ ";;;" + str(state.currentlyMentioned))
		quit()
		story_events = []		
	elif "<EOS>" in line:
		print("<EOS>")
	else:
		(e,sentence) = line.split(";")
		story_events.append(e)


"""
#TODO: this needs prepositions
events_from_file = [line.strip() for line in open("genEvent-genSent-full-newVerb.txt").readlines()]
story_events = []
for line in events_from_file:
	if "%%%%%%%%%%%%%%%%%" in line:
		line = line.replace("%%%%%%%%%%%%%%%%%","")
		named_entities = eval(line.replace("<class 'list'>", 'list'))
		for event in story_events:
			eventList = eval(event)
			e = eventList[0]
			if len(eventList) > 1:
				for event in eventList:
					if not "-" in event[2]:
						break
					e = event						
			state = ManipulateState(e,named_entities)
			#if state.currentlyMentioned:
			print(str(e) + ";;;" + str(state.currentlyMentioned))
		quit()
		story_events = []		
	elif "<EOS>" in line:
		print("<EOS>")
	else:
		split = line.split(";")
		if len(split) > 3:
			e = split.pop(0)
			gen_sent = split.pop(0)
			sentence = "; ".join(split)
		else:
			(e,gen_sent,sentence) = line.split(";")
		story_events.append(e)
"""
