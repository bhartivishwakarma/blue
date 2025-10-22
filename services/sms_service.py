# services/sms_service.py
from twilio.rest import Client
from config import Config
import random

def send_sms(to_number, message):
    """Send SMS using Twilio service"""
    
    # For demo purposes, print to console and generate random OTP
    print(f"SMS to {to_number}: {message}")
    
    # If Twilio credentials are configured, use actual service
    if all([Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN, Config.TWILIO_PHONE_NUMBER]):
        try:
            client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=message,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=f'+91{to_number}'  # Assuming Indian numbers
            )
            
            return message.sid
        except Exception as e:
            print(f"Twilio error: {e}")
            return f"demo_sms_{random.randint(1000, 9999)}"
    
    return f"demo_sms_{random.randint(1000, 9999)}"

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_sms(mobile_number):
    """Send OTP to mobile number"""
    otp = generate_otp()
    message = f"Your BlueCollarResume verification code is: {otp}. Valid for 10 minutes."
    
    sms_id = send_sms(mobile_number, message)
    return otp, sms_id

def verify_otp_sms(mobile_number, entered_otp, stored_otp):
    """Verify OTP entered by user"""
    return entered_otp == stored_otp