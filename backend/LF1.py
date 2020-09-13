import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def send_sqs_message(QueueName, msg_body):
    """

    :param sqs_queue_url: String URL of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    # Send the SQS message
    sqs_client = boto3.client('sqs', region_name="us-east-1")
    sqs_queue_url = sqs_client.get_queue_url(
        QueueName=QueueName
    )['QueueUrl']
    try:
        sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageBody=json.dumps(msg_body))
    except ClientError as e:
        logging.error(e)
        return None

def Thankyou(intent_request):
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': "You're welcome."
        }
    )

def Greeting(intent_request):
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hi there,how can I help?'
        }
    )

def Dinning_suggestion(intent_request):
    location = intent_request['currentIntent']['slots']['Location']
    food = intent_request['currentIntent']['slots']['Cuisine']
    time = intent_request['currentIntent']['slots']['DiningTime']
    Numberofpeople = intent_request['currentIntent']['slots']['Numberofpeople']
    Phonenumber = intent_request['currentIntent']['slots']['Phonenumber']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Okay, I have received your request and I will give you some restaurant suggestions soon, please check your text messegaes.'
        }
    )

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug(
        'dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return Dinning_suggestion(intent_request)
    elif intent_name=="GreetingIntent":
        return Greeting(intent_request)
    elif intent_name=="ThankYouIntent":
        return Thankyou(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    """Exercise send_sqs_message()"""
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    QueueName = 'Q1'
    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')
    if event["currentIntent"]["name"]=="DiningSuggestionsIntent":
        send_sqs_message(QueueName,event["currentIntent"]["slots"])
    return dispatch(event)
    #msg = send_sqs_message(QueueName, event)
    #return msg

