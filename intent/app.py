from flask import Flask, request
import boto3
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
nltk.download("wordnet")
nltk.download("omw-1.4")
nltk.download("punkt")
from sklearn.feature_extraction.text import TfidfVectorizer , CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import hamming_loss
from sklearn.metrics import multilabel_confusion_matrix , ConfusionMatrixDisplay
import json
import re
import pandas as pd
import numpy as np





#Expand contractions

file = open('contractions.json')
contractions = json.load(file)

contractions_regex=re.compile('(%s)' % '|'.join(contractions.keys()))

classifier_path = "intent_clasifier.joblib"
dataset_path = "frames.json"

dataset = pd.read_json(dataset_path)

app = Flask(__name__)
app.secret_key = b'_5dfgtrdf45345^73@#4'
app.debug = True



@app.route("/train")
def train():
	print("Training started")
	
	classifier = train_model(dataset)
	save_model(classifier, classifier_path)

	print("Training ended")
	
	return View


@app.route("/predict", methods=["GET"])
def predict():

	print("Prediction started")
	
	classifier = read_classifier(classifier_path)
	input_text = request.args.get("text")
	multilabel,tfidf,dataframe = NLP_parameters(dataset)
	txt = input_text.lower()
	txt = re.sub(r'\d+', '', txt)
	txt = re.sub('[,\.!?]', ' ', txt)
	text_tokenized = []
	text_tokenized.append(word_tokenize(txt))
	stop_words_with_negation = set(stopwords.words('english'))
	data_words_nostops = remove_stopwords(text_tokenized,stop_words_with_negation)
	data_lemmatized = lemmatization(data_words_nostops)
	X = tfidf.transform([txt])
	intents = multilabel.inverse_transform(classifier.predict(X))
	print(intents[0][0])

	print("Prediction ended")
	
	return intents[0][0]

@app.route("/getMetrics", methods=["GET"]) #Return matrics of prediction on whole dataset
def getMetrics():
	classifier = read_classifier(classifier_path)
	multilabel,tfidf,dataframe = NLP_parameters(dataset)
	y = multilabel.transform(dataframe['labels'])
	X = tfidf.transform(dataframe['text_processed'])
	y_pred = classifier.predict(X)
	loss = hamming_loss(y_pred, y)
	score = hamming_score(y_pred, y)
	confusion_matrix = multilabel_confusion_matrix(y, y_pred)
	labels = multilabel.classes_
	return loss, score, confusion_matrix, labels
  

def NLP_parameters(dataset):
	texts,intents = get_data_and_intents(dataset)
	dataframe = pd.DataFrame(texts, columns=['text','labels'])
	dataframe['text_processed']=dataframe['text'].apply(lambda x:replace_contractions(x))
	#Delete null labels
	dataframe = dataframe.drop(dataframe[dataframe['labels'].apply(lambda x: len(x)==0)].index)
	dataframe['text_processed'] = [re.sub(r'\d+', '', text) for text in dataframe['text_processed']]
	dataframe['text_processed'] = dataframe['text_processed'].map(lambda x: re.sub('[,\.!?]', ' ', x))
	dataframe['text_processed'] = dataframe['text_processed'].map(lambda x: x.lower())
	text_tokenized = [word_tokenize(text) for text in dataframe.text_processed]

	stop_words_with_negation = set(stopwords.words('english'))
	data_words_nostops = remove_stopwords(text_tokenized,stop_words_with_negation)
	data_lemmatized = lemmatization(data_words_nostops)

	multilabel = MultiLabelBinarizer()
	multilabel.fit(dataframe['labels'])


	tfidf = TfidfVectorizer(analyzer='word', max_features = 1000)
	tfidf.fit(dataframe['text_processed'])

	return multilabel,tfidf,dataframe

def train_model(dataset):
	multilabel,tfidf,dataframe = NLP_parameters(dataset)
	y = multilabel.transform(dataframe['labels'])
	X1 = tfidf.transform(dataframe['text_processed'])

	X_train, X_test, y_train, y_test = train_test_split(X1, y, test_size = 0.2, random_state = 0)

	classifier = OneVsRestClassifier(SGDClassifier())
	classifier.fit(X_train, y_train)
	#y_pred = classifier.predict(X_test)
	return classifier

def save_model(classifier, path):
	from joblib import dump
	dump(classifier, path)

def read_classifier(path):
	from joblib import load
	clf = load(path)
	return clf



#Get all the intents from the conversation by Users as well as the texts
def get_data_and_intents(dataset):
  intents = set()
  data = []
  for conversation in dataset['turns']:
      for index, turn in enumerate(conversation):
        if turn['author'] == 'user':
          names = set()
          for act in turn['labels']['acts']:
            names.add(act['name']) # Adding the intents from the lists of acts
            intents.add(act['name'])
            for arg in act['args']:
              if arg['key']=='intent':
                names.add(arg['val'])
                intents.add(arg['val']) # Adding the intent "book" in our list of intent
          data.append([turn['text'],names])
  return data,intents

#Replace contractions
def replace_contractions(txt,contractions=contractions):
  def replace(match):
    return contractions[match.group(0)]
  return contractions_regex.sub(replace, txt)




#Code from labs
def get_wordnet_pos(word):
    """Map the POS tag to the first character lemmatize() accepts."""

    try:  # download nltk's POS tagger if it doesn't exist
        nltk.data.find("taggers/averaged_perceptron_tagger")
    except LookupError:
        nltk.download("averaged_perceptron_tagger")
    tag = nltk.pos_tag([word])[0][1][0].upper()  # use ntlk's POS tagger on the word

    # now we need to convert from nltk to wordnet POS notations (for compatibility reasons)
    tag_dict = {
        "J": wordnet.ADJ,
        "N": wordnet.NOUN,
        "V": wordnet.VERB,
        "R": wordnet.ADV
    }

    return tag_dict.get(tag, wordnet.NOUN)  # return and default to noun if not found

def lem_tokenizer(text):
  lemmatizer = WordNetLemmatizer()
  return [lemmatizer.lemmatize(x, pos=get_wordnet_pos(x)) for x in text]

def lemmatization(texts):
  stem_tokens = [lem_tokenizer(token) for token in texts]
  return stem_tokens

def remove_stopwords(texts,stop_words):
  return [[word for word in token if word not in stop_words] for token in texts]

def hamming_score(y_true, y_pred, normalize=True, sample_weight=None):
    acc_list = []
    for i in range(y_true.shape[0]):
        set_true = set( np.where(y_true[i])[0] )
        set_pred = set( np.where(y_pred[i])[0] )
        tmp_a = None
        if len(set_true) == 0 and len(set_pred) == 0:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred))/float(len(set_true.union(set_pred)) )
        acc_list.append(tmp_a)
    return np.mean(acc_list)