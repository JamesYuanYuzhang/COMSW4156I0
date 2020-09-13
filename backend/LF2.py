# function:
# pull messages from SQS
# Get a random resturant recommendation for the cuisine collected
# Format them
# Send them over text message to the phone number included in the SQS message, using SNS

# the return json sample from SQS {"Location": "Columbia University", "Cuisine": "Chinese food", "DiningTime": "10:00", "Numberofpeople": "5", "Phonenumber": "1234568888"}

from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection
import requests
import json
import boto3, decimal, random
from boto3.dynamodb.conditions import Key, Attr
import certifi
from requests_aws4auth import AWS4Auth


def search_elastic(es, Cuisine_type, index="restaurants", doc_type="_doc", size=1000):
    query = {"query": {"match": {"Cuisine type": Cuisine_type}}, "size": size}
    try:
        response = es.search(index=index, doc_type=doc_type, body=query)
        #print(json.dumps(response, indent=2))
        return response["hits"]["hits"]
    except Exception as e:
        print(e)
        return None


def _delete_elastic(es, index):
    try:
        response = es.indices.delete(index=index, ignore=[400, 404])
        print(response)
    except Exception as e:
        print(e)


def select_restaurants(candidates):
    can = random.randint(0, len(candidates) - 1)
    return candidates[can]


def select_dynamodb(target):
    id = target["Business_ID"]
    # id="Z0VCrAW4VKIL7SteB6w8Mw"
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("yelp-restaurants")
    res = table.query(KeyConditionExpression=Key("Business_ID").eq(id))
    try:
        return res["Items"][0]
    except Exception as e:
        print("Error happens when select data from dynamodb!", e)
    return ""

def receive_and_delete():
    sqs = boto3.client('sqs', region_name="us-east-1")
    QueueName = "Q1"
    sqs_queue_url = sqs.get_queue_url(QueueName=QueueName)['QueueUrl']
    response = sqs.receive_message(QueueUrl=sqs_queue_url, MaxNumberOfMessages=1, MessageAttributeNames=['Cuisine'],
                                   VisibilityTimeout=0, WaitTimeSeconds=0)
    # print(response)
    if not response.get("Messages"):
        print("The SQS is empty!")
        return {}
    try:
        print(response)
        message = response['Messages'][0]
        print(message["Body"])
        receipt_handle = message['ReceiptHandle']
        sqs.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=receipt_handle
        )
        return message["Body"]
    except Exception as e:
        print("Something wrong with SQS", e)



def send_text_msg(msg, phone_number):
    if not phone_number.startswith("+1"):
        phone_number="+1"+phone_number
    sns = boto3.client("sns", region_name="us-east-1")
    print(str(msg))
    #msg="Stop study."
    sns.publish(PhoneNumber=phone_number, Message=str(msg))


def put_data_to_es(es):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    print("connect dynamodb successfull")
    table = dynamodb.Table("yelp-restaurants")
    pe = ["Business_ID", "Cuisine type"]
    data = []
    response = table.scan(AttributesToGet=pe)
    data.extend(response["Items"])
    # print(json.dumps(response,indent=2))
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    print(len(data))
    try:
        res = helpers.bulk(es, gen_data(data))
        print(res)
    except Exception as e:
        print(str(e))


def gen_data(data, index="restaurants", type="_doc"):
    for d in data:
        yield {
            '_index': index,
            '_type': type,
            '_id': d["Business_ID"],
            "Business_ID": d["Business_ID"],
            "Cuisine type": d["Cuisine type"]
        }


def lambda_handler(event, context):
    host = "search-restaurants-ljthbucz4jrosxjnru64urdd4q.us-east-1.es.amazonaws.com"
    region = "us-east-1"
    service = "es"
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service,session_token=credentials.token)
    # es = Elasticsearch(hosts="https://vpc-restaurants-ljthbucz4jrosxjnru64urdd4q.us-east-1.es.amazonaws.com",ca_certs=certifi.where())
    es = Elasticsearch(hosts=[{"host": host, "port": 443, "use_ssl": True}], http_auth=awsauth, use_ssl=True,
                       verify_certs=True, connection_class=RequestsHttpConnection, request_timeout=30)
    #put_data_to_es(es)
    #return
    try:
        event=receive_and_delete()
        if not event:
            return {
            'statusCode': 200,
            'body': json.dumps('SQS is empty!')
        }
        event=json.loads(event) if type(event)!=dict else event
        food_type, phone_number = event["Cuisine"], event["Phonenumber"]
        candidates = search_elastic(es, food_type)
        target = select_restaurants(candidates)["_source"]
        result = select_dynamodb(target)
        print(result)
        msg="The name of restaurant is {}, and the location is {}, and the rating is {}.".format(result["Name"],result["Address"],result["Rating"])
    except:
        phone_number=event["Phonenumber"]
        msg="There is something wrong with your query. Please try again."
    send_text_msg(msg, phone_number)
    return {
        'statusCode': 200,
        'body': json.dumps('I have sent you a text message which contains my suggestions.')
    }
