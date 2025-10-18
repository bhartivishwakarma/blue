# config.py
import os
from datetime import timedelta

class Config:
    DB_CONFIG = {
        
        'host': 'localhost',
        'user': 'root',
        'password': 'Demo@100',
        'database': 'bluecollar_resume',
        'auth_plugin': 'mysql_native_password'
    }
    
    MYSQL_HOST = DB_CONFIG['host']
    MYSQL_USER = DB_CONFIG['user']              
    MYSQL_PASSWORD = DB_CONFIG['password']
    MYSQL_DATABASE = DB_CONFIG['database']  

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'instance/resumes'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # SMS Service Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')