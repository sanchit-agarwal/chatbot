import re

class RuleBasedDialog:


    intent_lookup_table = (
         'affirm',
	 'book',
	 'confirm',
	 'goodbye',
	 'greeting',
	 'inform',
	 'moreinfo',
	 'negate',
	 'request',
	 'request_alts',
	 'request_compare',
	 'switch_frame',
	 'thankyou')


    def __init__(self):
        print("")
    
    def get_intent(self, userInput):
        
        ask_question_regex = r"(.*) book (.*)"
        clarity_regex = r"Do|What|Are|Can (.*)"
        new_query_regex = r"(.*) trip|package|options (.*)"
        affirm_regex = r"(.*) confirm|okay|book|take (.*)"
        negate_regex = r"(.*) no|nope (.*)"
        
        if re.match(ask_question_regex, userInput):
            return "inform"
        elif re.match(clarity_regex, userInput):
            return "clarity"
        elif re.match(new_query_regex, userInput):
            return "new_query"
        elif re.match(affirm_regex, userInput):
            return "affirm"
        else:
            return "negate"
        
    def dialog_policy(self, intent, previousStates, transitions):
    
    
    
    
    
    
       
    
    
    
    
    
    
    
    
    
    
        if intent == "inform" and previousStates[-1] == "greetings":
            return [x for x in transitions if x["trigger"] == "ask_question"][0]
        
        elif intent == "clarity" and previousStates[-1] == "inform":
            return [x for x in transitions if x["trigger"] == "clarity"][0]
        
        elif intent == "confirm" and previousStates[-1] == "inform":
            return [x for x in transitions if x["trigger"] == "confirm"][0]
        
        elif intent in ["affirm", "thankyou", "goodbye"] and previousStates[-1] == "affirm":
            return [x for x in transitions if x["trigger"] == "affirm_end"][0]
        
        elif intent == "switch_frame" and previousStates[-1] == "affirm":
            return [x for x in transitions if x["trigger"] == "ask_question"][0]
        
        
        
        
        

class DialogFrame:
    """ Knowledge representation for the Trip package booking """
    
    slot = {
      "dst_city" = None,
      "sou_city" = None,
      "budget" = None,
      "start_date" = None,
      "end_date" = None,
      "people" = None
    }
    
    def __init__(object):
        print("Initializing Dialog Frame")
        
    
    def checkForAllInfo(self):
    
        remaining_slots = []
        
    	for key, value in self.slot.items():
    		if value is None:
    			remaining_slots.append(key)
    
    
    	return remaining_slots
    
        
    def extract_entities(self, userInput):
        
        #Regex based NER 
        
        """source_regex = r"(.*) from|source (.*)"
        destination_regex = r"(.*) to|destionation (.*)"
        budget = r"(.*) budget|spend|money \d+ (.*)"
        start_date = r"(.*) from \d{2}-\d{2}-\d{4} (.*)"
        end_date = r"(.*) to \d{2}-\d{2}-\d{4} (.*)"
        people = r"(.*) \d+ adults|adult|people (.*)"
        
        match_object = re.match(source_regex, userInput)
        if match_object is not None:
            self.sou_city = userInput.split(match_object[0])[1].split()[0]
            userInput = userInput.split(match_object[0])[1]
            
        match_object = re.match(destination_regex, userInput)
        if match_object is not None:
            self.dst_city = userInput.split(match_object[0])[1].split()[0]
            userInput = userInput.split(match_object[0])[1]
            
        match_object = re.match(budget, userInput)
        if match_object is not None:
            self.budget = int(userInput.split(match_object[0])[1].split()[0])
            userInput = userInput.split(match_object[0])[1]
        
        match_object = re.match(start_date, userInput)
        if match_object is not None:
            self.start_date = userInput.split(match_object[0])[1].split()[0]
            userInput = userInput.split(match_object[0])[1]
            
        match_object = re.match(end_date, userInput)
        if match_object is not None:
            self.end_date = userInput.split(match_object[0])[1].split()[0]
            userInput = userInput.split(match_object[0])[1]
        
        match_object = re.match(people, userInput)
        if match_object is not None:
            print(userInput)
            print(userInput.split(match_object[0]))
            self.people = userInput.split(match_object[0])[1].split()[0]
            userInput = userInput.split(match_object[0])[1]
        
        
        print(self.sou_city)
        print(self.dst_city)
        print(self.budget)
        print(self.start_date)
        print(self.end_date)
        print(self.people)
        
        if match_object is not None:
            self.extract_entities(self, userInput)
        else:
            print("NER done")"""
        
        #END
        
        self.sou_city = "Gotham City"
        self.dst_city = "Minas Anor"
        self.budget = 300
        self.start_date = datetime.datetime.now()
        self.end_date = datetime.datetime.now()
        self.people = 4
        
        print(self.sou_city)
        print(self.dst_city)
        print(self.budget)
        print(self.start_date)
        print(self.end_date)
        print(self.people)
        
        
