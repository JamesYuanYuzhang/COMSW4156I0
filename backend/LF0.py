import boto3
import json


def send(event):
    responderName = "DinnerSuggestions"
    userId = event["SenderID"]
    userInput = event["Text"]
    alias = "James"

    client = boto3.client('lex-runtime')

    response = client.post_text(
        botName=responderName,
        botAlias=alias,
        userId=userId,
        sessionAttributes={
        },
        requestAttributes={
        },
        inputText=userInput
    )
    try:
        return respond(None, response["message"])
    except:
        return respond("IntentName is {}".format(event.get("intentName")), event.get("message"))


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps(err) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            # "Access-Control-Allow-Origin": "*"
        },
    }


def get(payload):
    return "I'm still under development. Please come back later."


def lambda_handler(event, context):
    return send(event)
