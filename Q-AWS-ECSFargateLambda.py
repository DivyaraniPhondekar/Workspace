import boto3
import smtplib
from email.mime.text import MIMEText
from botocore.exceptions import ClientError
import time
from email.mime.multipart import MIMEMultipart
import datetime
from smtplib import SMTPException
import base64
import ast
import os
import re
from time import sleep
from dateutil.tz import tzutc, tzlocal

def get_secret():
    secret_name = "devops/prod"
    endpoint_url = "https://secretsmanager.us-east-1.amazonaws.com"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )
    try:

        get_secret_value_response = client.get_secret_value(SecretId=secret_name)


    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']


def lambda_handler(event, context):
    #--fetch time-----------------------------------------------------------------------------------------------
    ts = int(time.time())+19800
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S')
    #--fetch information of created cluster---------------------------------------------------------------------------------------------------------
    pwd=get_secret()
    i=eval(pwd)
    j=i.get("devops@quantiphi.com")

    region = event['detail']['awsRegion']
    #print region

    time1 = event['detail']['eventTime']
    date = str(time1.split('T')[0])
    rawtime = str(time1.split('T')[1])
    time1 = str(rawtime.split('Z')[0])
    time1 = date+" "+time1



    print time
    print(type(time))

    rawEmailId = event['detail']['userIdentity']['principalId']
    emailId = str(rawEmailId.split(':')[1])
    #print emailId

    arn = event['detail']['responseElements']['cluster']['clusterArn']
    #print arn

    clustername = event['detail']['requestParameters']['clusterName']
    #print clustername

    #--insert info of created cluster inro dynamodb------------------------------------------------------------------------------------------
    dynamodb = boto3.resource('dynamodb')
    table =dynamodb.Table('ECSMonitoring')

    # Finding max SrNo
    ECSMonitoring = table.scan()
    ECSMonitoring = ECSMonitoring['Items']

    if (len(ECSMonitoring) == 0):
        table.put_item(Item={'SrNo':1,'clustername':clustername,'region':region,'ARN':arn,'emailId':emailId,'time':time1})
    else:
        srlist = []
        for i in range(len(ECSMonitoring)):
            srlist.append(int(ECSMonitoring[i]['SrNo']))
        maxsr = max(srlist)
        table.put_item(Item={'SrNo':maxsr + 1,'clustername':clustername,'region':region,'ARN':arn,'emailId':emailId,'time':time1})


    #--send email to person who have created cluster--------------------------------------------------------------------------------------------
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('devops@quantiphi.com',j)

    record='''
        <tr style="text-align:center">
        <td colspan= "1" style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        <td colspan= "1" style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        <td style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        <td style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        <td style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        <td style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        <td style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        </tr>'''.format('AWS',region,'ECS',arn,clustername,time1,emailId)
    html = """\
            <!DOCTYPE html>
            
<html lang="en">
              
<head>
              
              
<meta charset="utf-8">
              
<meta name="viewport" content="width=device-width, initial-scale=1">
              
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
              

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
              

<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
              

</head>

              

<body>

Hello,<br/>
<br/>
ECS Resource(s) created with below information.<br/>
<br/>
<font color="red">Report if cluster is not created by you.<br/>

<br/>

</font><br/>	

------------------------------------------------------------------------<br/>
<h2>Resource Info</h2><br/>

<div class="container">
              

<table class="table table-condensed">
              
<thead> 

              
<tr style="background:lightblue;color:black"> 
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Account</th> 		  
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Region/Zone</th> 
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Service</th> 			 
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Cluster ARN</th> 
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Cluster Name</th> 
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Launch time(UTC)</th>
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">E-mail</th> 
             
</tr>
</tr>
</thead>
<tbody>
{}		 
</tbody>
</table>
</div>
</body>
</html>""".format(record)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "ECS Resources created "+st+""
    msg['To'] = emailId
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    server.sendmail("devops@quantiphi.com",msg['To'], msg.as_string())
    server.quit()

    return 'Done'
