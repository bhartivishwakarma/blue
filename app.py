
from flask import Flask,render_template, request, redirect, url_for, session, flash, send_file, jsonify
import mysql.connector
from config import Config
from services.file_upload import save_uploaded_file
from services.sms_service import send_sms
from utils.resume_generator import generate_resume_pdf
from utils.translation import translator
from utils.speech_recognition import transcribe_audio
from utils.ai_helper import AIHelper
from utils.job_recommender import JobRecommender
from utils.auth import Auth
from services.assistant_service import assistant_bp     

import json
import random
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
app.register_blueprint(assistant_bp)

# COMPLETE profession configuration with ALL professions
PROFESSIONS_CONFIG = {
    "Driver": {
        "icon": "fas fa-truck",
        "fields": [
            {"name": "license_number", "label": "Driving License Number", "type": "text", "required": True},
            {"name": "vehicle_type", "label": "Vehicle Type", "type": "select", "options": ["Car", "Motorcycle", "Truck", "Bus", "Auto Rickshaw"], "required": True},
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "areas_covered", "label": "Areas Covered", "type": "text", "required": False},
            {"name": "license_type", "label": "License Type", "type": "select", "options": ["LMV", "MCWG", "HMV", "Transport"], "required": True}
        ]
    },
    "Electrician": {
        "icon": "fas fa-bolt", 
        "fields": [
            {"name": "license_number", "label": "Electrician License Number", "type": "text", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Domestic", "Industrial", "Commercial", "Automotive"], "required": True},
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "certifications", "label": "Certifications", "type": "text", "required": False},
            {"name": "wiring_types", "label": "Wiring Types Known", "type": "text", "required": False}
        ]
    },
    "Plumber": {
        "icon": "fas fa-faucet",
        "fields": [
            {"name": "license_number", "label": "Plumber License Number", "type": "text", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Residential", "Commercial", "Industrial", "Pipeline"], "required": True},
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "pipe_materials", "label": "Pipe Materials Worked With", "type": "text", "required": False},
            {"name": "tools", "label": "Tools Available", "type": "text", "required": False}
        ]
    },
    "Carpenter": {
        "icon": "fas fa-hammer",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Furniture", "Cabinet", "Construction", "Repair"], "required": True},
            {"name": "wood_types", "label": "Wood Types Worked With", "type": "text", "required": False},
            {"name": "tools", "label": "Tools Available", "type": "text", "required": False},
            {"name": "projects_completed", "label": "Projects Completed", "type": "number", "required": False}
        ]
    },
    "Mechanic": {
        "icon": "fas fa-tools",
        "fields": [
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Car", "Motorcycle", "Heavy Vehicle", "AC Repair", "General"], "required": True},
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "certifications", "label": "Certifications", "type": "text", "required": False},
            {"name": "tools", "label": "Tools Available", "type": "text", "required": False},
            {"name": "brands_expertise", "label": "Brands Expertise", "type": "text", "required": False}
        ]
    },
    "Welder": {
        "icon": "fas fa-fire",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "welding_types", "label": "Welding Types", "type": "select", "options": ["Arc", "MIG", "TIG", "Gas", "Spot"], "required": True},
            {"name": "materials", "label": "Materials Worked With", "type": "text", "required": False},
            {"name": "certifications", "label": "Welding Certifications", "type": "text", "required": False},
            {"name": "safety_training", "label": "Safety Training", "type": "select", "options": ["Yes", "No"], "required": True}
        ]
    },
    "Construction Worker": {
        "icon": "fas fa-hard-hat",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Masonry", "Painting", "Welding", "Scaffolding", "General Labor"], "required": True},
            {"name": "skills", "label": "Specific Skills", "type": "text", "required": False},
            {"name": "tools", "label": "Tools Available", "type": "text", "required": False},
            {"name": "safety_certifications", "label": "Safety Certifications", "type": "text", "required": False}
        ]
    },
    "Painter": {
        "icon": "fas fa-paint-roller",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "painting_types", "label": "Painting Types", "type": "select", "options": ["Interior", "Exterior", "Commercial", "Residential", "Industrial"], "required": True},
            {"name": "surface_types", "label": "Surface Types", "type": "text", "required": False},
            {"name": "tools", "label": "Tools Available", "type": "text", "required": False},
            {"name": "brands_expertise", "label": "Paint Brands Expertise", "type": "text", "required": False}
        ]
    },
    "Mason": {
        "icon": "fas fa-ruler-combined",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Brick", "Stone", "Concrete", "Tile", "All Types"], "required": True},
            {"name": "materials", "label": "Materials Worked With", "type": "text", "required": False},
            {"name": "tools", "label": "Tools Available", "type": "text", "required": False},
            {"name": "projects_completed", "label": "Projects Completed", "type": "number", "required": False}
        ]
    },
    "Gardener": {
        "icon": "fas fa-seedling",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Landscaping", "Lawn Care", "Tree Surgery", "Nursery", "General Gardening"], "required": True},
            {"name": "plant_types", "label": "Plant Types Expertise", "type": "text", "required": False},
            {"name": "tools", "label": "Gardening Tools", "type": "text", "required": False},
            {"name": "organic_methods", "label": "Organic Methods", "type": "select", "options": ["Yes", "No"], "required": False}
        ]
    },
    "Security Guard": {
        "icon": "fas fa-shield-alt",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "license_number", "label": "Security License Number", "type": "text", "required": True},
            {"name": "specialization", "label": "Specialization", "type": "select", "options": ["Corporate", "Residential", "Event", "Industrial", "Mall Security"], "required": True},
            {"name": "training_certifications", "label": "Training Certifications", "type": "text", "required": False},
            {"name": "shift_preference", "label": "Shift Preference", "type": "select", "options": ["Day", "Night", "Rotating", "Any"], "required": True}
        ]
    },
    "Cleaner": {
        "icon": "fas fa-broom",
        "fields": [
            {"name": "experience_years", "label": "Years of Experience", "type": "number", "required": True},
            {"name": "cleaning_types", "label": "Cleaning Types", "type": "select", "options": ["House", "Office", "Industrial", "Commercial", "Car"], "required": True},
            {"name": "equipment", "label": "Cleaning Equipment", "type": "text", "required": False},
            {"name": "chemicals_knowledge", "label": "Cleaning Chemicals Knowledge", "type": "select", "options": ["Basic", "Intermediate", "Expert"], "required": False},
            {"name": "areas_covered", "label": "Areas Covered", "type": "text", "required": False}
        ]
    }
}

