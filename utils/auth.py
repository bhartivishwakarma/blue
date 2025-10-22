# utils/auth.py
import hashlib
import secrets
import string
from datetime import datetime, timedelta
import jwt
from config import Config

class Auth:
    def __init__(self):
        self.secret_key = Config.SECRET_KEY

    def generate_otp(self, length=6):
        """Generate a numeric OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return self.hash_password(password) == hashed

    def generate_passkey(self):
        """Generate a random passkey"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    def create_session_token(self, user_data, expires_hours=24):
        """Create JWT session token"""
        payload = {
            'user_id': user_data.get('mobile'),
            'exp': datetime.utcnow() + timedelta(hours=expires_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_session_token(self, token):
        """Verify JWT session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def generate_remember_token(self):
        """Generate remember me token"""
        return secrets.token_urlsafe(32)

    def create_password_reset_token(self, user_id, expires_minutes=30):
        """Create password reset token"""
        payload = {
            'user_id': user_id,
            'purpose': 'password_reset',
            'exp': datetime.utcnow() + timedelta(minutes=expires_minutes),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_password_reset_token(self, token):
        """Verify password reset token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload.get('purpose') == 'password_reset':
                return payload
            return None
        except:
            return None

    def validate_mobile_number(self, mobile):
        """Validate Indian mobile number"""
        if len(mobile) != 10:
            return False
        if not mobile.isdigit():
            return False
        # Indian mobile numbers start with 6,7,8,9
        if mobile[0] not in ['6', '7', '8', '9']:
            return False
        return True

    def validate_email(self, email):
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def generate_secure_filename(self, original_filename):
        """Generate secure filename for uploads"""
        import hashlib
        import os
        ext = os.path.splitext(original_filename)[1]
        hash_name = hashlib.md5(original_filename.encode() + secrets.token_bytes(8)).hexdigest()
        return f"{hash_name}{ext}"

    def check_password_strength(self, password):
        """Check password strength"""
        if len(password) < 8:
            return "weak"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        score = sum([has_upper, has_lower, has_digit, has_special])
        
        if score == 4:
            return "strong"
        elif score >= 2:
            return "medium"
        else:
            return "weak"

    def generate_api_key(self):
        """Generate API key for external integrations"""
        return secrets.token_urlsafe(32)

    def create_verification_code(self, length=6):
        """Create verification code for email/mobile verification"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    def sanitize_input(self, input_string):
        """Basic input sanitization"""
        import html
        return html.escape(input_string.strip())

    def validate_date_format(self, date_string, format='%Y-%m-%d'):
        """Validate date format"""
        try:
            datetime.strptime(date_string, format)
            return True
        except ValueError:
            return False