import json
import datetime
import boto3
import os
import base64
import logging
import decimal


def getLogger(name, LOG_LEVEL=logging.INFO):
    """Return a logger configured based on env variables."""
    logger = logging.getLogger(name)
    # in lambda environment, logging config has already been setup so can't use logging.basicConfig to change log level
    logger.setLevel(LOG_LEVEL)
    return logger

logger = getLogger("CatDog")

# We create our AWS clients
rek_client = boto3.client('rekognition')
sns_client = boto3.client('sns')
ddb_client = boto3.client('dynamodb')

# We hardcode the model version to serve
# This could be parametrized
MODEL_ARN = "arn:aws:rekognition:us-east-1:447262884034:project/catdog-custom-labels/version/catdog-custom-labels.2020-03-07T11.57.47/1583610953438"

# The name of the DynamoDB table with users/api key information
DDB_TABLE = "awscodestar-catdog-infrastructure-User-1CRZT7NCN70OC"

def cat_or_dog(image_data):
    """ Returns whether an image is a cat or dog """

    response = rek_client.detect_custom_labels(
                        ProjectVersionArn=MODEL_ARN,
                        Image={'Bytes':image_data},
                        MaxResults=2)
    logger.info(f"Full response: {response}")

    return response

def send_message(message):
    """ Sends a message to SNS topic """
    sns_topic = os.getenv('snsTopicArn')
    sns_client.publish(TopicArn=sns_topic, Message=message)
    
    
def get_user_name(api_key):
    """ Queries DynamoDB for a user by using the api_key """
    response = ddb_client.get_item(TableName=DDB_TABLE, Key={'api_key':{'S':str(api_key)}}, ProjectionExpression="user_name")
    return response["Item"]["user_name"]["S"]


def increment_user_count(api_key):
    """ Increments the count for a given user """
    response = ddb_client.update_item(
        TableName=DDB_TABLE,
        Key={
            'api_key': {"S":api_key}
        },
        UpdateExpression="set request_count = request_count + :val",
        ExpressionAttributeValues={
            ':val': {"N": "1"}
        },
        ReturnValues="UPDATED_NEW")
    
    return response
    

# Had to follow those instructions to get binary image passed properly via API Gateway
# https://aws.amazon.com/blogs/compute/binary-support-for-api-integrations-with-amazon-api-gateway/
def handler(event, context):
    """ Processes an image """
    
    # We log the whole event
    logger.info(event)
    
    # We get the image from the body payload
    b64_image_data = event["base64Image"]
    image_data = base64.b64decode(b64_image_data)
    
    # We get the API key from the request headers
    api_key = event["headers"]["x-api-key"]
    
    # we get the name of the user based on the API key
    user_name = get_user_name(api_key)
    logger.info(user_name)
    
    # We send a notification to SNS
    message = f"Request from {user_name} received"
    send_message(message)
    
    # We call Rekognition to get classification
    returned_body = cat_or_dog(image_data)
    
    # We increment the count of requests for that given user
    increment_user_count(api_key)
    
    return {'statusCode': 200,
            'body': json.dumps(returned_body),
            'headers': {'Content-Type': 'application/json'}}
