import json
import boto3
import eml_parser
import datetime
import base64
import os


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
    ddb_table = os.getenv("DDB_TABLE")

    def json_serial(obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()
            return serial

    with open(file, 'rb') as fhdl:
        raw_email = fhdl.read()

    parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email, include_attachment_data=True)

    email_from_address = parsed_eml["header"]["from"]
    email_subject = parsed_eml["header"]["subject"]
    email_attachment_file_name = parsed_eml["attachment"][0]["filename"]
    attachment = parsed_eml["attachment"][0]["raw"].decode('UTF-8')
    output_filename = '/tmp/' + email_attachment_file_name

    data = base64.b64decode(attachment)
    output_file = open(output_filename, "wb")
    output_file.write(data)
    output_file.close()

    messageId = file.split("/")[2].replace(".eml", "")
    update_status(messageId, "extracted_attachment", ddb_table)

    return output_filename


def upload_attachment(filename, data):
    ddb_table = os.getenv("DDB_TABLE")
    json_data = json.loads(data)
    for item in json_data:
        message_id = item["messageId"]
        bucket = item["bucket"]

    update_status(message_id, "attachment_uploaded", ddb_table)

    print(json_data)
    print(message_id)


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


def main(event, context):
    data = extract_stream(event)

    email_file = download_message(data)

    extracted_attachment = extract_message(email_file)

    upload_attachment(extracted_attachment, data)


if __name__ == "__main__":
    test_stream = {'Records': [{'eventID': 'ac37c9a827bc7b2dd4b5138370cc5e9d', 'eventName': 'INSERT', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'eu-west-1', 'dynamodb': {'ApproximateCreationDateTime': 1563200821.0, 'Keys': {'messageId': {'S': '91ac053d-5110-4dd5-a413-34538c12e9df'}}, 'NewImage': {'bucketName': {'S': 'sam-dbcc-converter-dev-eu-west-1'}, 'messageKey': {'S': 'in/ofak20804gklf2e0j38hgt5gkp3h0qicvei382g1'}, 'eventTime': {'S': '2019-07-15T13:58:41.944Z'}, 'messageId': {'S': '91ac053d-5110-4dd5-a413-34538c12e9df'}, 'messageSize': {'S': '85714'}, 'status': {'S': 'pending'}}, 'SequenceNumber': '239900000000000614529657', 'SizeBytes': 247, 'StreamViewType': 'NEW_IMAGE'}, 'eventSourceARN': 'arn:aws:dynamodb:eu-west-1:722777194664:table/sam-dbcc-converter-dev/stream/2019-07-15T14:12:06.786'}]}
    temp_file = "/tmp/91ac053d-5110-4dd5-a413-34538c12e9df.eml"

    main(test_stream, "")
    # attachment_data = extract_message(temp_file)
    # upload_attachment(attachment_data)