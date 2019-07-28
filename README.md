# sam-dbcc-converter
A serverless application to convert dbcc files into excel


disable ses rule set for now so that the default new file that is created by amazon doesn't cause problems with the ddb stream processor logic

TODO: need to add some logic to check if file says "AMAZON SES" something, not to add to DDB.