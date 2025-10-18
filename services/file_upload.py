# services/file_upload.py
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file, user_id, file_type):
    """Save uploaded file with unique filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{file_type}_{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        file.save(filepath)
        return filename
    
    raise ValueError("Invalid file type")