import json
import boto3
import datetime
import base64
import os
import email
import sys


def status_check(data):
    json_data = json.loads(data)
    for item in json_data:
        return item["status"]


def extract_stream(event):
    output = []
    for record in event["Records"]:
        messageId = record["dynamodb"]["NewImage"]["messageId"]["S"]
        bucket = record["dynamodb"]["NewImage"]["bucketName"]["S"]
        messageKey = record["dynamodb"]["NewImage"]["messageKey"]["S"]
        status = record["dynamodb"]["NewImage"]["status"]["S"]

        event_details = {
            'messageId': messageId,
            'bucket': bucket,
            'messageKey': messageKey,
            'status': status
        }

        output.append(event_details)
    return json.dumps(output)


def download_message(stream_data):
    s3 = boto3.resource('s3')
    json_data = json.loads(stream_data)
    for item in json_data:
        messageId = item["messageId"]
        s3.meta.client.download_file(item["bucket"], item["messageKey"], '/tmp/' + messageId + '.eml')

    return '/tmp/' + messageId + '.eml'


def extract_message(file):
    def json_serial(obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()
            return serial

    with open(file, 'rb') as fhdl:
        raw_email = fhdl.read()

    decoded_raw_email = raw_email.decode('UTF-8')
    message_from_string = email.message_from_string(decoded_raw_email)

    for part in message_from_string.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            filePath = os.path.join('/tmp/', fileName)
            if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
            email_subject = str(message_from_string).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
            email_from_address = str(message_from_string).split("From: ", 1)[1].split("\nDate:", 1)[0].split("<")[1].replace("<","").replace(">", "")
            email_attachment_file_name = fileName

    messageId = file.split("/")[2].replace(".eml", "")
    add_email_details(messageId, email_from_address)

    # Comment out to prevent stream update loop
    # update_status(messageId, "extracted_attachment", ddb_table)

    return '/tmp/' + email_attachment_file_name


def upload_attachment(filename, data):
    response = []
    ddb_table = os.getenv("DDB_TABLE")
    json_data = json.loads(data)
    for item in json_data:
        message_id = item["messageId"]
        bucket = item["bucket"]

        s3 = boto3.resource('s3')
        dest_key = "attachments/%s.dbc" % message_id
        s3.Bucket(bucket).upload_file(filename, dest_key)

        # Comment out to prevent stream update loop
        # update_status(message_id, "attachment_uploaded", ddb_table)
        s3_object = {
            "bucketName": bucket,
            "objectKey": dest_key
        }
        response.append(s3_object)

    print(json.dumps(response))
    return json.dumps(response)


def update_status(messageId, status_message, table_name):
    client = boto3.client('dynamodb')
    item_get = client.get_item(
        TableName=table_name,
        Key={
            'messageId': {"S": messageId}
        }
    )

    item_get["Item"]["status"]["S"] = status_message

    item_put = client.put_item(
        TableName=table_name,
        Item=item_get["Item"]
    )


def add_email_details(messageId, email_address):
    ddb_table = os.getenv("DDB_TABLE")
    client = boto3.client('dynamodb')
    item_get = client.get_item(
        TableName=ddb_table,
        Key={
            'messageId': {"S": messageId}
        }
    )

    print(item_get["Item"])

    # item_get["Item"]["emailaddress"]["S"] = email_address
    # item_get["Item"]["status"]["S"] = "processing"
    #
    # item_put = client.put_item(
    #     TableName=table_name,
    #     Item=item_get["Item"]
    # )


def send_sqs_message(body):
    sqs_queue_url = os.getenv("SQS_CONVERTER_QUEUE")
    sqs = boto3.client('sqs')

    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageAttributes={},
        MessageBody=body
    )
    print(body)


def main(event, context):
    data = extract_stream(event)

    if status_check(data) == "pending":

        email_file = download_message(data)

        extracted_attachment = extract_message(email_file)

        uploaded_attachments = upload_attachment(extracted_attachment, data)

        send_sqs_message(uploaded_attachments)


if __name__ == "__main__":
    test_stream = {'Records': [{'eventID': 'ac37c9a827bc7b2dd4b5138370cc5e9d', 'eventName': 'INSERT', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'eu-west-1', 'dynamodb': {'ApproximateCreationDateTime': 1563200821.0, 'Keys': {'messageId': {'S': '91ac053d-5110-4dd5-a413-34538c12e9df'}}, 'NewImage': {'bucketName': {'S': 'sam-dbcc-converter-dev-eu-west-1'}, 'messageKey': {'S': 'in/ofak20804gklf2e0j38hgt5gkp3h0qicvei382g1'}, 'eventTime': {'S': '2019-07-15T13:58:41.944Z'}, 'messageId': {'S': '91ac053d-5110-4dd5-a413-34538c12e9df'}, 'messageSize': {'S': '85714'}, 'status': {'S': 'pending'}}, 'SequenceNumber': '239900000000000614529657', 'SizeBytes': 247, 'StreamViewType': 'NEW_IMAGE'}, 'eventSourceARN': 'arn:aws:dynamodb:eu-west-1:722777194664:table/sam-dbcc-converter-dev/stream/2019-07-15T14:12:06.786'}]}
    temp_file = "/tmp/j1tf7l10n25mnbnkf0vngp7heqbs1ej6otivbio1.eml"

    # main(test_stream, "")
    print(extract_message(temp_file))
    # upload_attachment(attachment_data)