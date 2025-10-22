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
        
        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filename
    
    raise ValueError("Invalid file type or no file provided")

def get_file_path(filename):
    """Get full file path for a given filename"""
    return os.path.join(Config.UPLOAD_FOLDER, filename)

def delete_uploaded_file(filename):
    """Delete uploaded file"""
    try:
        filepath = get_file_path(filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")
    return False

def get_file_size(filename):
    """Get file size in bytes"""
    try:
        filepath = get_file_path(filename)
        return os.path.getsize(filepath)
    except:
        return 0