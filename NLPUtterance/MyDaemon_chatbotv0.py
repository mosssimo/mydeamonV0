# Paul Zanelli
# created: 4th April 2020

import sys
import pandas as pd
import nltk
import numpy as np
import re
from nltk.stem import wordnet # to perform lemmitization
from sklearn.feature_extraction.text import CountVectorizer # to perform bow
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize # to create tokens
from nltk import pos_tag # for parts of speech
from sklearn.metrics import pairwise_distances # to perform cosine similarity
from nltk import word_tokenize # to create tokens
from nltk.corpus import stopwords # for stop words
from pathlib import Path
from pathlib import Path, PureWindowsPath
import getopt
import paho.mqtt.publish as publish


def text_normalization(text):
    text=str(text).lower() # text to lower case)
    spl_char_text=re.sub(r'[^ a-z]','',text) # removing special characters
    tokens=nltk.word_tokenize(spl_char_text) # word tokenizing
    lema=wordnet.WordNetLemmatizer() # initializing lemmatization
    tags_list=pos_tag(tokens,tagset=None) # parts of speech
    lema_words=[] # empty list
    for token,pos_token in tags_list:
        if pos_token.startswith('V'): #verb
            pos_val='v'
        elif pos_token.startswith('J'): # adjective
            pos_val='a'
        elif pos_token.startswith('R'): # Adverb
            pos_val='r'
        else:
            pos_val='n' # Noun
        lema_token=lema.lemmatize(token,pos_val) # performing lemmatization
        lema_words.append(lema_token) # appending the lemmatized token into a list

    return " ".join(lema_words) # returns the lemmatized tokens as a sentence

def stop_word(text):
    tag_list=pos_tag(nltk.word_tokenize(text),tagset=None)
    stop=stopwords.words('english')
    lema=wordnet.WordNetLemmatizer()
    lema_word=[]
    for token,pos_token in tag_list:
        if token in stop:
            continue
        if pos_token.startswith('V'):
            pos_val='v'
        elif pos_token.startswith('J'):
            pos_val='a'
        elif pos_token.startswith('R'):
            pos_val='r'
        else:
            pos_val='n'
        lema_token=lema.lemmatize(token,pos_val)
        lema_word.append(lema_token)
    return " ".join(lema_word)

def load_database():
    # read the question answer dataset
    project_home = Path("")
    if (project_home) not in sys.path:
        sys.path = [project_home] + sys.path

    path_on_windows = PureWindowsPath(project_home / "MyDaemon-question-answer-db.csv")
    dataset = pd.read_csv(path_on_windows)
    dataset.head()
    # print(dataset) # print the data set
    # print(dataset.shape[0]) # print the number of rows
    # fill any undefined values
    dataset.ffill(axis=0, inplace=True)
    dataset.head(5)
    return(dataset)

def get_answer(question, dataset):

    # fill any undefined values
    dataset.ffill(axis=0, inplace=True)
    dataset.head(5)

    # normalise text and remove stop words
    dataset['lemmatized_text'] = dataset['Context'].apply(
        text_normalization)  # applying the text normlization that Anna wrote function to the dataset to get clean text
    #dataset['lemmatized_text'] = dataset['Context'].apply(
    #    stop_word)  # applying the stop word function to the dataset to get clean text
    dataset.head()

    question = text_normalization(question)
    #question = stop_word(question)
    #print("The normalized question with stop words removed is: " + question)

    cv = CountVectorizer()  # init counter vector
    X = cv.fit_transform(dataset['lemmatized_text']).toarray()
    features = cv.get_feature_names()

    # get bow for data set
    dataset_bow = pd.DataFrame(X, columns=features)
    dataset_bow.head()

    # tfidf data set
    tfidf = TfidfVectorizer()  # init tf-id
    x_tfidf = tfidf.fit_transform(dataset['lemmatized_text']).toarray()  # transforming the data into array
    dataset_tfidf = pd.DataFrame(x_tfidf, columns=tfidf.get_feature_names())
    dataset_tfidf.head()

    # get bow for question
    question_bow = cv.transform([question]).toarray()  # applying bow

    # tdidf question
    question_tfidf = tfidf.transform([question]).toarray()  # applying tf-idf

    distances = 1 - pairwise_distances(dataset_tfidf, question_tfidf, metric='cosine')
    index_value = distances.argmax()  # getting the index value
    return(str(dataset['Text Response'].loc[index_value]))

def main(argv):
    # get the question from the command line parameters
    # set a default question
    question = "Have you got any toilet paper"
    try:
        opts, args = getopt.getopt(argv, "q:")
    except getopt.GetoptError:
        print("mydaemon.py -h -q <url>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("nltk-chatbot.py -h -u <url>")
            sys.exit()
        elif opt in ("-q"):
            question = arg

    #Load the database
    dataset = load_database()
    return (get_answer(question, dataset))

if __name__ == '__main__':
    answer = main(sys.argv[1:])
    print("The answer is :" + answer)