from collections import defaultdict
import math

selhierarchy= { "+vehicle" :["+machine", "+int-control", "+concrete", "+artifact", "+phys-obj"],
		"+human" :["+concrete", "+animate", "+int-control", "+natural"],
		"+animal" :["+concrete", "+animate", "+int-control", "+natural"],
		"+body-part" :["+concrete", "+animate", "+int-control", "+natural"],
		"+machine" :["+concrete", "+int-control", "+artifact", "+phys-obj"],
		"+garment" :["+concrete", "+artifact", "+phys-obj"],
		"+tool" :["+concrete", "+artifact", "+phys-obj"],
		"+non-rigid" :["+concrete", "+solid"], ##removed rigid
		"+elongated" :["+concrete", "+pointed","+shape"],
		"+force" :["+concrete", "+int-control"],
		"+animate" :["+concrete", "+natural", "+int-control"],
		"+plant" :["+concrete", "+natural"],
		"+comestible" :["+concrete", "+phys-obj"],
		"+biotic" :["+concrete", "+phys-obj"], ##added
		"+artifact" :["+concrete", "+phys-obj"],
		"+rigid" :["+concrete", "+solid"],
		"+pointed" :["+concrete", "+shape"],
		"+int-control" :["+concrete"],
		"+natural" :["+concrete"],
		"+phys-obj" :["+concrete"],
		"+solid" :["+concrete"],
		"+shape" :["+concrete"],
		"+substance" :["+concrete"],
		"+idea" :["+abstract"],
		"+sound" :["+abstract"],
		"+communication" :["+abstract"],
		"+region" :["+location"], ##changed name
		"+place" :["+location"],
		"+object" :["+location"],
		"+concrete" :[],
		"+time" :[],
		"+state" :[],
		"+abstract" :[],
		"+scalar" :[],
		"+currency" :[],
		"+location" :[],
		"+organization" :[],
		"+plural" :["+concrete"], ##added
	}

#TODO: remove contradictory selectors given new, narrower information

#given 2 selrestrs, find the parent
def findMinParent(sel1, sel2):
	interSet = set(selhierarchy[sel1]).intersection(set(selhierarchy[sel2]))
	#the lowest should have the fewest children
	if len(interSet) == 1:
		return interSet[0]
	if len(interSet) < 1:
		return None
	min_parent = None
	min_val = 100
	for sel in interSet:
		if len(selhierarchy[sel]) < min_val:
			min_val = len(selhierarchy[sel])
			min_parent = sel
	return min_parent


#given a set of selrestrs, gives the full set of restrictions (adds corresponding super-categories)
def maxSel(query):
	finalset = set()
	for item in query:
		if "|" in item:
			sel1,sel2 = item.split("|")
			parent = findMinParent(sel1, sel2)
			finalset |= set([parent])
			finalset |= set(selhierarchy[parent])
		else:
			finalset |= set([item])
			if item in selhierarchy:
				finalset |= set(selhierarchy[sel])
	return finalset

#find the minimum set of selectional restrictions
def findMinSel(new, current):
	if current in self.selhierarchy[new]: #current is parent of new
		return [new]
	elif new in self.selhierarchy[current]: #new is parent of current, aka-don't add it
		return [current]
	else: #use both, they're fairly independent
		return [current, new]

#checks against all restrictions in the role
def checkSel(source_ls, role):
	for rest in role: #each restriction
		restriction_satisfied = False
		for r in rest.split("|"):
			if r in source_ls:
				restriction_satisfied = True
				break
		if not restriction_satisfied: #it can't be this 
			return False
	return True

