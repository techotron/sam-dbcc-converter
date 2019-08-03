import sqs
import json
import os
import boto3
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


def send_email(recipient, subject, attachment_file, attachment_filename):
    msg = MIMEMultipart()
    msg['Subject'] = 'RE: ' + subject
    msg['From'] = 'no-reply@snow-online.co.uk'
    msg['To'] = recipient

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'Multipart message.\n'

    # the message body
    part = MIMEText('DBCC Converter - file converted to excel spreadsheet')
    msg.attach(part)

    # the attachment
    part = MIMEApplication(open(attachment_file, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
    msg.attach(part)

    sesClient = boto3.client('ses')
    result = sesClient.send_raw_email(
        Source=msg['From'],
        Destinations=[
            msg['To'],
        ],
        RawMessage={
            'Data': msg.as_string()
        }
    )

    print(result)


def consume_message(event):
    message = (sqs.extract_body(event))
    return json.dumps(sqs.parse_message(message))


def return_email(data):
    table_name = os.getenv("DDB_TABLE")
    s3 = boto3.resource('s3')
    client = boto3.client('dynamodb')
    json_data = json.loads(data)
    for item in json_data:
        key = item["messageKey"]
        bucket = item["bucketName"]
        messageId = key.split("/")[-1].replace(".xlsx","")
        s3.meta.client.download_file(bucket, key, '/tmp/' + messageId + '.xlsx')

    item_get = client.get_item(
        TableName=table_name,
        Key={
            'messageId': {"S": messageId}
        }
    )

    email_address = item_get["Item"]["emailAddress"]["S"]
    email_subject = item_get["Item"]["subject"]["S"]
    attachment_name = item_get["Item"]["attachmentName"]["S"].replace(".dbc",".xlsx")

    send_email(email_address, email_subject, '/tmp/' + messageId + '.xlsx', attachment_name)


def main(event, context):
    processed_message = consume_message(event)
    return_email(processed_message)
