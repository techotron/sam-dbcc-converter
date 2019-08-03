import boto3
import json


def put_item(data, tableName):

    json_data = json.loads(data)
    return json_data
