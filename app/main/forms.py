from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class EmailTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Template name must be between 3 and 100 characters')
    ])
    subject = StringField('Email Subject', validators=[
        DataRequired(),
        Length(min=5, max=255, message='Subject must be between 5 and 255 characters')
    ])
    body = TextAreaField('Email Body', validators=[
        DataRequired(),
        Length(min=10, message='Email body must be at least 10 characters')
    ])
    is_default = BooleanField('Set as Default Template')
    submit = SubmitField('Save Template')

class SMTPConfigForm(FlaskForm):
    name = StringField('Configuration Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    smtp_server = StringField('SMTP Server', validators=[
        DataRequired(),
        Length(min=5, max=255, message='SMTP server must be between 5 and 255 characters')
    ])
    smtp_port = IntegerField('SMTP Port', validators=[
        DataRequired(),
        NumberRange(min=1, max=65535, message='Port must be between 1 and 65535')
    ], default=587)
    use_tls = BooleanField('Use TLS', default=True)
    use_ssl = BooleanField('Use SSL', default=False)
    username = StringField('Username/Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=1, message='Password is required')
    ])
    from_email = StringField('From Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    from_name = StringField('From Name', validators=[
        Optional(),
        Length(max=255, message='From name must be less than 255 characters')
    ])
    is_active = BooleanField('Set as Active Configuration')
    submit = SubmitField('Save Configuration')

class JobSearchForm(FlaskForm):
    company_name = StringField('Company Name', validators=[
        DataRequired(),
        Length(min=2, max=255, message='Company name must be between 2 and 255 characters')
    ])
    position = StringField('Position/Role', validators=[
        Optional(),
        Length(max=255, message='Position must be less than 255 characters')
    ])
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=1000, message='Notes must be less than 1000 characters')
    ])
    submit = SubmitField('Search Company')

class SendEmailForm(FlaskForm):
    template_id = SelectField('Email Template', coerce=int, validators=[DataRequired()])
    smtp_config_id = SelectField('SMTP Configuration', coerce=int, validators=[DataRequired()])
    hr_name = StringField('HR Name', validators=[Optional()])
    hr_email = StringField('HR Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    position = StringField('Position', validators=[Optional()])
    custom_message = TextAreaField('Additional Message', validators=[Optional()])
    submit = SubmitField('Send Email')
