# sam-dbcc-converter
A serverless application to convert dbcc files into excel


disable ses rule set for now so that the default new file that is created by amazon doesn't cause problems with the ddb stream processor logic

TODO: need to add some logic to check if file says "AMAZON SES" something, not to add to DDB.


example run command:

```bash
sam build && sam package --output-template-file packaged.yaml --s3-bucket snowco-sam-eu-west-1 && sam deploy --template-file packaged.yaml --stack-name sam-dbcc-converter --capabilities CAPABILITY_IAM --region eu-west-1 --parameter-overrides AppVersion=v0.1 
```