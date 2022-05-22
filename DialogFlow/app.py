import re
import requests
import datetime
from transitions import Machine
import random
from flask import Flask, request, render_template
import json

intent_url = "http://127.0.0.1:5001/predict"
ner_url = "http://127.0.0.1:5002/predict"

class RuleBasedDialog:


    def __init__(self):
        print("")
    
    def get_intent(self, userInput):
    
        response = requests.get(intent_url, params={"text": userInput})
        
        intent = str(response.text)
        
        print("Intent detected for {0}: \n{1}".format(userInput, intent))
        
        return intent
                
    def dialog_policy(self, intent, previousStates, transitions):
    
        #User gives some information or intents to book a package
        if intent in ["inform","book"] and previousStates[-1] == "greetings":
            return [x for x in transitions if x["trigger"] == "clarity"][0]
            
        #User doesn't intent to book. Ask the question    
        elif previousStates[-1] == "greetings":
            return [x for x in transitions if x["trigger"] == "ask_question"][0]
        
        #Chatbot asked the question, user wants to book
        elif intent in ["inform","book"] and previousStates[-1] == "question":
            return [x for x in transitions if x["trigger"] == "clarity"][0]
            
            
        #Chatbot needs more information from the user to complete its task
        elif intent in ["inform","book"] and previousStates[-1] == "inform":
            return [x for x in transitions if x["trigger"] == "clarity"][0]
        
        
        #Chatbot asked the question, user doesn't intent to book. Ask the question again, and again, and again, and.....
        elif previousStates[-1] == "question":
            return [x for x in transitions if x["trigger"] == "ask_question"][0]
        
        #User intents to change information
        elif intent == "switch_frame" and previousStates[-1] == "inform":
            return [x for x in transitions if x["trigger"] == "ask_update"][0]
        
        #User updates chatbot with new information
        elif intent in ["inform","book"] and previousStates[-1] == "update":
            return [x for x in transitions if x["trigger"] == "update_info"][0]
            
        #User wants to confirm booking the package
        elif intent == "affirm" and previousStates[-1] == "affirm":
            return [x for x in transitions if x["trigger"] == "end_convo"][0]
        
        #User doesn't want to confirm booking the package
        elif intent == "negate" and previousStates[-1] == "affirm":
            return [x for x in transitions if x["trigger"] == "ask_update"][0]
        
        #User wants to end the conversation
        elif intent in ["thankyou", "goodbye"]:
            return [x for x in transitions if x["trigger"] == "end_convo"][0]
        
        
          
        