class Predicate:
	def __init__(self,predicate_string,negated=False):
		"""
		Event Classification
		during(E) 	-- occurs during the event (might result in post-conditions)
		E		-- timeless property; can be considered post-condition
		result(E) 	-- developed at end of event; post-condition
		end(E)		-- developed at end of event; post-condition
		start(E)	-- specifies pre-condition
		"""
		self.roles_to_fill = []
		self.time = ""
		self.pre_conditions = set()
		self.post_conditions = set()
		self.predicate = ""
		self.negated = negated

		predicate, roles_to_fill = predicate_string[:-1].split("(",1)
		#print(predicate)
		
		if shouldBeRemoved(predicate): return None
		roles_to_fill = [x.strip() for x in roles_to_fill.split(",")]
		found_event = False
		i = 0
		for i,role in enumerate(roles_to_fill):
			if "E" in role and "<" not in role and "?" not in role:
				#remove the even from the roles but save it as a "time" variable
				#event = roles_to_fill.pop(0)
				event = role
				if "E" == event:
					self.time = "timeless"
				elif "during" in event:
					self.time = "during"
				elif "result" in event or "end" in event:
					self.time = "post"
				elif "start" in event:
					self.time = "pre"
				found_event = True
				break
		if found_event:
			roles_to_fill.pop(i)
		#print(self.time)
		self.roles_to_fill = roles_to_fill
		self.predicate = predicate

		if predicate == "path_rel":
			change_scale = self.dealingWithPathRel()
			if change_scale:
				return None
		#print("ROLES",self.roles_to_fill)
		#print(self.predicate+"("+",".join(self.roles_to_fill)+")")


	def dealingWithPathRel(self):
		new_predicate_label = ""
		index = 0
		if "ch_of_state" in self.roles_to_fill:
			new_predicate_label="state"
			self.roles_to_fill.pop(self.roles_to_fill.index("ch_of_state"))
		elif "ch_of_loc" in self.roles_to_fill:
			new_predicate_label="location"
			self.roles_to_fill.pop(self.roles_to_fill.index("ch_of_loc"))
		elif "ch_of_poss" in self.roles_to_fill or "ch_of_pos" in self.roles_to_fill:
			try:
				index = self.roles_to_fill.index("ch_of_pos")
			except:
				index = self.roles_to_fill.index("ch_of_poss")
			self.roles_to_fill.pop(index)
			new_predicate_label="has_possession"
		elif "tr_of_info" in self.roles_to_fill:
			new_predicate_label="understand"
			self.roles_to_fill.pop(self.roles_to_fill.index("tr_of_info"))
		elif "ch_on_scale" in self.roles_to_fill: #I don't entirely understand this one
			#new_predicate_label="change_value"
			return True
		else:
			raise ValueError("Unknown path_rel type: ",",".join(self.roles_to_fill))
		self.predicate = new_predicate_label
		return False

	def changeToCorePredicates(self):#,unchangedState,sels,rev_roles):
		#Updates predicates to only be "core predicates"; core predicates are marked with ###
		#Changes pre- & post-conditions of predicates
		name = self.predicate
		"""
		if name == "about":
		elif name == "act":
		elif name == "adjust":
		elif name == "admit":
		elif name == "adopt":
		elif name == "agree":
		"""
		if name == "alive":###
			return "alive("+self.roles_to_fill[0]+")"
		"""
		elif name == "allow":
		elif name == "apart":
		elif name == "appear":
		elif name == "apply_heat":
		elif name == "approve":
		if name == "assess":
		if name == "attempt":
		if name == "attract":
		if name == "authority_relationship":
		if name == "avoid":
		if name == "base":
		if name == "begin":
		if name == "believe":
		if name == "benefit":
		if name == "body_motion":
		if name == "body_process":
		if name == "calculate":
		if name == "capacity":
		if name == "cause":
		if name == "change_value":
		if name == "characterize":
		if name == "charge":
		if name == "conclude":
		if name == "confined":
		if name == "conflict":
		"""
		if name == "confront":
			#Agent,Theme,Instrument
			self.pre_conditions.add("has_possession("+self.roles_to_fill[0]+","+self.roles_to_fill[2]+")")
			self.post_conditions.add("confront("+",".join(self.roles_to_fill)+")")
			#if "+concrete" in sels[rev_roles[self.roles_to_fill[1]]] or "<PERSON>" in self.roles_to_fill[1]: #Theme
			#	self.post_conditions.add("together("+self.roles_to_fill[0]+","+self.roles_to_fill[1]+")")
		"""
		if name == "consider":
		if name == "conspire":
		if name == "contact":
		if name == "contain":
		if name == "continue":
		if name == "convert":
		if name == "cooked":
		if name == "cooperate":
		if name == "cope":
		if name == "correlate":
		if name == "cost":
		if name == "covered":
		if name == "created_image":
		if name == "declare":
		if name == "dedicate":
		if name == "defend":
		if name == "degradation":
		if name == "delay":
		if name == "depend":
		if name == "describe":
		if name == "designated":
		if name == "desire":
		if name == "destroyed":
		if name == "different":
		if name == "direction":
		if name == "disappear":
		if name == "discomfort":
		if name == "discover":
		if name == "do":
		if name == "earn":
		if name == "emit":
		if name == "emotional_state":
		if name == "end":
		if name == "enforce":
		if name == "ensure":
		if name == "equals":
		if name == "exceed":
		if name == "exert_force":
		if name == "exist":
		if name == "experience":
		if name == "express":
		if name == "filled_with":
		if name == "financial_relationship":
		if name == "flinch":
		"""
		if name == "free": #the act of freeing
			self.pre_conditions.add("confined("+",".join(self.roles_to_fill)+")")
			self.post_conditions.add("!confined("+",".join(self.roles_to_fill)+")")
		if name == "function":###
			return "function("+",".join(self.roles_to_fill)+")"
		"""
		if name == "give_birth":
		if name == "group":
		if name == "harmed":
		if name == "harmonize":
		"""
		if name == "has_possession":###
			return "has_possession("+",".join(self.roles_to_fill)+")"
		"""
		if name == "help":
		if name == "in_reaction_to":
		if name == "indicate":
		if name == "involuntary":
		if name == "involve":
		if name == "license":
		if name == "limit":
		if name == "linger":
		"""
		if name == "location":### X is at location Y
			return "location("+",".join(self.roles_to_fill)+")"
		if name == "made_of":###
			return "made_of("+",".join(self.roles_to_fill)+")"
		if name == "manner":###?
			return "manner("+",".join(self.roles_to_fill)+")"
		"""
		if name == "masquerade":
		if name == "mingled":
		"""
		#if name == "motion":
		"""
		if name == "necessitate":
		if name == "neglect":
		if name == "nonagentive_cause":
		if name == "occur":
		if name == "has_possession":
		if name == "perceive":
		if name == "perform":
		if name == "physical_form":
		if name == "promote":
		if name == "property":
		if name == "relate":
		if name == "require":
		if name == "risk":
		if name == "rotational_motion":
		if name == "rush":
		if name == "satisfy":
		if name == "search":
		if name == "seem":
		if name == "set_member":
		if name == "signify":
		if name == "sleep":
		if name == "social_interaction":
		if name == "spend":
		if name == "subjugated":
		if name == "successful_in":
		"""
		if name == "suffocate":
			self.pre_conditions.add("alive("+",".join(self.roles_to_fill)+")")
			self.post_conditions.add("!alive("+",".join(self.roles_to_fill)+")")
		"""
		if name == "support":
		if name == "suspect":
		if name == "take_care_of":
		if name == "take_in":
		if name == "think":
		if name == "time":
		"""
		if name == "together":### X and Y are together (near)
			return "together("+",".join(self.roles_to_fill)+")"
		#if name == "transfer_info":
		#	print(self.roles_to_fill)
		#	self.pre_conditions.add("understand("+self.roles_to_fill[0]+","+self.roles_to_fill[2]+")")
		#	self.post_conditions.add("understand("+self.roles_to_fill[1]+","+self.roles_to_fill[2]+")")
		#if name == "transfer":
		#	self.pre_conditions.add("has_possession("+",".join(self.roles_to_fill)+")")

		if name == "understand":
			return "understand("+",".join(self.roles_to_fill)+")"
		"""
		if name == "urge":
		if name == "use":
		"""
		if name == "utilize":
			self.pre_conditions.add("has_possession("+",".join(self.roles_to_fill)+")")
			self.pre_conditions.add("function("+self.roles_to_fill[1]+")")
		"""
		if name == "value":
		if name == "visible":
		if name == "void":
		if name == "wear":
		if name == "withdraw":
		if name == "work":
		if name == "yield":	
		"""
		return None
		
