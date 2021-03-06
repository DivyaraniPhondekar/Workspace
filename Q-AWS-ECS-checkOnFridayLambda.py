import boto3,json
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import datetime
import smtplib
from email.mime.text import MIMEText
from botocore.exceptions import ClientError
import time
from email.mime.multipart import MIMEMultipart
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
    ts = int(time.time())+19800
    currenttime = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S')

    pwd=get_secret()
    i=eval(pwd)
    j=i.get("devops@quantiphi.com")

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ECSMonitoring')

    client = boto3.client('ecs')
    response = client.list_clusters()

    Arns = response['clusterArns']

    for i in Arns:
        print i
        response1 = table.scan(FilterExpression=Attr('ARN').eq(i))
        try:
            DBtime=response1['Items'][0]['time']
            t = datetime.datetime(int(DBtime[0:4]), int(DBtime[5:7]), int(DBtime[8:10]), int(DBtime[11:13]), int(DBtime[14:16]), int(DBtime[17:19]))
            v=time.mktime(t.timetuple())
            u=int(v)+19800
            Dbtime1 = datetime.datetime.fromtimestamp(u).strftime('%Y/%m/%d %H:%M:%S')

            DBarn=response1['Items'][0]['ARN']
            DBclustername=response1['Items'][0]['clustername']
            DBregion=response1['Items'][0]['region']
            print DBregion
            DBemail=response1['Items'][0]['emailId']
            print(DBtime1,DBarn,DBclustername,DBregion,DBemail)

        except Exception as e:
            pass

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
        <td style="padding:10px;text-align:left;border-collapse:collapse;border:lightblue solid thin"><p style="color: black;">{}</p></td>
        </tr>'''.format('AWS',DBregion,'ECS',DBarn,DBclustername,Dbtime1,currenttime,DBemail)
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
ECS cluster(s) available with below information.<br/>
<br/>
<font color="red">Delete it, if you are not using.<br/>
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
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Launch time(IST)</th>
<th rowspan="4" style="padding:10px;text-align:center;border-collapse:collapse;border:lightblue solid thin">Current time(IST)</th>
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
    msg['Subject'] = "ECS Resources monitoring "+currenttime+""
    #msg['To']="divyarani.phondekar@quantiphi.com"
    #msg['To']="nikhil.padghan@quantiphi.com"
    msg['To'] = DBemail
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    server.sendmail("devops@quantiphi.com",msg['To'], msg.as_string())
    server.quit()

    return 'Hello from Lambda'
