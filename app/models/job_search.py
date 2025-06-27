from app import db
from datetime import datetime

class JobSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    company_domain = db.Column(db.String(255))
    position = db.Column(db.String(255))
    hr_name = db.Column(db.String(255))
    hr_email = db.Column(db.String(255))
    hr_linkedin = db.Column(db.String(500))
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    email_template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    smtp_config_id = db.Column(db.Integer, db.ForeignKey('smtp_config.id'))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, contacted, responded, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email_template = db.relationship('EmailTemplate', backref='job_searches')
    smtp_config = db.relationship('SMTPConfig', backref='job_searches')
    
    def mark_email_sent(self):
        """Mark email as sent"""
        self.email_sent = True
        self.email_sent_at = datetime.utcnow()
        self.status = 'contacted'
    
    def get_status_color(self):
        """Get Bootstrap color class for status"""
        status_colors = {
            'pending': 'secondary',
            'contacted': 'primary',
            'responded': 'success',
            'rejected': 'danger'
        }
        return status_colors.get(self.status, 'secondary')
    
    def __repr__(self):
        return f'<JobSearch {self.company_name} - {self.position}>'