# Initialize helpers
ai_helper = AIHelper()
job_recommender = JobRecommender()
auth_helper = Auth()

def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        auth_plugin='mysql_native_password',
    )

def save_user_to_db(user_data):
    """Save user data to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        created_at=user_data.get('created_at') or datetime.now()
        cursor.execute('''
            INSERT INTO users (mobile, full_name, email, gender, address, profession, 
                             verification_data, id_verified, id_data, language, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            mobile=VALUES(mobile),
            full_name = VALUES(full_name),
            email = VALUES(email),
            gender = VALUES(gender),
            address = VALUES(address),
            profession = VALUES(profession),
            verification_data = VALUES(verification_data),
            id_verified = VALUES(id_verified),
            id_data = VALUES(id_data),
            language=VALUES(language),
            updated_at = CURRENT_TIMESTAMP
               ''', (
            user_data.get('mobile'),
            user_data.get('full_name', ''),
            user_data.get('email', ''),
            user_data.get('gender', ''),              # safe access
            user_data.get('address', ''),
            user_data.get('profession', ''),
            json.dumps(user_data.get('verification_data', {})),
            1 if user_data.get('id_verified') else 0, # ensure int for DB
            json.dumps(user_data.get('id_data')) if user_data.get('id_data') else None,
            user_data.get('language', 'en'),
            created_at
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def get_user_from_db(mobile):
    """Get user data from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE mobile = %s', (mobile,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        print(f"Database error: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('language') )

