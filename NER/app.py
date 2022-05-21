from flask import Flask, request
import subprocess
import pandas as pd
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import re


dataset_path = "frames.json"
dataset = pd.read_json(dataset_path)

app = Flask(__name__)
app.secret_key = b'_5dfgtrdf45345^73@#4'
app.debug = True




@app.route("/predict", methods=["GET"])
def predict():

	input_text = request.args.get("text")
	
	print(input_text)
	
	nlp = spacy.load("./NER/model-best/") 
	doc = nlp(input_text)
	span_group = doc.spans["sc"] # default key, can be changed
	scores = span_group.attrs["scores"]

	# Note that `scores` is an array with one score for each span in the group
	for span, score, ent in zip(span_group, scores, doc.ents):
	    print("LABEL :",span.label_,"start :","span :", span, "len :",len(span.text),"score : ",score,ent.start_char,ent.end_char  )

	return [[span.label_ for span in span_group], [span.text for span in span_group]]
	


@app.route("/train")
def train():
	key_value = dict()

	data = []


	for conversation in dataset['turns']:
		for index, turn in enumerate(conversation):
			if turn['author'] == 'user':
				dataitem = set()
				utterance = turn["text"]
				dataitem.add(utterance)
				#print(utterance)

				for act in turn['labels']['acts']:

					entities = []


					for arg in act["args"]:

						# No value for the key, useless
						if "val" not in arg:
							continue

						#Not considering key_value pairs with annotations 
						if "val" in arg and type(arg["val"]) == list:
							continue


						#INCLUDE KEYS HERE WHICH YOU DON"T WANT IN THE TRAINING DATASET
						#
						if arg["key"] in ["intent", "flex", "id", "max_duration"]:
							continue


						#print(arg)

						start_index = utterance.find(str(arg["val"]))
						end_index = start_index + len(str(arg["val"])) - 1
						#print(start_index)
						#print(end_index)

						entities.append((start_index, end_index, arg["key"],)) 

					#print(entities)
					if len(entities) > 0:
						data.append((utterance, {"entities": entities}))
	    
    
	nlp = spacy.blank("en") # load a new spacy model
	db = DocBin() # create a DocBin object
	
	
	for text, annot in tqdm(data): 
		doc = re.sub(' +', ' ', text)
		doc = nlp.make_doc(text) 
		ents = []
		for start, end, label in annot["entities"]:
			span = doc.char_span(start, end, label=label, alignment_mode="contract")
			if span is None:
				continue
			else:
				ents.append(span)
		doc.ents = ents 
		db.add(doc)

	db.to_disk("./training_data.spacy") # save the docbin object

	for text, annot in tqdm(data): # data in previous format
		doc = nlp.make_doc(text) # create doc object from text
		try:
			ents = []
			for start, end, label in annot["entities"]: # add character indexes
				span = doc.char_span(start, end, label=label, alignment_mode="strict")
				if span is not None:
					ents.append(span)            
			doc.ents = ents # label the text with the ents
		except Exception as e:
			doc.ents = []
		
		db.add(doc)

	db.to_disk("./spandata.spacy") # save the docbin object

	#after getting ner data converting into doc.spans["sc"]
	docbin = DocBin().from_disk("./spandata.spacy")
	docs = list(docbin.get_docs(nlp.vocab))
	for doc in docs:
	    doc.spans["sc"] = list(doc.ents)
	DocBin(docs=docs).to_disk("./spansdata.spacy")

	nlp.add_pipe('spancat')
	
	print(run_command("python3 -m spacy init config Adam_v1_config.cfg --lang en --pipeline  ner,spancat --optimize efficiency --force"))

	print(run_command("python3 -m spacy train Adam_v1_config.cfg --output ./NER --paths.train ./spansdata.spacy --paths.dev ./spansdata.spacy"))




def run_command(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

