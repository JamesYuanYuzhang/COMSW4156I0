import requests
import json
import boto3
import collections
import datetime
from decimal import *

API_Key="iHLrR7BOfKc0xRjaR688Ait3j9g47AAy_QksiwyKzEc0BA4PISSy_u1u_daSE-YRVHtLFn3owOIe1HQqCbltL1-dT0aPrVetEAc7FtP4B5FmCjlHcqaM_e7TaqhBXnYx"
headers = {'Authorization': 'Bearer %s' % API_Key}
url='https://api.yelp.com/v3/businesses/search'

cuisine_types=["Italian","Chinese","American","Indian","Japanese","Mexican"]
records=dict()
different_type=collections.defaultdict(set)
dynamodb = boto3.resource('dynamodb',region_name ='us-east-1')
table = dynamodb.Table('yelp-restaurants')
count=0
with table.batch_writer() as batch:
    for cuisine_type in cuisine_types:
        limit, offset = 50, 0
        while offset<1000:
            params = {'term': cuisine_type, 'location': 'New York City', "limit": limit, "offset": offset}
            req = requests.get(url, params=params, headers=headers)
            # proceed only if the status code is 200
            if req.status_code!=200:
                print(req)
                raise ValueError
            # printing the text from the response
            parsed = json.loads(req.text)
            businesses = parsed["businesses"]
            #print(len(businesses))
            for business in businesses:
                record=dict()
                record["Business_ID"]=business["id"]
                record["Name"]=business["name"]
                record["Address"]=" ".join(business["location"]["display_address"])
                record["Coordinates"]=business["coordinates"]
                record["Number of Reviews"]=business["review_count"]
                record["Rating"]=(business["rating"])
                record["Zip Code"]=business["location"]["zip_code"]
                record["Cuisine type"]=cuisine_type
                record["insertedAtTimestamp"]=str(datetime.datetime.now())
                #print(json.dumps(record,indent=2))
                record=json.loads(json.dumps(record),parse_float=Decimal)
                #for v in record.values():
                #    print(type(v))
                #exit()
                id = business["id"]
                if record.get(id,None) is None:
                    records[id]=record
                    try:
                        batch.put_item(Item=record)
                        count+=1
                    except Exception as e:
                        print(e)
                        print(record)
            offset += 50
print(offset,len(records),count)


