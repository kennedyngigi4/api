import os
import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import Client


def send_text(to_number, message):
    twilio_account_sid="AC13cb37c0bcbced8df1ae37f8005ca87e"
    twilio_auth_token="52bce1d6807962b0e8c29865da5c612d"
    from_number = "whatsapp:+14155238886"

    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_account_sid}/Messages.json"
    payload = {"From": from_number, "To": to_number, "Body": message}

    requests.post(url, auth=HTTPBasicAuth(twilio_account_sid, twilio_auth_token), data=payload)



