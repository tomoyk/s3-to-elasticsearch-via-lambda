import boto3
import re
import requests
from requests_aws4auth import AWS4Auth

from parser import parser as parse

import logging
logger = logging.getLogger()

region = 'ap-northeast-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-reiwa0407-bmwrgzepuso6dsiivp3ugyp5x4.ap-northeast-1.es.amazonaws.com' # the Amazon ES domain, including https://
index = 'lambda-s3-index-sample'
type = 'lambda-type2'
url = host + '/' + index + '/' + type

headers = { "Content-Type": "application/json" }

s3 = boto3.client('s3')

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:

        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Get, read, and split the file into lines
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj['Body'].read()
        lines = body.splitlines()
        
        # Match the regular expressions to each line and index the JSON
        for line in lines:
            document = parse(line)
            r = requests.post(url, auth=awsauth, json=document, headers=headers)
            if r.ok >= 400:
                print(r)
            else:
                print("success")

