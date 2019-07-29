import sqs


def main(event, context):
    message = (sqs.extract_body(event))
    print(message)
