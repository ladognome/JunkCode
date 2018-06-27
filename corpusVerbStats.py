from collections import defaultdict
import csv

verbs = defaultdict(int)
events_from_file = [line.strip() for line in open("miniSents-prepEvents_pruned.txt").readlines()]
with open('verbStats.csv','w') as csvFile:
	writer = csv.writer(csvFile, delimiter=",")
	for line in events_from_file:
		if "%%%%%%%%%%%%%%%%%" in line:
			continue
		elif "<EOS>" in line:
			continue
		else:
			(e,sentence) = line.split(";")
			events = eval(e)
			for event in events:
				[agent, verb, patient, theme, prep] = event
				verb_base = verb
				if "-" in verb:
					ind = verb.index("-")
					if verb[ind+1].isdigit():
						verb_base = verb.split("-")[0]
						verb_base += "[vn]"				
				verbs[verb_base]+=1
	for key in verbs.keys():
		writer.writerow([key,verbs[key]])
