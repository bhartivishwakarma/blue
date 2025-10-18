# services/sms_service.py
from twilio.rest import Client
from config import Config

def send_sms(to_number, message):
    """Send SMS using Twilio service"""
    
    # For demo purposes, print to console
    print(f"SMS to {to_number}: {message}")
    
    # Uncomment to use actual Twilio service
    """
    if not all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN, Config.TWILIO_PHONE_NUMBER]):
        raise Exception("Twilio credentials not configured")
    
    client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=message,
        from_=Config.TWILIO_PHONE_NUMBER,
        to=f'+91{to_number}'  # Assuming Indian numbers
    )
    
    return message.sid
    """
    
    return "demo_sms_id"