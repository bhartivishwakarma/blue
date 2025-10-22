# utils/job_recommender.py
import google.generativeai as genai
import json
import random
from config import Config

class JobRecommender:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
        
        # Base job data for fallback
        self.base_jobs = {
            "Driver": [
                {
                    "title": "Commercial Driver",
                    "company": "Logistics Solutions Ltd",
                    "location": "Mumbai, Maharashtra",
                    "description": "Required experienced driver for commercial vehicle operations with valid license.",
                    "salary": "₹25,000 - ₹35,000/month",
                    "experience": "2+ years",
                    "skills": ["Valid Driving License", "Route Knowledge", "Vehicle Maintenance"],
                    "match_score": 95
                }
            ],
            "Electrician": [
                {
                    "title": "Industrial Electrician",
                    "company": "Power Tech Industries",
                    "location": "Pune, Maharashtra", 
                    "description": "Need certified electrician for industrial electrical work and maintenance.",
                    "salary": "₹22,000 - ₹32,000/month",
                    "experience": "3+ years",
                    "skills": ["Electrical Certification", "Wiring", "Troubleshooting"],
                    "match_score": 92
                }
            ]
        }

    def get_recommendations(self, user_data):
        """Get AI-powered job recommendations"""
        profession = user_data.get('profession', 'Worker')
        experience = user_data.get('experience', 0)
        skills = user_data.get('skills', '')
        location = user_data.get('location', '')
        
        # If no AI model, return base recommendations
        if not self.model:
            return self.get_base_recommendations(profession, experience)
        
        try:
            prompt = f"""
            Generate 5 realistic job recommendations for a {profession} in India with the following details:
            - Experience: {experience} years
            - Skills: {skills}
            - Preferred Location: {location}
            
            For each job, provide:
            1. Job title (relevant to {profession})
            2. Company name (realistic Indian company)
            3. Location (Indian city)
            4. Job description (2-3 lines)
            5. Salary range (realistic for Indian market in INR)
            6. Required experience
            7. Key skills required
            8. Match score (85-98)
            
            Return only a JSON array without any other text.
            Format: [{{"title": "", "company": "", "location": "", "description": "", "salary": "", "experience": "", "skills": [], "match_score": 0}}]
            """
            
            response = self.model.generate_content(prompt)
            jobs_text = response.text.strip()
            
            # Clean the response and parse JSON
            jobs_text = jobs_text.replace('```json', '').replace('```', '').strip()
            jobs = json.loads(jobs_text)
            
            # Add additional fields for frontend
            for job in jobs:
                job['source'] = 'AI Recommended'
                job['apply_url'] = '#'
                job['id'] = f"job_{random.randint(1000, 9999)}"
            
            return jobs
            
        except Exception as e:
            print(f"AI job recommendation error: {e}")
            return self.get_base_recommendations(profession, experience)
    
    def get_base_recommendations(self, profession, experience):
        """Get base job recommendations when AI fails"""
        base_jobs = self.base_jobs.get(profession, [])
        
        # Add some random jobs based on profession
        all_professions = [
            {
                "title": f"Senior {profession}",
                "company": "Premium Services Ltd.",
                "location": "Delhi, NCR",
                "description": f"Looking for experienced {profession.lower()} with verified credentials.",
                "salary": f"₹{20000 + int(experience)*1000} - ₹{30000 + int(experience)*1000}/month",
                "experience": f"{experience}+ years",
                "skills": ["Professional", "Verified", "Reliable"],
                "match_score": 90 - int(experience) + random.randint(0, 10),
                "source": "BlueCollar Jobs",
                "apply_url": "#",
                "id": f"job_{random.randint(1000, 9999)}"
            },
            {
                "title": f"Professional {profession}",
                "company": "Quality Work Solutions",
                "location": "Bangalore, Karnataka", 
                "description": f"Immediate opening for skilled {profession.lower()} with good experience.",
                "salary": f"₹{18000 + int(experience)*800} - ₹{28000 + int(experience)*800}/month",
                "experience": f"{max(1, int(experience)-1)}+ years",
                "skills": ["Skilled", "Experienced", "Professional"],
                "match_score": 85 - int(experience) + random.randint(0, 10),
                "source": "Job Portal",
                "apply_url": "#", 
                "id": f"job_{random.randint(1000, 9999)}"
            }
        ]
        
        return base_jobs + all_professions

    def get_jobs_by_location(self, profession, location):
        """Get jobs filtered by location"""
        all_jobs = self.get_base_recommendations(profession, 2)
        location_jobs = [job for job in all_jobs if location.lower() in job['location'].lower()]
        
        if not location_jobs:
            # If no location matches, return all jobs with location updated
            for job in all_jobs:
                job['location'] = location
            return all_jobs
        
        return location_jobs

    def enhance_job_descriptions(self, jobs, user_skills):
        """Enhance job descriptions based on user skills"""
        if not self.model:
            return jobs
        
        try:
            enhanced_jobs = []
            for job in jobs:
                prompt = f"""
                Enhance this job description to better highlight skills matching: {user_skills}
                
                Original: {job['description']}
                
                Keep it professional and make it more appealing for candidates with these skills.
                Return only the enhanced description.
                """
                
                response = self.model.generate_content(prompt)
                enhanced_desc = response.text.strip()
                
                job['description'] = enhanced_desc
                enhanced_jobs.append(job)
            
            return enhanced_jobs
            
        except Exception as e:
            print(f"Job description enhancement error: {e}")
            return jobs

    def calculate_match_score(self, job_requirements, user_profile):
        """Calculate match score between job and user profile"""
        score = 80  # Base score
        
        # Experience match
        job_exp = self._extract_experience(job_requirements.get('experience', ''))
        user_exp = user_profile.get('experience', 0)
        
        if user_exp >= job_exp:
            score += 10
        elif user_exp >= job_exp - 2:
            score += 5
        
        # Skills match (basic)
        job_skills = job_requirements.get('skills', [])
        user_skills = user_profile.get('skills', '').lower()
        
        skill_matches = sum(1 for skill in job_skills if skill.lower() in user_skills)
        if skill_matches > 0:
            score += min(skill_matches * 5, 10)
        
        return min(score, 98)  # Cap at 98%

    def _extract_experience(self, experience_text):
        """Extract years from experience text"""
        import re
        match = re.search(r'(\d+)\+?', str(experience_text))
        if match:
            return int(match.group(1))
        return 0

    def get_trending_skills(self, profession):
        """Get trending skills for a profession"""
        trending_skills = {
            "Driver": ["GPS Navigation", "Vehicle Maintenance", "Safety Protocols", "Route Planning"],
            "Electrician": ["Smart Home Systems", "Solar Installation", "Energy Efficiency", "Safety Standards"],
            "Plumber": ["Water Conservation", "Modern Fixtures", "Pipe Relining", "Emergency Repair"],
            "Mechanic": ["Hybrid Vehicles", "Computer Diagnostics", "Emission Systems", "Advanced Tools"]
        }
        
        return trending_skills.get(profession, ["Professional Skills", "Quality Work", "Reliability"])

    def generate_application_tips(self, job, user_profile):
        """Generate application tips for a specific job"""
        tips = [
            "Highlight your relevant experience in the cover letter",
            "Emphasize your verified professional status",
            "Mention specific skills that match the job requirements",
            "Provide examples of past successful projects"
        ]
        
        # Add profession-specific tips
        profession_tips = {
            "Driver": ["Mention your clean driving record", "Highlight route knowledge"],
            "Electrician": ["Discuss safety certifications", "Mention complex projects completed"],
            "Plumber": ["Talk about emergency response experience", "Highlight water-saving installations"]
        }
        
        additional_tips = profession_tips.get(user_profile.get('profession', ''), [])
        return tips + additional_tips