from app import db
from datetime import datetime
from cryptography.fernet import Fernet
import os

class SMTPConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # User-friendly name
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False, default=587)
    use_tls = db.Column(db.Boolean, default=True)
    use_ssl = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(255), nullable=False)
    password_encrypted = db.Column(db.Text, nullable=False)
    from_email = db.Column(db.String(255), nullable=False)
    from_name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(SMTPConfig, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """Encrypt and store password"""
        key = self._get_encryption_key()
        f = Fernet(key)
        self.password_encrypted = f.encrypt(password.encode()).decode()
    
    def get_password(self):
        """Decrypt and return password"""
        key = self._get_encryption_key()
        f = Fernet(key)
        return f.decrypt(self.password_encrypted.encode()).decode()
    
    def _get_encryption_key(self):
        """Get or generate encryption key"""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # In production, store this securely
            os.environ['ENCRYPTION_KEY'] = key.decode()
        return key if isinstance(key, bytes) else key.encode()
    
    def test_connection(self):
        """Test SMTP connection"""
        import smtplib
        from email.mime.text import MIMEText
        
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            server.login(self.username, self.get_password())
            server.quit()
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def __repr__(self):
        return f'<SMTPConfig {self.name} for user {self.user_id}>'
