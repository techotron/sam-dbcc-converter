import datetime
import json


def get_timestamp():
    timestamp = datetime.datetime.today()
    return timestamp


def extract_body(event):
    output = []
    for record in event['Records']:
        record = {
            "messageId": record["messageId"],
            "body": record["body"]
        }
        output.append(record)
    return json.dumps(output)
