#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Publish utterances from "user" - recieve uuterances from "mydaemon"

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging
import requests
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json
import time

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
from aiy.voice import tts

latest_user_utterance = ""

def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon")

# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):
    global latest_user_utterance
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

    if msg.topic == "mydaemon":
        # The msg has content from mydaemon
        if(message_json["mydaemon"] != ""):
            #is this the response to the latest question
            #first check that the user_utterance_array has data
            if latest_user_utterance != "":
                if latest_user_utterance == message_json["user"]:
                    tts.say(message_json["mydaemon"],volume=20,lang="en-GB")
                else:
                    print("Question does not match latest user utterance")
            else:
                print("Latest utterance is empty")
    
def main():
    
    # global variable use in callback to make sure the response is to the latest user input
    global latest_user_utterance
    
    # Read the parameters
    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()
    
    logging.info('Initializing for language %s...', args.language)
    
    # Load the hints if the lang starts with en
    hints = get_hints(args.language)
    
    # Start a cloud speech client
    cloudspeech_client = CloudSpeechClient()
    
    # Create an MQTT client and attach our routines to it.
    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    
    # Speak an initial message
    tts.say('Hello Paul.',volume=20,lang="en-GB")
    logging.basicConfig(level=logging.DEBUG)

    with Board() as board:
        while True:
            local_mqtt_client.loop()
            text = cloudspeech_client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text != None:
                
                #create a string which has a question and and space for an answer
                qa_json = {"user": "", "mydaemon": ""}
                qa_json["user"] = text
                qa_string = json.dumps(qa_json)
                
                #publish the JSON
                mqtt_publish.single("user", qa_string, hostname="test.mosquitto.org")
                #print the JSON
                print("JSON published: ", qa_json)
                
                #store latest utterance in global variable - need to remove global
                latest_user_utterance = qa_json["user"]
            time.sleep(1)            

if __name__ == '__main__':
    main()
