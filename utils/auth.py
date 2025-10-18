# utils/auth.py
import random
import hashlib
import secrets
from datetime import datetime, timedelta
import mysql.connector
from config import Config

def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    digits = "0123456789"
    return ''.join(random.choice(digits) for _ in range(length))

def verify_otp(entered_otp, stored_otp):
    """Verify if the entered OTP matches the stored one"""
    return entered_otp == stored_otp

def hash_password(password):
    """Hash a password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_passkey(user_id):
    """Set up passkey authentication for user"""
    # Generate a simple numeric passkey for demo
    # In production, use proper biometric or hardware key authentication
    passkey = str(random.randint(100000, 999999))
    hashed_passkey = hash_password(passkey)
    
    # Store in database
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET has_passkey = TRUE, passkey_data = %s WHERE id = %s",
        (hashed_passkey, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return passkey  # In production, don't return the actual passkey

def verify_passkey(user_id, entered_passkey):
    """Verify user passkey"""
    hashed_entered = hash_password(entered_passkey)
    
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT passkey_data FROM users WHERE id = %s AND has_passkey = TRUE",
        (user_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result and result['passkey_data'] == hashed_entered