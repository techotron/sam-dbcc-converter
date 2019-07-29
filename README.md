# sam-dbcc-converter
A serverless application to convert dbcc files into excel

example build/package and deploy command:

```bash
sam build && sam package --output-template-file packaged.yaml --s3-bucket snowco-sam-eu-west-1 && sam deploy --template-file packaged.yaml --stack-name sam-dbcc-converter --capabilities CAPABILITY_IAM --region eu-west-1 --parameter-overrides AppVersion=v0.1 
```