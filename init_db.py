#!/usr/bin/env python3
"""
Database initialization script for JobSearch application
"""

from app import db
from app.models import User, SMTPConfig, EmailTemplate, JobSearch

# Import create_app from the main app.py file
import importlib.util
import os
spec = importlib.util.spec_from_file_location("app_main", os.path.join(os.path.dirname(__file__), "app.py"))
app_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_main)
create_app = app_main.create_app

def init_database():
    """Initialize the database with tables"""
    # Ensure instance directory exists
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a sample email template for new users
        sample_template = EmailTemplate(
            user_id=1,  # Will be updated when first user registers
            name="Professional Job Application",
            subject="Application for {position} Position at {company_name}",
            body="""Dear {hr_name},

I hope this email finds you well. I am writing to express my strong interest in the {position} position at {company_name}.

With my background and skills, I believe I would be a valuable addition to your team. I am particularly drawn to {company_name} because of your reputation for innovation and excellence in the industry.

I have attached my resume for your review and would welcome the opportunity to discuss how my experience and enthusiasm can contribute to your team's success.

Thank you for considering my application. I look forward to hearing from you soon.

Best regards,
{user_name}
{user_email}""",
            is_default=True
        )
        
        print("Sample data would be created when first user registers.")
        print("Database initialization completed!")

if __name__ == '__main__':
    init_database()
