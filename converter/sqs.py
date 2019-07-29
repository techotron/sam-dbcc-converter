import datetime
import json


def get_timestamp():
    timestamp = datetime.datetime.today()
    return timestamp


def parse_message(message):
    output = []
    json_message = json.loads(message)

    for item in json_message:
        body = item["body"]
        message_id = item["messageId"]
        records = json.loads(body)["Records"]

        for record in records:
            event_time = record["eventTime"]
            s3_details = record["s3"]
            bucket_name = s3_details["bucket"]["name"]
            object_key = s3_details["object"]["key"]
            message_size = s3_details["object"]["size"]

            item = {
                "messageId": message_id,
                "eventTime": event_time,
                "bucketName": bucket_name,
                "messageKey": object_key,
                "messageSize": message_size
            }
            output.append(item)
    return output


def extract_body(event):
    output = []
    for record in event['Records']:
        record = {
            "messageId": record["messageId"],
            "body": record["body"]
        }
        output.append(record)
    return json.dumps(output)
