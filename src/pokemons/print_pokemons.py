import json
import logging
import os

import requests
import boto3
from botocore.exceptions import ClientError

from .utils import get_current_timestamp

BUCKET_NAME = "pokemon-data-store" 


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        print('HEHRHERH!!!!! ', file_name)
        print('HEHRHERH!!!!! ', bucket)
        print('HEHRHERH!!!!! ', object_name)
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def lambda_handler(event : dict, context: object) -> dict:
    """Sample pure Lambda function
    
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    pokemons = []


    # https://pokeapi.co/api/v2/pokemon

    offset = 0
    page_size = 50
    request_limit = 1
    request_counter = 0
    while (True):
        url = f"https://pokeapi.co/api/v2/pokemon?offset={offset}&limit={page_size}"

        response = requests.get(url)
        request_counter += 1
        response_data = response.json()
        print(f"Queried url: {url}, count: {response_data['count']}")
        pokemons.extend(response_data['results'])

        if response_data['next']:
            offset += page_size
        else:
            break

        if request_counter >= request_limit:
            break

    print(f"Result length!!: {len(pokemons)}")
    logging.info('Saving data to file')

    object_name = f"pokemons|{get_current_timestamp()}.json"
    file_name = f'/tmp/{object_name}'
    with open(file_name, "w") as f:
        f.write(json.dumps(pokemons))
        # s3.upload_fileobj(f, "BUCKET_NAME", "OBJECT_NAME")

    print(os.environ)
    upload_file(file_name, BUCKET_NAME, object_name=object_name)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello pokemon! world",
            # "location": ip.text.replace("\n", "")
        }),
    }
