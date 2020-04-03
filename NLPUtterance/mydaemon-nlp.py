# This programme checks to see if there is an utterance on the utterance server
# If there is it uses nltk to decompse and tag the utterance
# Note that I am dealing with an utterance but considering it to be a sentence
# Paul Zanelli
# Creation date: 4th April 2020

import nltk
import requests
import time
import sys
import getopt

def main(argv):
        #default hostname
        api_url_base = "http://localhost:3000"
        try:
                opts, args = getopt.getopt(argv, "u:")
        except getopt.GetoptError:
                print("mydaemon.py -h -u <url>")
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h':
                        print("mydaemon.py -h -u <url>")
                        sys.exit()
                elif opt in ("-u"):
                        api_url_base = arg
        print('URL is ', api_url_base)

        utterances_json = requests.get(api_url_base)
        #check that the response is 200 that indicates we have data
        while True:
                utterances_json = requests.get(api_url_base)
                #print the response code
                #print(utterances_json.status_code)
                if utterances_json.status_code == 200:
                        #we have received a valid response
                        #print the json


                        #convert json to an array
                        utterances_array = utterances_json.json()
                        if  utterances_array:
                                #array is not empty
                                print(utterances_json.text)
                                #process the first utterance
                                tokens = nltk.word_tokenize(utterances_array[0]["utterance"])
                                tagged = nltk.pos_tag(tokens)
                                entities = nltk.chunk.ne_chunk(tagged)
                                #print(utterances_array[0]["utterance"])
                                if utterances_array[0]["utterance"] == "stop all processes":
                                        break
                                print(tokens)
                                print(tagged)
                                print(entities)

                                #pop the last utterance
                                print('calling delete')
                                requests.delete(api_url_base + '/' + str(0) )
                        else:
                                #array is empty
                                #print('array is empty - exit')
                                time.sleep(5)
                else:
                        # response not 200
                        # print('response not 200')
                        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv[1:])