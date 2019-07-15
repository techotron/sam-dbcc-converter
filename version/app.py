import json
import requests
import os

app_version = os.getenv("APP_VERSION")
app_name = os.getenv("APP_NAME")

def get_version(event, context):
    try:
        ip = requests.get("http://checkip.amazonaws.com/")
    except requests.RequestException as e:
        print(e)

        raise e

    return {
        "statusCode": 200,
        "body": json.dumps({
            "application": app_name,
            "version": app_version,
            "location": ip.text.replace("\n", "")
        }),
    }
