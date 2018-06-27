events_from_file = [line.strip() for line in open("miniSents-prepEvents_pruned.txt").readlines()]
story_events = []
with open('SciFi-Prep-Events.txt', 'w') as outfile:
	for line in events_from_file:
		if "%%%%%%%%%%%%%%%%%" in line:
			outfile.write(",".join(story_events))
			outfile.write("\n,\n")
			story_events = []		
		elif "<EOS>" in line:
			continue
		else:
			(e,sentence) = line.split(";")
			events = eval(e)
			for event in events:
				story_events.append(" ".join(event))
