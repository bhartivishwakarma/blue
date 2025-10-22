# utils/ai_helper.py
import google.generativeai as genai
import json
import re
from config import Config

class AIHelper:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def enhance_text(self, text, field_name, profession):
        """Enhance user input text using AI for better professionalism"""
        if not self.model or not text.strip():
            return text

        try:
            prompt = f"""
            Enhance the following text for a {profession}'s resume. Make it more professional, clear, and impactful for employers.
            
            Field: {field_name}
            Original text: "{text}"
            
            Requirements:
            - Keep it concise and professional
            - Use industry-appropriate terminology
            - Highlight skills and achievements
            - Make it employer-friendly
            - Keep the meaning unchanged
            - Return only the enhanced text, no explanations
            
            Enhanced text:
            """
            
            response = self.model.generate_content(prompt)
            enhanced_text = response.text.strip()
            
            # Clean the response
            enhanced_text = re.sub(r'^"|"$', '', enhanced_text)
            return enhanced_text
            
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return text

    def generate_professional_summary(self, user_data, verification_data):
        """Generate professional summary using AI"""
        if not self.model:
            return self._generate_default_summary(user_data, verification_data)

        try:
            prompt = f"""
            Create a professional summary for a {user_data.get('profession', 'professional')} with the following details:
            - Experience: {verification_data.get('experience_years', 0)} years
            - Specialization: {verification_data.get('specialization', 'general')}
            - Skills: {verification_data.get('skills', 'various')}
            - Tools: {verification_data.get('tools', 'standard equipment')}
            
            Requirements:
            - Keep it 2-3 sentences
            - Professional and confident tone
            - Highlight key strengths
            - Suitable for resume/CV
            - Return only the summary text
            
            Professional Summary:
            """
            
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            # Clean the response
            summary = re.sub(r'^"|"$', '', summary)
            return summary
            
        except Exception as e:
            print(f"AI summary generation error: {e}")
            return self._generate_default_summary(user_data, verification_data)

    def _generate_default_summary(self, user_data, verification_data):
        """Generate default professional summary"""
        profession = user_data.get('profession', 'Professional')
        experience = verification_data.get('experience_years', 0)
        specialization = verification_data.get('specialization', '')
        
        summary = f"Experienced {profession.lower()} with {experience} years in the field. "
        
        if specialization:
            summary += f"Specializing in {specialization.lower()}. "
        
        summary += "Verified professional with proven track record of reliability and quality workmanship."
        
        return summary

    def generate_resume_sections(self, user_data, verification_data):
        """Generate enhanced resume sections using AI"""
        if not self.model:
            return self._generate_default_sections(user_data, verification_data)

        try:
            prompt = f"""
            Create enhanced resume sections for a {user_data.get('profession', 'professional')} based on:
            - Experience: {verification_data.get('experience_years', 0)} years
            - Skills: {verification_data.get('skills', '')}
            - Tools: {verification_data.get('tools', '')}
            - Certifications: {verification_data.get('certifications', '')}
            - Specialization: {verification_data.get('specialization', '')}
            
            Return a JSON with sections for:
            - professional_summary
            - key_skills
            - work_experience
            - certifications
            
            Format: {{"professional_summary": "", "key_skills": [], "work_experience": "", "certifications": []}}
            """
            
            response = self.model.generate_content(prompt)
            sections_text = response.text.strip()
            
            # Clean and parse JSON
            sections_text = sections_text.replace('```json', '').replace('```', '').strip()
            sections = json.loads(sections_text)
            
            return sections
            
        except Exception as e:
            print(f"AI sections generation error: {e}")
            return self._generate_default_sections(user_data, verification_data)

    def _generate_default_sections(self, user_data, verification_data):
        """Generate default resume sections"""
        profession = user_data.get('profession', 'Professional')
        experience = verification_data.get('experience_years', 0)
        
        return {
            "professional_summary": f"Reliable and skilled {profession.lower()} with {experience} years of hands-on experience. Committed to delivering quality work and maintaining professional standards.",
            "key_skills": ["Professional Work Ethic", "Quality Assurance", "Time Management", "Safety Compliance"],
            "work_experience": f"Provided professional {profession.lower()} services with focus on quality and customer satisfaction.",
            "certifications": ["Professional Verification", "Identity Verification"]
        }

    def enhance_job_description(self, job_data, user_profile):
        """Enhance job description based on user profile"""
        if not self.model:
            return job_data

        try:
            prompt = f"""
            Enhance this job description to better match a {user_profile.get('profession', 'professional')} with {user_profile.get('experience', 0)} years experience.
            
            Original job: {job_data.get('title', '')} at {job_data.get('company', '')}
            Description: {job_data.get('description', '')}
            
            Make it more appealing and relevant while keeping the core information.
            Return only the enhanced description.
            """
            
            response = self.model.generate_content(prompt)
            enhanced_desc = response.text.strip()
            
            job_data['description'] = enhanced_desc
            return job_data
            
        except Exception as e:
            print(f"AI job enhancement error: {e}")
            return job_data

    def generate_cover_letter(self, user_data, job_data):
        """Generate AI-powered cover letter"""
        if not self.model:
            return self._generate_default_cover_letter(user_data, job_data)

        try:
            prompt = f"""
            Write a professional cover letter for a {user_data.get('profession', 'professional')} applying for:
            Position: {job_data.get('title', '')}
            Company: {job_data.get('company', '')}
            
            Applicant details:
            - Experience: {user_data.get('verification_data', {}).get('experience_years', 0)} years
            - Skills: {user_data.get('verification_data', {}).get('skills', '')}
            - Specialization: {user_data.get('verification_data', {}).get('specialization', '')}
            
            Requirements:
            - Professional tone
            - 1 paragraph
            - Highlight relevant experience
            - Express enthusiasm for the role
            """
            
            response = self.model.generate_content(prompt)
            cover_letter = response.text.strip()
            
            return cover_letter
            
        except Exception as e:
            print(f"AI cover letter error: {e}")
            return self._generate_default_cover_letter(user_data, job_data)

    def _generate_default_cover_letter(self, user_data, job_data):
        """Generate default cover letter"""
        profession = user_data.get('profession', 'Professional')
        experience = user_data.get('verification_data', {}).get('experience_years', 0)
        
        return f"I am writing to express my interest in the {job_data.get('title', 'position')} at {job_data.get('company', 'your company')}. With {experience} years of experience as a {profession.lower()}, I have developed strong skills and a proven track record of delivering quality work. I am confident that my experience and professional approach would make me a valuable addition to your team."