import boto3,json
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

def lambda_handler(event, context):

    # delete ECS Clutser---------------------------------------------------
    # client = boto3.client('ecs')
    # response = client.delete_cluster(cluster='tagger')
    # print(response)

    # Time split-----------------------------------------------------------
    # time = '2018-05-09T10:05:05Z'
    # date = str(time.split('T')[0])
    # rawtime = str(time.split('T')[1])
    # time = str(rawtime.split('Z')[0])
    # print date+" "+time


    # convert unicode json to python string--------------------------------
    # x={u'a': u'aValue', u'b': u'bValue', u'c': u'cValue'}
    # y=json.dumps(x)
    # print y


    # Get data from DB and check with available ECS clusters--------------------------------------------
    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table('ECSMonitoring')

    # client = boto3.client('ecs')
    # response = client.list_clusters()

    # Arns = response['clusterArns']
    # print len(Arns)
    # print Arns
    # for i in Arns:
    #     print i
    #     response1 = table.scan(FilterExpression=Attr('ARN').eq(i))
    #     try:
    #         print (response1['Items'][0]['time'])
    #     except Exception as e:
    #         pass
    # print datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    return 'Hello from Lambda'
