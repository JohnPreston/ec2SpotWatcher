#!/usr/bin/env python

"""

Script to run from within the SpotInstance to see if it's going to get terminated.
Configure the topic URL to send a message via SNS (requires the right IAM profile on the instance).

- Note: virtualenv used python 3.6

"""


import re
import boto3
import requests

def check_spot_status():
    """
    """

    spot_status_url = "http://169.254.169.254/latest/meta-data/spot/termination-time"
    try:
        r = requests.get(spot_status_url, timeout=1)
    except:
        return (False,)

    if r.status_code == 404:
        return (False,)
    elif r.status_code == 200:
        return (True, r.text)

def get_instance_id():
    id_url = "http://169.254.169.254/latest/meta-data/instance_id"
    try:
        r = requests.get(id_url, timeout=1)
        return r.tex
    except:
        return "(Issue getting the instance ID)"



def notify_owner():

    try:
        from user_config import topic_arn
    except Exception as e:
        print (e)

    instance_id = get_instance_id()

    pattern = re.compile('(arn:aws:sns:([a-z]{2})-(east|west|central)-([0-9]{1}):([0-9]{12}):([a-z0-9]{1,256}))?')
    if not pattern.fullmatch(topic_arn):
        print("Invalid ARN for the topic to send the message to")
        return
    else:
        print("Will send a message to %s" % (topic_arn))
        client = boto3.client('sns')
        try:
            client.public(
                TopicArn=topic_arn,
                Message="Your instance %s is about to be terminated - Outbidden" % (instance_id),
                Subject="SPOT INSTANCE TERMINATION"
            )
        except Exception as e:
            print(e)


if __name__ == '__main__':

    check_spot_status()
    notify_owner()
    print("Bye")
