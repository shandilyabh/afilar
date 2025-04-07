"""
Function responsible for sending a slack notification
via the slack webhook URL.
"""

import os
import json
from dotenv import load_dotenv # type: ignore
import requests
import datetime

load_dotenv()
slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

def format_notification(timestamp: datetime.datetime, notification_type: str, object_location: str) -> str:
    '''
    function to format a spoof attempt slack notification
    parameters: 
        timestamp: datetime object
        notification_type: type of notification (spoof or pdf)
        location: location of the object (PDF or image)
    returns:
        formatted string for slack notification
    '''
    if notification_type == "spoof":
        return f"*Spoof Attempt* at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
    elif notification_type == "pdf":
        return f"*PDF generated* at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
    else:
        raise ValueError("Invalid notification type. Use 'spoof' or 'pdf'.") 

def send_to_slack(slack_webhook: str, timestamp: datetime.datetime, notification_type: str, object_location: str) -> None:
    '''
    function to send the slack notification
    '''
    try:
        message = format_notification(timestamp, notification_type, object_location)
        payload = {"text": message}
        response = requests.post(slack_webhook, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")
    except ValueError:
        print("Error sending to Slack. Invalid notification type. Use 'spoof' or 'pdf'.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Slack: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Slack notification sent.")
    return None

# usage:
# send_to_slack(slack_webhook, datetime.datetime.now(), "spoof", "some://url.where.image/is_stored.jpg")