class DialogFrame:
    """ Knowledge representation for the Trip package booking """
    
    slot = {
      "dst_city": None,
      "or_city": None,
      "budget": None,
      "str_date": None,
      "end_date": None,
      "n_adults": None
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
        
        response = requests.get(ner_url, params={"text": userInput})
        
        ner = json.loads(response.content.decode('utf-8'))
        
        print("NER detected for {0}".format(userInput))
        
        print(ner)
        
        for key,value in ner.items():
        	if key in self.slot:
        		self.slot[key] = value
        
        
        
        #print(self.slot)
        
        #self.slot["sou_city"] = "Gotham City"
        #self.slot["dst_city"] = "Minas Anor"
        #self.slot["budget"] = 300
        #self.slot["start_date"] = datetime.datetime.now()
        #self.slot["end_date"] = datetime.datetime.now()
        #self.slot["people"] = 4
        
        #print(self.slot["sou_city"])
        #print(self.slot["dst_city"])
        #print(self.slot["budget"])
        #print(self.slot["start_date"])
        #print(self.slot["end_date"])
        #print(self.slot["people"])
        
        

class DialogFlow(object):
    states = ["greetings", "question", "inform", "affirm", "update", "end"]
    userInput = ""
    previousStates = []
    frame = DialogFrame()
    transitions = [
        {"trigger": "initialize", "source": "dummy", "dest": "greetings"},
        {"trigger": "clarity", "source": ["greetings", "inform"], "dest": "inform"},
        {"trigger": "ask_question", "source": "greetings", "dest": "question"},
        {"trigger": "ask_update", "source": ["inform","affirm"], "dest": "update"},
        {"trigger": "update_info", "source": "update", "dest": "inform"},
        {"trigger": "confirm", "source": "inform", "dest": "affirm"},        
        {"trigger": "end_convo", "source": ["affirm", "inform", "question", "update"]   ,"dest": "end"}
             
    ]
    
    chatbotOutput = ""
    
    
    def __init__(self):
        """ Also included a dummy state since state callbacks are not fired when machine is
        first initialized"""
        
        self.machine = Machine(model=self, transitions = DialogFlow.transitions, 
                               states = DialogFlow.states, initial="dummy")
    
    def get_user_input(self, userInput):
        """ Callback for capturing user input and performing state transition """
        
        self.userInput = userInput
        
        if self.userInput == "quit":
            sys.exit()
        
        engine = RuleBasedDialog()
        
        intent = engine.get_intent(self.userInput)
               
        nextTransition = engine.dialog_policy(intent, self.previousStates, self.transitions)
        
        print("Previous states of the chatbot were {0}".format(self.previousStates))
        
        print("Next Transition is {0}".format(nextTransition))
      
        self.trigger(nextTransition["trigger"])
        
    def on_enter_greetings(self):
        sentences = ["Hi!", "Greetings!", "Welcome", "Salut!"]
        
        response = random.choice(sentences) + "\n" + "How can I help you ?"
        self.chatbotOutput = response
        
        print(response)
        
        self.previousStates.append("greetings")
        
        
    def on_enter_question(self):
               
        response = "Would you like to book a trip package ?"
        
        self.chatbotOutput = response
        
        print(response)
        
        self.previousStates.append("question")
  	
                  
    def on_enter_inform(self):
        """ The main meaty part of the dialogflow manager. Responsible for 
                    1. Information extraction
                    2. Database query formation
                    3. Figuring out what other slots to fill """
        
        print("Inform State Reached")
        
        
        self.previousStates.append("inform")
    	
    	
    	#Extract entities
        
        self.frame.extract_entities(self.userInput)
                
        if len(self.frame.checkForAllInfo()) == 0:
            #Got all info, now moving to confirm
            
            self.trigger("confirm")
        
        else:
          
            #Need more info
            response = "Looks like I still haven't gotten information about "

            response_substring = []
    	
            for remaining_slot in self.frame.checkForAllInfo():
               if remaining_slot == "dst_city":
                  response_substring.append("destination city")
               if remaining_slot == "or_city":
                  response_substring.append("source city")
               if remaining_slot == "budget":
                  response_substring.append("your trip budget")
               if remaining_slot == "str_date":
                  response_substring.append("when you plan to leave")
               if remaining_slot == "end_date":
                  response_substring.append("when do you plan to come back")
               if remaining_slot == "n_adults":
                  response_substring.append("how many people is the package for")
		 
            
            #Response string formation

            if len(remaining_slot) == 1:
               response  = response + remaining_slot[0]

            else:
               for substring in response_substring[:-1]:
                  response = response + ", " + substring

               response = response + ",and " + response_substring[-1]


            print(response)

            self.chatbotOutput = response
    	


    def on_enter_affirm(self):
    
        print("Affirm State Reached")
    
        response = "Thank you for the details. Shall I go ahead and confirm it ?"
        
        self.chatbotOutput = response
        
        print(response)
        
        self.previousStates.append("affirm")
        
    def on_enter_end(self):
    
        print("End State Reached")
    
        response = "Thank you booking the trip package with us. Have a nice day!!!"
        
        self.chatbotOutput = response
        
        print(response)
        
        self.previousStates.append("end")
        
        print("Conversation ended")
    
    
    def on_enter_update(self):
    
    	print("Update State Reached")
    	
    	response = "What do you want to change ?"
    	
    	self.chatbotOutput = response
    
    	print(response)
    	
    	self.previousStates.append("update")
    
    
    
    
    
df = object
isConversationStarted = False
conversation = []

app = Flask(__name__)
app.secret_key = b'_5dfgtrdf45345^73@#4'
app.debug = True


@app.route("/input", methods=["GET"])
def converse():

        global isConversationStarted
        global conversation
        global df
        
        utterance = request.args.get("text")
        
        print(utterance)
        
        if not isConversationStarted:
        	
        	df = DialogFlow()
        	df.initialize()
        	isConversationStarted = True
        
        else:
        	
        	df.get_user_input(utterance)
        
        response = df.chatbotOutput
        if utterance is not None:
        	conversation.append(utterance)
        
        conversation.append(response)
        
        
        return render_template("template.html", data=conversation)





















