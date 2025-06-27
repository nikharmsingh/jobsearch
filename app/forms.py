from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from app.models import User, EmailTemplate, SMTPConfig

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CompanySearchForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=200)])
    position = StringField('Position', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Search Company')

class EmailTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(min=2, max=100)])
    subject = StringField('Email Subject', validators=[DataRequired(), Length(min=5, max=200)])
    body = TextAreaField('Email Body', validators=[DataRequired(), Length(min=10, max=5000)])
    is_default = BooleanField('Set as Default Template')
    submit = SubmitField('Save Template')

class SMTPConfigForm(FlaskForm):
    name = StringField('Configuration Name', validators=[DataRequired(), Length(min=2, max=100)])
    smtp_server = StringField('SMTP Server', validators=[DataRequired(), Length(min=5, max=255)])
    smtp_port = IntegerField('SMTP Port', validators=[DataRequired(), NumberRange(min=1, max=65535)], default=587)
    use_tls = BooleanField('Use TLS', default=True)
    use_ssl = BooleanField('Use SSL', default=False)
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=255)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1, max=255)])
    from_email = StringField('From Email', validators=[DataRequired(), Email()])
    from_name = StringField('From Name', validators=[Optional(), Length(max=255)])
    is_active = BooleanField('Set as Active Configuration')
    submit = SubmitField('Save Configuration')

class SendEmailForm(FlaskForm):
    template_id = SelectField('Email Template', coerce=int, validators=[DataRequired()])
    smtp_config_id = SelectField('SMTP Configuration', coerce=int, validators=[DataRequired()])
    hr_email = StringField('HR Email', validators=[DataRequired(), Email()])
    hr_name = StringField('HR Name', validators=[Optional(), Length(max=200)])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=200)])
    company_domain = StringField('Company Domain', validators=[Optional(), Length(max=200)])
    position = StringField('Position', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Send Email')

    def __init__(self, user_id, *args, **kwargs):
        super(SendEmailForm, self).__init__(*args, **kwargs)
        
        # Populate template choices
        templates = EmailTemplate.query.filter_by(user_id=user_id).all()
        self.template_id.choices = [(t.id, t.name) for t in templates]
        
        # Populate SMTP config choices
        smtp_configs = SMTPConfig.query.filter_by(user_id=user_id).all()
        self.smtp_config_id.choices = [(s.id, s.name) for s in smtp_configs]
