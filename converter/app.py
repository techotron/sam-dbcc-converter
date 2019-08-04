import sqs
import os
import canmatrix.convert
import json
import boto3


def convert_dbc(files):
    out_files = []
    for file in files:
        file_name = file.split("/")[-1].replace(".dbc", "").replace(".DBC", "")
        print(file)
        print(file_name)
        canmatrix.convert.convert(file, '/tmp/' + file_name + '.xlsx')
        out_files.append('/tmp/' + file_name + '.xlsx')
    return out_files


def download_files(files):
    s3 = boto3.resource('s3')
    for file in files:
        s3.meta.client.download_file(item["bucket"], item["messageKey"], '/tmp/' + messageId + '.eml')


def download_s3_object(message):
    files = []
    s3 = boto3.resource('s3')
    json_message = json.loads(message)
    for items in json_message:
        for s3_objects in json.loads(items["body"]):
            file_name = s3_objects["objectKey"].split("/")[-1]
            s3.meta.client.download_file(s3_objects["bucketName"], s3_objects["objectKey"], '/tmp/' + file_name)
            files.append('/tmp/' + file_name)
    return files


def upload_s3_object(files):
    bucket = os.getenv("S3_BUCKET_NAME")
    s3 = boto3.resource('s3')
    for file in files:
        print("Uploading %s to %s" % (file, 'processed/' + file.split("/")[-1]))
        s3.Bucket(bucket).upload_file(file, 'processed/' + file.split("/")[-1])


def main(event, context):
    message = (sqs.extract_body(event))

    files_to_convert = download_s3_object(message)

    processed_files = convert_dbc(files_to_convert)

    upload_s3_object(processed_files)


if __name__ == "__main__":
    test = [{'messageId': 'a32d7408-48d5-492f-9204-ea206da3b4a0', 'body': '[{"bucketName": "sam-dbcc-converter-dev-eu-west-1", "objectKey": "attachments/e28abd7f-73ef-43c6-8ab7-9b60c465e119.dbc"}]'}]
    anotherTest = "/tmp/e28abd7f-73ef-43c6-8ab7-9b60c465e119.xlsx"