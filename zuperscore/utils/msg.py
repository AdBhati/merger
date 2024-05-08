import requests
from twilio.rest import Client


def send_sms(mobile_number, otp):

    account_sid = "AC7a98ee130a3052a3efaf603ee969857c"
    auth_token = "7ebbb055af1379f1e91fd911191f7898"
    client = Client(account_sid, auth_token)
    to_number = f"+{mobile_number}"
    body = (
        f"{otp} is your OTP for Zuperscore. Please do not share this OTP with anyone."
    )
    message = client.messages.create(
        messaging_service_sid="MG8b50f203cf10c2534dd30ba5fca7e42d",
        body=body,
        to=to_number,
    )
    response = message.sid
    return response
