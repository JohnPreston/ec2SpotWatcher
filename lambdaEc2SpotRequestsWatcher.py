#!/usr/bin/env python

"""

The lambda version to see if the Status of the Spot reservation changed.
Run every 1 minute via CloudWatch Rules

"""

import re
import json
import boto3


def get_all_spot_requests():
    """
    """
    client = boto3.client('ec2')
    requests = client.describe_spot_instance_requests()['SpotInstanceRequests']
    marked = 0

    for request in requests:
        if request['Status']['Code'] == 'marked-for-termination':
            marked += 1
            notify_owner(request['InstanceId'], request['SpotInstanceRequestId'])
    print("All Spot Instances have been reviewed : %d - %d" % (len(requests), marked))


def notify_owner(instance_id, spot_id, fleet_id=None):
    """
    """
    try:
        from user_config import topic_arn
    except Exception as e:
        print (e)

    if not 'topic_arn' in locals():
        print("No topic ARN could be found, neither in the user_config.py file or in the variables of that script file")
        return


    pattern = re.compile('(arn:aws:sns:([a-z]{2})-(east|west|central)-([0-9]{1}):([0-9]{12}):([a-z0-9]{1,256}))?')
    if not pattern.fullmatch(topic_arn):
        print("Invalid ARN for the topic to send the message to")
        return
    else:
        termination_info = {
            'default': 'Instance %s is marked for termination' % (instance_id),
            'instance_id': instance_id,
            'spot_id': 'spot_id'
        }
        if fleet_id is not None:
            termination_info['fleet_id'] = fleet_id

        client = boto3.client('sns')
        try:
            client.publish(
                TopicArn=topic_arn,
                Message=json.dumps(termination_info),
                MessageStructure='json',
                Subject="marked-for-termination"
            )
            print("Message successfully sent to %s" % (topic_arn))
        except Exception as e:
            print(e)


def lambda_handler(event, context):
    """
    """
    get_all_spot_requests()


if __name__ == '__main__':
    get_all_spot_requests()