class Entity:
	def __init__(self,roles):
		self.attributes = []
		self.state = []
		self.relations = []
		self.possesions = []
		self.location = ""
		

def shouldBeRemoved(predicate):
	#remove these predicates because they are redundant or are verb-specific
	removal_list = ["financial_interest_in","body_reflex","Adv","weather","position","apply_material","attached","meets","state","transfer","equals","meets","transfer_info"]
	if predicate in removal_list:
		return True
	return False

#def mutuallyExclusivePredicates(P1, P2):
	

class ChangePredicate:
	def __init__(self,predicates,roles,unchangedState,sels):
		self.unchanged_state = unchangedState
		self.sels = sels
		self.new_state = None
		print("Pre-changed STATE",unchangedState)
		self.predicates = predicates
		self.roles = roles
		#self.new_preds = defaultdict(dict) #new_preds[entity] = {attributes:[], state:[], relations:[]}
		#for r in roles:
		#	self.new_preds[r] = {"attributes":[],"state":[],"relations":[]}
		self.pre_conditions = set()
		self.post_conditions = set()
		self.cause = ""
		cause_ind = -1
		#print("ROLES",roles)

		rev_roles = {}
		for r in self.roles.keys():
			val = self.roles[r]
			rev_roles[val] = r
		self.rev_roles = rev_roles

		for i,p in enumerate(self.predicates):
			if "cause" == p.predicate:
				cause_ind = i
				break
		if cause_ind > -1:
			self.cause = self.predicates[cause_ind].roles_to_fill[0]
			self.predicates.pop(cause_ind)
		for pred in self.predicates:
			#print(pred.predicate)
			core = pred.changeToCorePredicates()#unchangedState,sels,rev_roles)
			if core: #this is a core predicate, it should go depending on the start/end of the "event"
				if pred.negated:
					core = "!"+core
				if pred.time == "pre":
					self.pre_conditions.add(core)
				elif pred.time == "post":
					self.post_conditions.add(core)
				#else: #during
				#	self.post_conditions.add(core)
			else:
				self.post_conditions |= pred.post_conditions
				self.pre_conditions |= pred.pre_conditions
		print("Pre: "+str(self.pre_conditions))
		print("Post: "+str(self.post_conditions))
		print("Cause: "+self.cause)

	def checkSelrestrs(self, prev_state):
		#for each entity in the previous state
		for entity in prev_state.keys():
			if entity in self.rev_roles:
				#pull out the restrictions that the role requires in this verb
				role = self.rev_roles[entity]
				role_sels = self.sels[role]
				#pull out all of the restrictions it currently has
				prev_sels = [x for x in prev_state[entity] if (x.startswith("+") or x.startswith("-"))]
				#compare to make sure that the restrictions of the entity are equal to or children of the restrictions of the verb (e.g. "+animate" can be filled with someone who has "+person" unless explicitly made "-animate")
				for new_sel in role_sels:
					satisfied_restriction = checkSel(prev_sels, new_sel)
					if not satisfied_restriction:
						return False
		return True
					

	def checkPredicates(self, prev_state):
		prev_preds = 
		#if x and y are in different locations, they can't be together(x,y)
		#-concrete can't have location
		#!alive becomes -animate
		#+animal & !alive --> +comestible


	def canBeNext(self, prev_state):
		#TODO: fill self.new_preds based on old state and self.post_conditions
		next_state = {}
		NER = {"<PERSON>":["+human"],
			"<LOCATION>":["+location"],
			"<ORGANIZATION>":["+organization"],
			"<DURATION>":["+time"],
			"<DATE>":["+time"],
			"<OBJECT>":["+artifact"],
			"<VESSEL>":["+machine","+vehicle"]}
		selRestrsAreGood = self.checkSelrestrs(prev_state)
		if selRestrsAreGood:
			predicatesAreGood = self.checkPredicates(prev_state)
			if predicatesAreGood:
				#update the state
				for entity in self.unchanged_state.keys():
					if entity in self.rev_roles: #the entity should be updated
					else: #nothing happened with it, leave it alone
						next_state[entity] = self.unchanged_state[entity]
					role = self.rev_roles[entity]
					role_sels = self.sels[role]
					print("ROLE_SELS",entity,role,role_sels)
				for entity in self.rev_roles:
					if entity not in next_state:
						#add it
						next_state[entity] = set()
						for sel in self.rev_roles[entity]:
							next_state[entity] |= maxSel(sel)
						if entity.split(">")[0]+">" in NER:
							next_state[entity] |= maxSel(NER[entity.split(">")[0]+">"])

		return next_state






