import os
import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import Client
from django.conf import settings


def send_text(to_number, message):
    twilio_account_sid=os.getenv("twilio_account_sid")
    twilio_auth_token=os.getenv("twilio_auth_token")
    from_number = "whatsapp:+14155238886"

    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_account_sid}/Messages.json"
    payload = {"From": from_number, "To": to_number, "Body": message}

    requests.post(url, auth=HTTPBasicAuth(twilio_account_sid, twilio_auth_token), data=payload)



