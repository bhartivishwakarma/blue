# utils/ai_helper.py
import json
import openai
from config import Config

# Configure OpenAI
openai.api_key = Config.OPENAI_API_KEY

def generate_profession_fields(profession):
    """Generate profession-specific verification fields using AI"""
    
    # Field templates for different professions
    field_templates = {
        'Electrician': [
            {'name': 'license_number', 'label': 'Electrician License Number', 'type': 'text', 'required': True},
            {'name': 'years_experience', 'label': 'Years of Experience', 'type': 'number', 'required': True},
            {'name': 'specializations', 'label': 'Specializations', 'type': 'text', 'required': False},
            {'name': 'certifications', 'label': 'Certifications', 'type': 'text', 'required': False},
            {'name': 'areas_covered', 'label': 'Areas/Regions Covered', 'type': 'text', 'required': False}
        ],
        'Plumber': [
            {'name': 'license_number', 'label': 'Plumbing License Number', 'type': 'text', 'required': True},
            {'name': 'years_experience', 'label': 'Years of Experience', 'type': 'number', 'required': True},
            {'name': 'pipe_types', 'label': 'Types of Pipes Worked With', 'type': 'text', 'required': False},
            {'name': 'certifications', 'label': 'Certifications', 'type': 'text', 'required': False},
            {'name': 'service_areas', 'label': 'Service Areas', 'type': 'text', 'required': False}
        ],
        'Driver': [
            {'name': 'license_number', 'label': 'Driver License Number', 'type': 'text', 'required': True},
            {'name': 'license_type', 'label': 'License Type', 'type': 'text', 'required': True},
            {'name': 'vehicle_types', 'label': 'Vehicle Types Licensed For', 'type': 'text', 'required': True},
            {'name': 'years_experience', 'label': 'Years of Driving Experience', 'type': 'number', 'required': True},
            {'name': 'areas_covered', 'label': 'Areas Covered', 'type': 'text', 'required': False}
        ],
        'Carpenter': [
            {'name': 'years_experience', 'label': 'Years of Experience', 'type': 'number', 'required': True},
            {'name': 'specializations', 'label': 'Specializations', 'type': 'text', 'required': False},
            {'name': 'tools_expertise', 'label': 'Tools Expertise', 'type': 'text', 'required': False},
            {'name': 'projects_completed', 'label': 'Notable Projects', 'type': 'text', 'required': False}
        ]
    }
    
    # Return specific template or generic one
    return field_templates.get(profession, [
        {'name': 'years_experience', 'label': 'Years of Experience', 'type': 'number', 'required': True},
        {'name': 'skills', 'label': 'Key Skills', 'type': 'text', 'required': True},
        {'name': 'certifications', 'label': 'Certifications', 'type': 'text', 'required': False},
        {'name': 'achievements', 'label': 'Notable Achievements', 'type': 'text', 'required': False}
    ])

def enhance_text(text, field_type, profession):
    """Enhance text using AI for better grammar and clarity"""
    
    if not Config.OPENAI_API_KEY:
        # Fallback without AI
        enhancements = {
            'skills': f"Skilled in {text} with professional expertise",
            'experience': f"Experienced professional with {text}",
            'achievements': f"Notable achievement: {text}",
            'voice_input': text.capitalize(),
            'default': text
        }
        return enhancements.get(field_type, enhancements['default'])
    
    try:
        prompt = f"""
        As a professional {profession}, enhance this text to make it more professional and clear for a resume:
        
        Original: "{text}"
        Field Type: {field_type}
        
        Return only the enhanced text without any explanations.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume writer helping blue-collar workers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"AI enhancement error: {e}")
        return text  # Return original text if AI fails

def get_job_recommendations(user_data):
    """Get AI-powered job recommendations based on user profile"""
    
    profession = user_data.get('profession', 'Worker')
    verification_data = json.loads(user_data.get('verification_data', '{}'))
    experience = verification_data.get('years_experience', '2')
    
    # Sample job data - in production, integrate with job APIs
    job_templates = {
        'Electrician': [
            {
                'title': f'Senior Electrician ({experience}+ years)',
                'company': 'PowerGrid Solutions Ltd.',
                'location': 'Mumbai, Maharashtra',
                'description': f'Looking for experienced electrician with {experience} years in commercial electrical systems. Must have valid license and safety certifications.',
                'salary': '₹25,000 - ₹40,000 per month',
                'match_score': 92,
                'source': 'Naukri.com',
                'apply_url': '#'
            },
            {
                'title': 'Electrical Maintenance Technician',
                'company': 'Metro Infrastructure Corp.',
                'location': 'Delhi, NCR',
                'description': 'Immediate opening for skilled electrical technician for building maintenance and repair work.',
                'salary': '₹22,000 - ₹35,000 per month',
                'match_score': 85,
                'source': 'Indeed',
                'apply_url': '#'
            }
        ],
        'Plumber': [
            {
                'title': f'Lead Plumber ({experience}+ years)',
                'company': 'AquaFlow Services',
                'location': 'Bangalore, Karnataka',
                'description': f'Experienced plumber needed for residential and commercial projects. {experience} years experience required.',
                'salary': '₹20,000 - ₹35,000 per month',
                'match_score': 88,
                'source': 'Naukri.com',
                'apply_url': '#'
            }
        ]
    }
    
    # Return profession-specific jobs or generic ones
    return job_templates.get(profession, [
        {
            'title': f'Skilled {profession}',
            'company': 'Various Employers',
            'location': 'Multiple Locations',
            'description': f'Opportunities for experienced {profession.lower()} with verified credentials.',
            'salary': '₹18,000 - ₹30,000 per month',
            'match_score': 75,
            'source': 'BlueCollar Jobs',
            'apply_url': '#'
        }
    ])

def get_chatbot_response(message, context, session_data):
    """Get AI response for chatbot queries"""
    
    if not Config.OPENAI_API_KEY:
        # Simple rule-based responses for demo
        responses = {
            'experience': "You can describe your work experience. For example: 'I have 5 years of experience in electrical wiring and maintenance for residential buildings.'",
            'skills': "List your key skills. For example: 'Electrical installation, wiring, troubleshooting, safety protocols, customer service.'",
            'help': "I'm here to help you build your resume. You can ask me about filling specific fields or describing your experience.",
            'default': "I understand you're working on your resume. Please provide more details about your question so I can assist you better."
        }
        return responses.get(context, responses['default'])
    
    try:
        user_context = f"""
        User is a {session_data.get('profession', 'professional')} creating a resume.
        Current context: {context}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant guiding blue-collar workers to create better resumes. Keep responses brief and practical."},
                {"role": "system", "content": user_context},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return "I'm here to help with your resume. Please try rephrasing your question."