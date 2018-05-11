import boto3
import datetime
import json
import re

# to Get Email tag from Instance
def descEC2(InstanceId):
    # EC2 client from boto3
    ec2client = boto3.client('ec2')
    Email = ''
    Username = ''
    print "EC2 Function : ",InstanceId
    # Request for the EC2 instance Details to get Email tag
    response = ec2client.describe_instances(
        InstanceIds=[
            InstanceId,
        ]
    )
    tags = ''
    print "EC2 Response : ",str(response)
    # if not null response then get all Tags
    if response!='':
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        print "EC2 Tags : ",str(tags)
    # Traversing through tags to get Email tag
    for t in tags:
        if str.lower(t.get('Key'))=='email':
            Email = t.get('Value')
            print "EC2 Email : ",Email
        if str(t.get('Key')).lower()=='username':
            Username = t.get('Value')
            print "EC2 Username : ",Username
        if re.match(email,Email) or re.match(email,Username):
            break
    # Returns the Email to calling function
    if re.match(email,Email):
        return Email
    elif re.match(email,Username):
        return Username
    else :
        print Email,Username
        return ''

# to Get Email tag from Lambda
def descLambda(funName):
    email = '[a-zA-Z]+\.[a-zA-Z]+@quantiphi\.com'

    lambdaClient = boto3.client('lambda')
    # Request for the Lambda Details to get Email tag
    response = lambdaClient.get_function(
        FunctionName=funName
        )
    print 'Lambda Function :',funName
    print 'Lambda Response :',str(response)
    print 'This is tags output :',response['Tags']

    try:
        # get Email tag from Response from Lambda Details
        if response['Tags']:
            print 'Tags :',response['Tags']
            for t in response['Tags']:
                print t,response['Tags'][t]
                if re.match(email,response['Tags'][t]):
                    return response['Tags'][t]
    except Exception, e:
        print e


# It add username(value = Email id) tag to all the nodes of redis cluster
def addtag(arn,Email,region):
    # A client representing Amazon ElastiCache:
    elasticacheclient = boto3.client('elasticache', region_name=region)
    try:
        response = elasticacheclient.add_tags_to_resource(ResourceName=str(arn),
        Tags=[{
            'Key': 'username',
            'Value': str(Email)
            }]
            )
        print 'Done'
    except Exception as e:
        pass

def list_instances_by_tag_value(region):
    Email = ''
    # A client representing Amazon ElastiCache and cloudtrail
    cloudtrailclient = boto3.client('cloudtrail', region_name=region)
    elasticacheclient = boto3.client('elasticache', region_name=region)

    # Python function to take current datetime details
    current = datetime.datetime.now()
    year = current.year
    month = current.month
    day = current.day

    # Day and month logic applied to get the next date of current date
    # responce1 ------> memcached cluster info of current day
    # responce2 ------> redis cluster info of current day
    if (day == 31 and month in [1,3,5,7,8,10,12]):
        day1 = 1
        month1 = month + 1
        response1 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateCacheCluster'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month1,day1))
        response2 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateReplicationGroup'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month1,day1))


    elif (day == 30 and month in [4,6,9,11]):
        day1 = 1
        month1 = month + 1
        response1 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateCacheCluster'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month1,day1))
        response2 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateReplicationGroup'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month1,day1))

    elif ((day == 28 or day == 29) and month == 2):
        day1 = 1
        month1 = month + 1
        response1 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateCacheCluster'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month1,day1))
        response2 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateReplicationGroup'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month1,day1))

    else:
        day1 = day + 1
        response1 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateCacheCluster'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month,day1))
        response2 = cloudtrailclient.lookup_events(LookupAttributes=[{'AttributeKey': 'EventName','AttributeValue': 'CreateReplicationGroup'},],StartTime=datetime.datetime(year,month,day),EndTime=datetime.datetime(year,month,day1))

    if response1['Events']:
        clustername = response1['Events'][0]['CloudTrailEvent']
        # Handling lazy JSON in Python---------
        dicti = json.loads(clustername)
        resource = dicti['responseElements']['cacheClusterId']
        print (resource)

        letEmail = response1['Events'][0]['Username']

        # Syntax:
        # arn:aws:elasticache:region:account-id:resourcetype:resourcename
        arn = 'arn:aws:elasticache:'+str(region)+':130159455024:cluster:'+str(resource)
        # Expressions to test letEmail
        email = '[a-zA-Z]+\.[a-zA-Z]+@quantiphi\.com'
        ec2 = 'i-+\w'
        lam = '[a-zA-Z0-9_-]'
        try:
            if re.match(email,letEmail):
                Email = letEmail
            elif re.match(ec2,letEmail):
                print "Calling ec2 function"
                Email = descEC2(letEmail)
            elif re.match(lam,letEmail):
                Email = descLambda(letEmail)
            print 'Final Extracted :',Email
            if re.match(email,Email):
                try:
                    response = elasticacheclient.add_tags_to_resource(ResourceName=str(arn),
                    Tags=[{
                        'Key': 'username',
                        'Value': str(Email)
                        }]
                        )
                    print 'Done'
                except Exception as e:
                    pass
            else :
                print Email
        except Exception as e:
            print e


    if response2['Events']:
        letEmail = response2['Events'][0]['Username']
        print (letEmail)

        # Expressions to test letEmail
        email = '[a-zA-Z]+\.[a-zA-Z]+@quantiphi\.com'
        ec2 = 'i-+\w'
        lam = '[a-zA-Z0-9_-]'

        # it gives the details about all nodes of redis cache
        response = elasticacheclient.describe_cache_clusters()
        if response['CacheClusters']:
            clusters = response['CacheClusters']
            for i in range(len(clusters)):
                resource = response['CacheClusters'][i]['CacheClusterId']
                print (resource)
                arn = 'arn:aws:elasticache:'+str(region)+':130159455024:cluster:'+str(resource)

                try:
                    if re.match(email,letEmail):
                        Email = letEmail
                    elif re.match(ec2,letEmail):
                        print "Calling ec2 function"
                        Email = descEC2(letEmail)
                    elif re.match(lam,letEmail):
                        Email = descLambda(letEmail)
                    print 'Final Extracted :',Email
                    if re.match(email,Email):
                        print (resource)
                        addtag(arn,Email,region)
                    else :
                        print Email
                except Exception as e:
                    print e

# Entry Point---->
def lambda_handler(event,context):
    # Tag the elasticache clusters of frequently used regions i.e. Oregon, N. Virginia, Ohio
    regions=['us-west-2','us-east-1','us-east-2']
    for region in regions:
        list_instances_by_tag_value(region)

    return "Executed"