from transitions import Machine
import random
import sys

class DialogFlow(object):
    states = ["greetings", "inform", "affirm", "update", "end"]
    userInput = ""
    previousStates = []
    frame = DialogFrame()
    transitions = [
        {"trigger": "initialize", "source": "dummy", "dest": "greetings", "after": "get_user_input"},
        {"trigger": "ask_question", "source": "greetings", "dest": "inform", "after": "get_user_input"},
        {"trigger": "clarity", "source": "inform", "dest": "inform", "after": "get_user_input"},
        {"trigger": "change_entitity", "source": "inform", "dest": "update", "after": "get_user_input"},
        {"trigger": "updated", "source": "update", "dest": "inform", "after": "get_user_input"},
        {"trigger": "confirm", "source": "inform", "dest": "affirm", "after": "get_user_input"},
        {"trigger": "affirm_end", "source": "affirm", "dest": "end", "after": "get_user_input"},
        {"trigger": "new_query_affirm", "source": "affirm", "dest": "inform", "after": "get_user_input"}
    ]
    
    def __init__(self):
        """ Also included a dummy state since state callbacks are not fired when machine is
        first initialized"""
        
        self.machine = Machine(model=self, transitions = DialogFlow.transitions, 
                               states = DialogFlow.states, initial="dummy")
    
    def get_user_input(self):
        """ Callback for capturing user input and performing state transition """
        
        self.userInput = input()
        
        if self.userInput == "quit":
            sys.exit()
        
        engine = RuleBasedDialog()
        
        intent = engine.get_intent(self.userInput)
               
        nextTransition = engine.dialog_policy(intent, self.previousStates, self.transitions)
      
        self.trigger(nextTransition["trigger"])
        
    def on_enter_greetings(self):
        sentences = ["Hi!", "Greetings!", "Welcome", "Salut!"]
        
        print(random.choice(sentences) + "\n" + "How can I help you ?")
        
        self.previousStates.append("greetings")
        
    def on_enter_clarity(self):
    	
    	response = "Looks like I still haven't gotten information about "
    	
    	response_substring = []
    	
    	for remaining_slot in self.frame.checkForAllInfo():
    		if remaining_slot == "dst_city":
    			response_substring.append("destination city")
    		if remaining_slot == "sou_city":
    			response_substring.append("source city")
    		if remaining_slot == "budget":
    			response_substring.append("your trip budget")
    		if remaining_slot == "start_date":
    			response_substring.append("when you plan to leave")
    		if remaining_slot == "end_date":
    			response_substring.append("when do you plan to come back")
    		if remaining_slot == "people":
    			response_substring.append("how many people is the package for")
    	        
    	
    	#Response string formation
    	
    	if len(remaining_slot) == 1:
    		response  = response + remaining_slot[0]
    	
    	else:
    		for substring in remaining_slot[:-1]:
    			response = response + ", " + substring
    	
    		response = response + ",and " + remaining_slot[-1]
    	
    	print(response)
    	
    	
        
    def on_enter_inform(self):
        """ The main meaty part of the dialogflow manager. Responsible for 
                    1. Information extraction
                    2. Database query formation
                    3. Figuring out what other slots to fill """
        
        #Extract entities
        
        self.frame.extract_entities(self.userInput)
        
        
        
        if len(self.frame.checkForAllInfo()) == 0:
            #Got all info, now moving to confirm
            
            self.trigger("confirm")
        
        else:
            #Need more info
            
            self.trigger("clarity")
        
    def on_enter_affirm_end(self):
    	print("Thank you confirming. I have booked the package for you. Have a great day !!!")
    	

    def on_enter_affirm(self):
        
        print("Thank you for the details. Shall I go ahead and confirm it ?")
        
        print("So, you would")
    
    
df = DialogFlow()
df.initialize()
