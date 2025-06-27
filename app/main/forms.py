from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError
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
    company_name = StringField('Company Name', validators=[Optional()])
    company_domain = StringField('Company Domain', validators=[Optional()])
    hr_name = StringField('HR Name(s)', validators=[Optional()],
                         render_kw={"placeholder": "John Doe, Jane Smith (optional, comma-separated)"})
    hr_email = TextAreaField('Email Address(es)', validators=[
        DataRequired(),
        validate_multiple_emails
    ], render_kw={
        "placeholder": "recipient1@company.com, recipient2@company.com\n(Enter one or multiple emails, separated by commas or semicolons)",
        "rows": 3
    })
    position = StringField('Position', validators=[Optional()])
    custom_message = TextAreaField('Additional Message', validators=[Optional()])
    submit = SubmitField('Send Email')

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
