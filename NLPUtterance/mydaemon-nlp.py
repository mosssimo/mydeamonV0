# This programme checks to see if there is an utterance on the utterance server
# If there is it uses nltk to decompse and tag the utterance
# Note that I am dealing with an utterance but considering it to be a sentence
# Paul Zanelli
# Creation date: 4th April 2020

import nltk
import requests

def main():

        #need to have this as a parameter
        api_url_base = 'Http://localhost:3000'
        utterances_json = requests.get(api_url_base)
        #check that the response is 200 that indicates we have data
        while True:
                utterances_json = requests.get(api_url_base)
                #print the response code
                print(utterances_json.status_code)
                if utterances_json.status_code == 200:
                        #we have received a valid response
                        #print the json
                        print(utterances_json.text)

                        #convert json to an array
                        utterances_array = utterances_json.json()
                        if  utterances_array:
                                #array is not empty

                                #process the first utterance
                                tokens = nltk.word_tokenize(utterances_array[0]["utterance"])
                                tagged = nltk.pos_tag(tokens)
                                entities = nltk.chunk.ne_chunk(tagged)
                                print(utterances_array[0]["utterance"])
                                print(tokens)
                                print(tagged)
                                print(entities)

                                #pop the last utterance
                                print('calling delete')
                                requests.delete(api_url_base + '/' + str(0) )
                        else:
                                #array is empty
                                print('array is empty - exit')
                                break
                else:
                        print('invalid response from get - exit')
                        break

if __name__ == '__main__':
    main()