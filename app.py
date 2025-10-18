# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
import mysql.connector
import json
import os
from datetime import datetime, timedelta
from config import Config
from utils.auth import generate_otp, verify_otp, setup_passkey, verify_passkey, hash_password
from utils.ai_helper import generate_profession_fields, enhance_text, get_job_recommendations, get_chatbot_response
from utils.resume_generator import generate_resume_pdf
from utils.speech_recognition import transcribe_audio
from services.sms_service import send_sms
from services.file_upload import save_uploaded_file, allowed_file
import secrets

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'super-secret-key-2025')


# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE'],
        auth_plugin='mysql_native_password'
    )

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('language_selection'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            flash('Please enter a valid 10-digit mobile number', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
        user = cursor.fetchone()
        
        if user and user.get('has_passkey'):
            session['mobile_for_passkey'] = mobile
            return redirect(url_for('passkey_login'))
        
        # Generate and send OTP
        otp = generate_otp()
        session['otp'] = otp
        session['mobile'] = mobile
        session['otp_created_at'] = datetime.now().isoformat()
        
        # Send SMS (in production)
        try:
            send_sms(mobile, f"Your BlueCollarResume OTP is: {otp}. Valid for 10 minutes.")
            flash('OTP sent to your mobile number', 'success')
        except Exception as e:
            # For development, show OTP on screen
            flash(f'OTP (for demo): {otp}', 'info')
        
        return redirect(url_for('verify_otp'))
    
    return render_template('login.html')

@app.route('/passkey-login', methods=['GET', 'POST'])
def passkey_login():
    mobile = session.get('mobile_for_passkey')
    if not mobile:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        passkey_input = request.form.get('passkey')
        remember_device = request.form.get('remember_device') == 'on'
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
        user = cursor.fetchone()
        
        if user and verify_passkey(user['id'], passkey_input):
            session['user_id'] = user['id']
            session.pop('mobile_for_passkey', None)
            
            if remember_device:
                device_token = secrets.token_urlsafe(32)
                session['device_token'] = device_token
                # Store device token in database (simplified)
            
            flash('Login successful!', 'success')
            return redirect(url_for('language_selection'))
        else:
            flash('Invalid passkey. Please try again or use OTP login.', 'error')
    
    return render_template('passkey_login.html', mobile=mobile)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        # Check OTP expiration (10 minutes)
        otp_created_at = datetime.fromisoformat(session.get('otp_created_at'))
        if datetime.now() - otp_created_at > timedelta(minutes=10):
            flash('OTP has expired. Please request a new one.', 'error')
            return redirect(url_for('login'))
        
        if verify_otp(entered_otp, session.get('otp')):
            mobile = session.get('mobile')
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
            user = cursor.fetchone()
            
            if not user:
                # Create new user
                cursor.execute(
                    "INSERT INTO users (mobile, created_at) VALUES (%s, %s)",
                    (mobile, datetime.now())
                )
                user_id = cursor.lastrowid
                conn.commit()
            else:
                user_id = user['id']
            
            session['user_id'] = user_id
            session.pop('otp', None)
            session.pop('mobile', None)
            session.pop('otp_created_at', None)
            
            flash('Login successful!', 'success')
            return redirect(url_for('stay_signed_in'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    
    return render_template('verify_otp.html')

@app.route('/stay-signed-in', methods=['GET', 'POST'])
def stay_signed_in():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        stay_signed = request.form.get('stay_signed') == 'yes'
        if stay_signed:
            setup_passkey(session['user_id'])
            flash('Passkey setup completed! You can use it for future logins.', 'success')
        
        return redirect(url_for('language_selection'))
    
    return render_template('stay_signed_in.html')

@app.route('/language-selection', methods=['GET', 'POST'])
def language_selection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        language = request.form.get('language')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET language = %s WHERE id = %s",
            (language, session['user_id'])
        )
        conn.commit()
        
        session['language'] = language
        flash('Language preference saved!', 'success')
        return redirect(url_for('profession_selection'))
    
    languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'hi', 'name': 'Hindi'},
        {'code': 'ta', 'name': 'Tamil'},
        {'code': 'te', 'name': 'Telugu'},
        {'code': 'bn', 'name': 'Bengali'},
        {'code': 'mr', 'name': 'Marathi'}
    ]
    
    return render_template('language.html', languages=languages)

@app.route('/profession-selection', methods=['GET', 'POST'])
def profession_selection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM professions ORDER BY name")
    professions = cursor.fetchall()
    
    if request.method == 'POST':
        profession = request.form.get('profession')
        
        if profession:
            cursor.execute(
                "UPDATE users SET profession = %s WHERE id = %s",
                (profession, session['user_id'])
            )
            conn.commit()
            
            session['profession'] = profession
            flash(f'Profession set to: {profession}', 'success')
            return redirect(url_for('profile_setup'))
        else:
            flash('Please select a profession', 'error')
    
    return render_template('profession.html', professions=professions)

@app.route('/profile-setup', methods=['GET', 'POST'])
def profile_setup():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        email = request.form.get('email')
        gender = request.form.get('gender')
        
        cursor.execute(
            """UPDATE users SET full_name = %s, address = %s, email = %s, gender = %s 
               WHERE id = %s""",
            (full_name, address, email, gender, session['user_id'])
        )
        conn.commit()
        
        flash('Profile information saved!', 'success')
        return redirect(url_for('id_verification'))
    
    return render_template('profile.html', user=user)

@app.route('/id-verification', methods=['GET', 'POST'])
def id_verification():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        id_type = request.form.get('id_type')
        id_number = request.form.get('id_number')
        
        # Handle file upload
        if 'id_file' not in request.files:
            flash('Please upload an ID document', 'error')
            return render_template('id_verification.html')
        
        file = request.files['id_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return render_template('id_verification.html')
        
        if file and allowed_file(file.filename):
            filename = save_uploaded_file(file, session['user_id'], 'id_documents')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE users SET id_type = %s, id_number = %s, id_file_path = %s, id_verified = %s 
                   WHERE id = %s""",
                (id_type, id_number, filename, True, session['user_id'])
            )
            conn.commit()
            
            flash('ID verification submitted successfully!', 'success')
            return redirect(url_for('profession_verification'))
        else:
            flash('Invalid file type. Please upload PNG, JPG, or PDF files.', 'error')
    
    return render_template('id_verification.html')

@app.route('/profession-verification', methods=['GET', 'POST'])
def profession_verification():
    if 'user_id' not in session or 'profession' not in session:
        return redirect(url_for('profession_selection'))
    
    profession = session['profession']
    
    if request.method == 'GET':
        fields = generate_profession_fields(profession)
        session['profession_fields'] = fields
    else:
        fields = session.get('profession_fields', [])
        verification_data = {}
        
        for field in fields:
            field_name = field['name']
            field_value = request.form.get(field_name)
            voice_input = request.form.get(f'{field_name}_voice')
            
            # Use voice input if available, otherwise text input
            final_value = voice_input if voice_input else field_value
            
            # Enhance text using AI
            if final_value:
                enhanced_value = enhance_text(final_value, field['type'], profession)
                verification_data[field_name] = enhanced_value
        
        # Save verification data to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET verification_data = %s WHERE id = %s",
            (json.dumps(verification_data), session['user_id'])
        )
        conn.commit()
        
        flash('Professional information saved!', 'success')
        return redirect(url_for('resume_generation'))
    
    return render_template('verification.html', fields=fields, profession=profession)

@app.route('/resume-generation', methods=['GET', 'POST'])
def resume_generation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if request.method == 'POST':
        template = request.form.get('template', 'modern')
        
        # Generate resume
        resume_file = generate_resume_pdf(user, template)
        
        # Save resume record
        cursor.execute(
            "INSERT INTO resumes (user_id, template, file_path) VALUES (%s, %s, %s)",
            (session['user_id'], template, resume_file)
        )
        conn.commit()
        
        session['resume_file'] = resume_file
        flash('Resume generated successfully!', 'success')
        return redirect(url_for('job_recommendations'))
    
    templates = [
        {'id': 'modern', 'name': 'Modern Professional', 'description': 'Clean and contemporary design'},
        {'id': 'classic', 'name': 'Classic', 'description': 'Traditional professional layout'},
        {'id': 'compact', 'name': 'Compact', 'description': 'Space-efficient single page'},
        {'id': 'executive', 'name': 'Executive', 'description': 'Premium detailed format'}
    ]
    
    return render_template('resume.html', templates=templates, user=user)

@app.route('/job-recommendations')
def job_recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    # Get AI-powered job recommendations
    jobs = get_job_recommendations(user)
    
    # Save recommendations to database
    for job in jobs:
        cursor.execute(
            """INSERT INTO job_recommendations 
               (user_id, job_title, company, location, description, salary_range, match_score, source, apply_url)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (session['user_id'], job['title'], job['company'], job['location'], 
             job['description'], job['salary'], job['match_score'], job['source'], job.get('apply_url', '#'))
        )
    conn.commit()
    
    return render_template('jobs.html', jobs=jobs, resume_file=session.get('resume_file'))

@app.route('/download-resume')
def download_resume():
    resume_file = session.get('resume_file')
    if resume_file and os.path.exists(resume_file):
        return send_file(resume_file, as_attachment=True, download_name='My_Professional_Resume.pdf')
    flash('Resume not found. Please generate a new one.', 'error')
    return redirect(url_for('resume_generation'))

@app.route('/voice-input', methods=['POST'])
def voice_input():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        field_name = data.get('field_name')
        audio_data = data.get('audio_data')  # Base64 encoded audio
        
        # Transcribe audio
        transcribed_text = transcribe_audio(audio_data)
        
        # Enhance text
        profession = session.get('profession', 'general')
        enhanced_text = enhance_text(transcribed_text, 'voice_input', profession)
        
        return jsonify({
            'success': True,
            'original_text': transcribed_text,
            'enhanced_text': enhanced_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        message = data.get('message')
        context = data.get('context', 'general')
        
        # Get AI response
        response = get_chatbot_response(message, context, session)
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Initialize database on first run
    from database.init_db import init_database
    init_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)