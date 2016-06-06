"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib2
import xml.etree.ElementTree as etree
from datetime import datetime as dt

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetBusTime":
        return get_bus_time(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Bus Tracker Application. " \
                    "Please ask me for bus times by saying, " \
                    "What are my bus times?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me for bus times by saying, " \
                    "What are my bus times?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_bus_time(intent, session):
    """ Grabs our bus times and creates a reply for the user
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
#Input your CTA API key in the URL BELOW
    url="http://www.ctabustracker.com/bustime/api/v1/getpredictions?key=YOURAPIKEYHERE&rt=22&stpid=1820"
    xml_data = urllib2.urlopen(url)

    #parse the example into ElementTree
    tree = etree.parse(xml_data)
    #close connection
    xml_data.close()

    #Find the root element
    rootElem = tree.getroot()

    #create lists to hold timesamps and prediction times
    timestamps = []
    predictiontime = []
    prediction = []

    #iterate over elementes in rootElem finding tags with tmstmp and prdtm
    for element in rootElem.iter():
        if element.tag == 'tmstmp':
    #        print element.tag, element.text
            timestamps.append(element.text)
        if element.tag == 'prdtm':
    #        print element.tag, element.text
            predictiontime.append(element.text)

    #print "Print out list data for tmstmp and prdtm"
    #print out our values to make sure Tim isn't stupid
    #for value in timestamps:
    #    print value
    #for value in predictiontime:
    #   print value

    #describe how the XML time data looks when retrieved from the list
    FT = '%Y%m%d %H:%M'
    #initialize count to check our work
    count = 0
    for element in rootElem.getchildren():
        delta = dt.strptime(predictiontime[count], FT) - dt.strptime(timestamps[count],FT)
        prediction.append(int(delta.total_seconds()/60))
        count += 1

    #check your work to make sure that we iterated correctly
    #for value in prediction:
    #    print value
    #print "Count of child xml elements under root (equal to actaul busses):"
    #print count

    if count != 0:
        speech_output = "Your next bus is arriving in " + str(prediction[0]) + " minutes" \

        reprompt_text = ""
    else:
        speech_output = "Please ask me for bus times by saying, " \
                        "What are my bus times?"
        reprompt_text = "Please ask me for bus times by saying, " \
                        "What are my bus times?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
