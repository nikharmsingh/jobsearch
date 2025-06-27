from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    smtp_configs = db.relationship('SMTPConfig', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    email_templates = db.relationship('EmailTemplate', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    job_searches = db.relationship('JobSearch', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_active_smtp_config(self):
        """Get the active SMTP configuration for this user"""
        return self.smtp_configs.filter_by(is_active=True).first()
    
    def get_default_template(self):
        """Get the default email template for this user"""
        return self.email_templates.filter_by(is_default=True).first()
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        # Handle invalid user_id (e.g., MongoDB ObjectId strings, None, etc.)
        return None
