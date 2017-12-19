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

    for request in requests:
        if request['Status']['Code'] == 'marked-for-termination':
            notify_owner(request['InstanceId'], request['SpotInstanceRequestId'])


def notify_owner(instance_id, spot_id):
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
        print("Will send a message to %s" % (topic_arn))
        client = boto3.client('sns')
        try:
            client.publish(
                TopicArn=topic_arn,
                Message="Your instance %s is about to be terminated - Outbidden" % (instance_id),
                Subject="SPOT INSTANCE TERMINATION"
            )
        except Exception as e:
            print(e)


if __name__ == '__main__':
    notify_owner('','' )
    get_all_spot_requests()
