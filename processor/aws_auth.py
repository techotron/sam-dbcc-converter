import boto3
import json


def put_item(data, tableName):

    json_data = json.loads(data)
    return json_data

    # client = boto3.client('dynamodb')
    # response = client.put_item(
    #     TableName=tableName,
    #     Item={
    #         'ComputerName': '%s' % computer,
    #         'IP': '%s' % ip
    #     })
    #
    # return response
