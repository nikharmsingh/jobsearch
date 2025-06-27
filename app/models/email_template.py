from app import db
from datetime import datetime

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Template variables that can be used
    AVAILABLE_VARIABLES = [
        'company_name',
        'hr_name',
        'hr_email',
        'position',
        'user_name',
        'user_email',
        'user_phone',
        'current_date',
        'company_domain'
    ]
    
    def get_rendered_subject(self, variables=None):
        """Render subject with provided variables"""
        if not variables:
            variables = {}
        
        subject = self.subject
        for var_name in self.AVAILABLE_VARIABLES:
            placeholder = f'{{{var_name}}}'
            if placeholder in subject and var_name in variables:
                subject = subject.replace(placeholder, str(variables[var_name]))
        
        return subject
    
    def get_rendered_body(self, variables=None):
        """Render body with provided variables"""
        if not variables:
            variables = {}
        
        body = self.body
        for var_name in self.AVAILABLE_VARIABLES:
            placeholder = f'{{{var_name}}}'
            if placeholder in body and var_name in variables:
                body = body.replace(placeholder, str(variables[var_name]))
        
        return body
    
    def get_used_variables(self):
        """Get list of variables used in this template"""
        used_vars = []
        content = self.subject + ' ' + self.body
        
        for var_name in self.AVAILABLE_VARIABLES:
            if f'{{{var_name}}}' in content:
                used_vars.append(var_name)
        
        return used_vars
    
    def __repr__(self):
        return f'<EmailTemplate {self.name} for user {self.user_id}>'
