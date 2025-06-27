from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from app.models import User, EmailTemplate, SMTPConfig
import re


def validate_multiple_emails(form, field):
    """Custom validator for multiple email addresses (comma or semicolon separated)"""
    if not field.data:
        return

    # Split by comma or semicolon and clean up
    email_list = re.split(r'[,;]', field.data)
    email_list = [email.strip() for email in email_list if email.strip()]

    if not email_list:
        raise ValidationError('Please enter at least one email address.')

    # Validate each email
    email_validator = Email()
    invalid_emails = []

    for email in email_list:
        try:
            # Create a mock field for validation
            class MockField:
                def __init__(self, data):
                    self.data = data

                def gettext(self, string):
                    return string

            mock_field = MockField(email)
            email_validator(form, mock_field)
        except ValidationError:
            invalid_emails.append(email)

    if invalid_emails:
        if len(invalid_emails) == 1:
            raise ValidationError(f'Invalid email address: {invalid_emails[0]}')
        else:
            raise ValidationError(f'Invalid email addresses: {", ".join(invalid_emails)}')


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
    hr_email = TextAreaField('Email Address(es)', validators=[
        DataRequired(),
        validate_multiple_emails
    ], render_kw={
        "placeholder": "recipient1@company.com, recipient2@company.com\n(Enter one or multiple emails, separated by commas or semicolons)",
        "rows": 3
    })
    hr_name = StringField('HR Name(s)', validators=[Optional(), Length(max=500)],
                         render_kw={"placeholder": "John Doe, Jane Smith (optional, comma-separated)"})
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

    def get_email_list(self):
        """Parse and return list of email addresses"""
        if not self.hr_email.data:
            return []

        # Split by comma or semicolon and clean up
        email_list = re.split(r'[,;]', self.hr_email.data)
        return [email.strip() for email in email_list if email.strip()]

    def get_name_list(self):
        """Parse and return list of names (if provided)"""
        if not self.hr_name.data:
            return []

        # Split by comma and clean up
        name_list = [name.strip() for name in self.hr_name.data.split(',') if name.strip()]
        return name_list
