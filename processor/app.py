import sqs
import boto3
import json
import os


def consume_message(event):
    message = (sqs.extract_body(event))
    return json.dumps(sqs.parse_message(message))


def put_item(data, tableName):
    response = []
    client = boto3.client('dynamodb')
    json_data = json.loads(data)
    for item in json_data:
        item_put = client.put_item(
            TableName=tableName,
            Item={
                'messageId': {"S": item["messageId"]},
                'eventTime': {"S": item["eventTime"]},
                'bucketName': {"S": item["bucketName"]},
                'messageKey': {"S": item["messageKey"]},
                'messageSize': {"S": str(item["messageSize"])},
                'status': {"S": "pending"}
            }
        )
        response.append(item_put)
    return response


def main(event, context):
    ddb_table = os.getenv("DDB_TABLE")
    processed_message = consume_message(event)
    print(put_item(processed_message, ddb_table))


if __name__ == "__main__":
    test_message = {'Records': [{'messageId': 'e413fd82-957c-439c-834b-f4a90d1626df', 'receiptHandle': 'AQEBu3Udeb2SW9xYxB3Nfj3UuReRAgt5shBxP1u3qXIKr3njjXw+K4uYrUo8+xZ9v/w80aSxUU7uhOrUWsDrOffmRKGuPqJTk9kUr3cbGONdaIStOSOIzBGlxKVsulVwqea47xG0QKVjVyBLSpc9g9ckCB26CwC+EQx3lAQG4Fw0gCPbhWmhC7tbZDzlcIdZQXQ9cZPd5nc11NNTo4dos1p99kX5pY61EfVIiP3lRVGyk7GcBrJlTRPt2JySZLLZ+B2P5BEoTVUQFRhwiHx8viSnkemGj3U6mrpifert+/fmmD3dS6ZeXLgiwserBbmHAWdvSLkJ/aFVPxvkwukYMpMYaXA/3vsvpb2aff55dXyr0joH51lP8JNElv2sLSUtUsRsv/loG5sD0/epcbWitV9F5g==', 'body': '{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"eu-west-1","eventTime":"2019-07-15T10:05:01.449Z","eventName":"ObjectCreated:Put","userIdentity":{"principalId":"AWS:AIDAJ6K7DK6VAQXGPRIYC"},"requestParameters":{"sourceIPAddress":"10.88.21.150"},"responseElements":{"x-amz-request-id":"7A8E9393B6C7FA34","x-amz-id-2":"bZqOkuAvKCA/W112UNyJfCvnjDCnbCOrg86S16VC/VZ81//k9N8TyoWH/cglN4LFZSQl1wWDDQc="},"s3":{"s3SchemaVersion":"1.0","configurationId":"f843fcfe-cd7b-4555-b064-20550bfe382f","bucket":{"name":"sam-dbcc-converter-dev-eu-west-1","ownerIdentity":{"principalId":"A3MT01BTHHIYR7"},"arn":"arn:aws:s3:::sam-dbcc-converter-dev-eu-west-1"},"object":{"key":"in/j1tf7l10n25mnbnkf0vngp7heqbs1ej6otivbio1","size":2380287,"eTag":"1b3a2c134fbf0af720686003d430867a","sequencer":"005D2C4FCD5AA60253"}}}]}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1563185102140', 'SenderId': 'AIDAJQOC3SADRY5PEMBNW', 'ApproximateFirstReceiveTimestamp': '1563185102157'}, 'messageAttributes': {}, 'md5OfBody': '0a13527672e86df58d180fa22a5ee282', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-1:722777194664:dbcConverterQueue', 'awsRegion': 'eu-west-1'}]}
    data = consume_message(test_message)
    print(data)
    # put_item(data, "sam-dbcc-converter-dev")



