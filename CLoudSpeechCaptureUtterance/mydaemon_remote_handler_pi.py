import argparse
import locale
import logging
import requests
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json
import time
import sys

from google.cloud.speech import enums
from google.cloud.speech import types

from mydaemon_cloudspeech_tts_pi import mydaemon_tts_speak
from mydaemon_cloudspeech_stt_pi import mydaemon_stt_capture

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon")


# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):
    # check to see if the message has valid content
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

    # if the message topic is mydaemon
    if msg.topic == "mydaemon":
        # The msg has content from mydaemon
        #if (message_json["mydaemon"] != ""):
            # is this the response to the latest question
            # first check that the user_utterance_array has data
        #    if MyDaemonSTT_.text != "":
        #        if MyDaemonSTT_.text == message_json["user"]:
        mydaemon_tts_speak(message_json["mydaemon"])
        #        else:
        #            print("Question does not match latest user utterance")
        #    else:
        #        print("Latest utterance is empty")

    # get the next input from the user
    while True:
        utterance = mydaemon_stt_capture()
        #MyDaemonSTT_.recognise_speech()
        if utterance != None:

            # create a string which has a question and and space for an answer
            qa_json = {"user": "", "mydaemon": ""}
            qa_json["user"] = utterance
            qa_string = json.dumps(qa_json)

            # publish the JSON
            mqtt_publish.single("user", qa_string, hostname="test.mosquitto.org")
            # print the JSON
            print("JSON published: ", qa_json)
            if utterance.lower() == "shutdown" or utterance.lower() == "shut down":
                sys.exit()
            # stop listening and wait for an answer
            break


def main():
    # Read the parameters
    # parser = argparse.ArgumentParser(description='Assistant service example.')
    # parser.add_argument('--language', default=locale_language())
    # args = parser.parse_args()

    # logging.info('Initializing for language %s...', args.language)

    # Load the hints if the lang starts with en
    # hints = get_hints(args.language)

    # Create an MQTT client and attach our routines to it.
    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)

    # Speak an initial message
    # mydaemon_tts_speak("Hello Paul. How are you today?")
    # logging.basicConfig(level=logging.DEBUG)

    #with Board() as board:
    while True:
        # create a string which has a question and and space for an answer
        qa_json = {"user": "", "mydaemon": ""}
        qa_json["user"] = "hello"
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("user", qa_string, hostname="test.mosquitto.org")
        #MyDaemonSTT_.text = qa_json["user"]
        local_mqtt_client.loop_forever()


if __name__ == '__main__':
    main()