@app.route('/language', methods=['GET', 'POST'])
def language():
    languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'hi', 'name': 'हिन्दी'},
        {'code': 'od', 'name': 'ଓଡ଼ିଆ'},
        {'code': 'ta', 'name': 'தமிழ்'},
        {'code': 'te', 'name': 'తెలుగు'},
        {'code': 'bn', 'name': 'বাংলা'}
    ]
    selected_language=session.get('language','en')
    if request.method == 'POST':
        lang=request.form.get('language')
        if lang:
           session['language']=lang

           return redirect(url_for('login'))

    return render_template('language.html', languages=languages, selected_language=selected_language)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        if mobile and len(mobile) == 10 and mobile.isdigit():
            session['mobile'] = mobile
            
            # Check if user exists for passkey login
            user = get_user_from_db(mobile)
            if user:
                return redirect(url_for('passkey_login'))
            else:
                # New user - send OTP
                session['otp'] = str(random.randint(100000, 999999))
                session['otp_created'] = datetime.now().isoformat()
                send_sms(mobile, f"Your OTP for BlueCollarResume is: {session['otp']}")
                return redirect(url_for('verify_otp'))
        else:
            flash('Please enter a valid 10-digit mobile number', 'error')
    
    return render_template('login.html')
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'mobile' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        stored_otp = session.get('otp')
        otp_created = session.get('otp_created')
        
        # Check OTP expiration (10 minutes)
        if otp_created:
            created_time = datetime.fromisoformat(otp_created)
            if datetime.now() - created_time > timedelta(minutes=10):
                flash('OTP has expired. Please request a new one.', 'error')
                return redirect(url_for('login'))
        
        if otp == stored_otp:
            session['authenticated'] = True
            session.pop('otp', None)
            session.pop('otp_created', None)
            return redirect(url_for('profession'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    
    return render_template('verify_otp.html')

            
        
       
@app.route('/passkey-login', methods=['GET', 'POST'])
def passkey_login():
    if 'mobile' not in session:
        return redirect(url_for('login'))
    
    user = get_user_from_db(session['mobile'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        passkey = request.form.get('passkey')
        remember_device = request.form.get('remember_device')
        
        # In a real app, verify passkey against stored hash
        if passkey:
            session['authenticated'] = True
            if remember_device:
                session['remember_me'] = True
                session.permanent = True
            return redirect(url_for('jobs'))
        else:
            flash('Invalid passkey. Please try again.', 'error')
    
    return render_template('passkey_login.html', mobile=session['mobile'])

@app.route('/profession', methods=['GET', 'POST'])
def profession():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        profession = request.form.get('profession')
        if profession:
            session['profession'] = profession
            return redirect(url_for('verification'))
    
    professions = []
    for prof_name, prof_config in PROFESSIONS_CONFIG.items():
        professions.append({
            'name': prof_name,
            'icon_class': prof_config['icon'],
            'description': f"Professional {prof_name.lower()} with verified skills"
        })
    
    return render_template('profession.html', professions=professions)

@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if not session.get('authenticated') or not session.get('profession'):
        return redirect(url_for('profession'))
    
    profession = session['profession']
    fields = PROFESSIONS_CONFIG.get(profession, {}).get('fields', [])
    
    if request.method == 'POST':
        verification_data = {}
        for field in fields:
            field_name = field['name']
            field_value = request.form.get(field_name)
            if field['required'] and not field_value:
                flash(f"Please fill in {field['label']}", 'error')
                return render_template('verification.html', profession=profession, fields=fields)
            verification_data[field_name] = field_value
        
        session['verification_data'] = verification_data
        return redirect(url_for('profile'))
    
    return render_template('verification.html', profession=profession, fields=fields)

@app.route('/profile', methods=['GET', 'POST'])
def profile():

    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        session['full_name'] = request.form.get('full_name')
        session['email'] = request.form.get('email')
        session['gender'] = request.form.get('gender')
        session['address'] = request.form.get('address')
        return redirect(url_for('id_verification'))
    
    return render_template('profile.html')

@app.route('/id-verification', methods=['GET', 'POST'])
def id_verification():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id_type = request.form.get('id_type')
        id_number = request.form.get('id_number')
        id_file = request.files.get('id_file')
        
        if id_file and id_type and id_number:
            filename = save_uploaded_file(id_file, session.get('mobile'), 'id_document')
            session['id_verified'] = True
            session['id_data'] = {
                'type': id_type,
                'number': id_number,
                'file': filename
            }

            # Prepare user data for saving
            user_data = {
                'mobile': session.get('mobile'),
                'full_name': session.get('full_name', ''),
                'email': session.get('email', ''),
                'gender ': session.get('gender', ''),
                'address': session.get('address', ''),
                'profession': session.get('profession', ''),
                'verification_data': session.get('verification_data'),
                'id_verified': session.get('id_verified', True),
                'id_data': session.get('id_data', {}),
                
                'created_at' :session.get('created_at', datetime.now().isoformat()),
                'language': session.get('language', 'en') ,
            }

            
            if save_user_to_db(user_data):
                return redirect(url_for('stay_signed_in'))
            else:
                flash('Error saving your data. Please try again.', 'error')
        else:
            flash('Please complete all ID verification fields', 'error')
    
    return render_template('id_verification.html')

@app.route('/stay-signed-in', methods=['GET', 'POST'])
def stay_signed_in():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        stay_signed = request.form.get('stay_signed')
        if stay_signed == 'yes':
            # Set up passkey for future logins
            session['passkey_setup'] = True
            flash('Passkey setup completed! You can use it for future logins.', 'success')
        return redirect(url_for('resume'))
    
    return render_template('stay_signed_in.html')

@app.route('/resume', methods=['GET', 'POST'])
def resume():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        template = request.form.get('template', 'modern')
        
        # Generate resume data
        resume_data = {
            'id': session.get('mobile'),
            'full_name': session.get('full_name', ''),
            'mobile': session.get('mobile', ''),
            'email': session.get('email', ''),
            'address': session.get('address', ''),
            'profession': session.get('profession', ''),
            'verification_data': session.get('verification_data', {}),
            'id_verified': session.get('id_verified', False)
        }
        
        # Generate PDF resume
        pdf_path = generate_resume_pdf(resume_data, template)
        session['resume_path'] = pdf_path
        
        return redirect(url_for('jobs'))
    
    templates = [
        {'id': 'modern', 'name': 'Modern Professional', 'description': 'Clean and contemporary design'},
        {'id': 'classic', 'name': 'Classic Traditional', 'description': 'Traditional formal layout'},
        {'id': 'compact', 'name': 'Compact One-Page', 'description': 'Single page optimized resume'},
        {'id': 'executive', 'name': 'Executive Style', 'description': 'Professional executive format'}
    ]
    
    return render_template('resume.html', templates=templates)

@app.route('/jobs')
def jobs():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    # Get AI-powered job recommendations
    profession = session.get('profession', 'Worker')
    user_data = {
        'profession': profession,
        'experience': session.get('verification_data', {}).get('experience_years', 0),
        'skills': session.get('verification_data', {}).get('skills', ''),
        'location': session.get('address', '')
    }
    
    jobs_data = job_recommender.get_recommendations(user_data)
    
    return render_template('jobs.html', jobs=jobs_data)

@app.route('/download-resume')
def download_resume():
    resume_path = session.get('resume_path')
    if resume_path and os.path.exists(resume_path):
        return send_file(resume_path, as_attachment=True)
    else:
        flash('Resume not found. Please generate your resume first.', 'error')
        return redirect(url_for('resume'))


@app.route('/voice-input', methods=['POST'])
def voice_input():
    try:
        data = request.get_json()
        field_name = data.get('field_name')
        text = data.get('text', '')
        profession = session.get('profession', '')
        
        # Enhanced text using AI
        enhanced_text = ai_helper.enhance_text(text, field_name, profession)
        
        return jsonify({
            'success': True,
            'enhanced_text': enhanced_text,
            'original_text': text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    try:
        audio_data = request.json.get('audio_data')
        if audio_data:
            text = transcribe_audio(audio_data)
            return jsonify({'success': True, 'text': text})
        return jsonify({'success': False, 'error': 'No audio data'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        
        translated_text = translator.translate_text(text, target_lang)
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'original_text': text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/track-job', methods=['POST'])
def track_job():
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        action = data.get('action')  # applied, saved, viewed
        
        # Store job tracking in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_tracking (user_mobile, job_id, action, created_at)
            VALUES (%s, %s, %s, %s)
        ''', (session.get('mobile'), job_id, action, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)