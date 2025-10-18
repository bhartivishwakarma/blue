# utils/resume_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import json
from datetime import datetime
from config import Config

def generate_resume_pdf(user_data, template='modern'):
    """Generate a resume PDF based on user data and selected template"""
    
    # Create output directory if it doesn't exist
    output_dir = Config.UPLOAD_FOLDER
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = f"resume_{user_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Choose template
    if template == 'classic':
        doc = generate_classic_resume(user_data, filepath)
    elif template == 'compact':
        doc = generate_compact_resume(user_data, filepath)
    elif template == 'executive':
        doc = generate_executive_resume(user_data, filepath)
    else:  # modern
        doc = generate_modern_resume(user_data, filepath)
    
    return filepath

def generate_modern_resume(user_data, filepath):
    """Generate modern style resume"""
    doc = SimpleDocTemplate(filepath, pagesize=letter, 
                          topMargin=0.5*inch, bottomMargin=0.5*inch,
                          leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    
    # Custom styles for modern template
    styles.add(ParagraphStyle(
        name='TitleModern',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#007BFF'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeaderModern',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#007BFF'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    
    story = []
    
    # Header with blue accent
    header_table_data = [
        [Paragraph(user_data.get('full_name', 'Professional'), styles['TitleModern'])]
    ]
    header_table = Table(header_table_data, colWidths=[6*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#007BFF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROUNDEDCORNERS', [0, 0, 10, 10]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Contact Information
    contact_info = []
    if user_data.get('mobile'):
        contact_info.append(f"📱 {user_data['mobile']}")
    if user_data.get('email'):
        contact_info.append(f"✉️ {user_data['email']}")
    if user_data.get('address'):
        contact_info.append(f"📍 {user_data['address']}")
    
    if contact_info:
        contact_paragraph = Paragraph(" | ".join(contact_info), styles['Normal'])
        story.append(contact_paragraph)
        story.append(Spacer(1, 15))
    
    # Professional Summary
    verification_data = json.loads(user_data.get('verification_data', '{}'))
    if verification_data:
        story.append(Paragraph('Professional Summary', styles['SectionHeaderModern']))
        
        summary_parts = []
        if user_data.get('profession'):
            summary_parts.append(f"Experienced {user_data['profession'].lower()}")
        
        if 'years_experience' in verification_data:
            summary_parts.append(f"with {verification_data['years_experience']} years of experience")
        
        if 'specializations' in verification_data:
            summary_parts.append(f"specializing in {verification_data['specializations']}")
        elif 'skills' in verification_data:
            summary_parts.append(f"skilled in {verification_data['skills']}")
        
        summary = ". ".join(summary_parts) + "."
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Skills and Qualifications
    skills_data = []
    for key, value in verification_data.items():
        if key not in ['years_experience', 'license_number'] and value:
            skills_data.append([key.replace('_', ' ').title(), str(value)])
    
    if skills_data:
        story.append(Paragraph('Skills & Qualifications', styles['SectionHeaderModern']))
        
        skills_table = Table(skills_data, colWidths=[2*inch, 4*inch])
        skills_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(skills_table)
        story.append(Spacer(1, 15))
    
    # License and Certification
    if 'license_number' in verification_data:
        story.append(Paragraph('License & Certification', styles['SectionHeaderModern']))
        license_text = f"<b>License Number:</b> {verification_data['license_number']}"
        story.append(Paragraph(license_text, styles['Normal']))
    
    doc.build(story)
    return filepath

def generate_classic_resume(user_data, filepath):
    """Generate classic style resume"""
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Similar implementation for classic style
    # ... (implementation details)
    
    doc.build(story)
    return filepath

def generate_compact_resume(user_data, filepath):
    """Generate compact style resume"""
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Similar implementation for compact style
    # ... (implementation details)
    
    doc.build(story)
    return filepath

def generate_executive_resume(user_data, filepath):
    """Generate executive style resume"""
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Similar implementation for executive style
    # ... (implementation details)
    
    doc.build(story)
    return filepath