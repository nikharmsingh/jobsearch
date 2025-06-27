import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import logging

class EmailSender:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_templated_email(self, smtp_config, email_template, recipient_email, 
                           template_variables=None, recipient_name=None):
        """Send a templated email using the provided SMTP configuration"""
        
        if not template_variables:
            template_variables = {}
        
        # Add default variables
        template_variables.update({
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'user_name': f"{smtp_config.user.first_name} {smtp_config.user.last_name}",
            'user_email': smtp_config.from_email
        })
        
        # Add recipient info if provided
        if recipient_name:
            template_variables['hr_name'] = recipient_name
        template_variables['hr_email'] = recipient_email
        
        try:
            # Render template
            subject = email_template.get_rendered_subject(template_variables)
            body = email_template.get_rendered_body(template_variables)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{smtp_config.from_name} <{smtp_config.from_email}>" if smtp_config.from_name else smtp_config.from_email
            msg['To'] = recipient_email
            
            # Create HTML and plain text versions
            text_part = MIMEText(body, 'plain')
            html_body = self._convert_to_html(body)
            html_part = MIMEText(html_body, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            success, message = self._send_email(smtp_config, msg, recipient_email)
            
            if success:
                self.logger.info(f"Email sent successfully to {recipient_email}")
                return True, "Email sent successfully"
            else:
                self.logger.error(f"Failed to send email to {recipient_email}: {message}")
                return False, message
                
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _send_email(self, smtp_config, message, recipient_email):
        """Send email using SMTP configuration"""
        try:
            # Create SMTP connection
            if smtp_config.use_ssl:
                server = smtplib.SMTP_SSL(smtp_config.smtp_server, smtp_config.smtp_port)
            else:
                server = smtplib.SMTP(smtp_config.smtp_server, smtp_config.smtp_port)
                if smtp_config.use_tls:
                    server.starttls()
            
            # Login
            server.login(smtp_config.username, smtp_config.get_password())
            
            # Send email
            text = message.as_string()
            server.sendmail(smtp_config.from_email, recipient_email, text)
            server.quit()
            
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            return False, "SMTP Authentication failed. Please check your username and password."
        except smtplib.SMTPRecipientsRefused:
            return False, f"Recipient email address '{recipient_email}' was refused by the server."
        except smtplib.SMTPSenderRefused:
            return False, f"Sender email address '{smtp_config.from_email}' was refused by the server."
        except smtplib.SMTPDataError as e:
            return False, f"SMTP Data Error: {str(e)}"
        except smtplib.SMTPConnectError:
            return False, f"Could not connect to SMTP server '{smtp_config.smtp_server}:{smtp_config.smtp_port}'"
        except smtplib.SMTPServerDisconnected:
            return False, "SMTP server disconnected unexpectedly."
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def test_smtp_connection(self, smtp_config):
        """Test SMTP connection without sending an email"""
        try:
            if smtp_config.use_ssl:
                server = smtplib.SMTP_SSL(smtp_config.smtp_server, smtp_config.smtp_port)
            else:
                server = smtplib.SMTP(smtp_config.smtp_server, smtp_config.smtp_port)
                if smtp_config.use_tls:
                    server.starttls()
            
            server.login(smtp_config.username, smtp_config.get_password())
            server.quit()
            
            return True, "SMTP connection successful"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Please check your username and password."
        except smtplib.SMTPConnectError:
            return False, f"Could not connect to SMTP server '{smtp_config.smtp_server}:{smtp_config.smtp_port}'"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def send_test_email(self, smtp_config, test_recipient=None):
        """Send a test email to verify configuration"""
        if not test_recipient:
            test_recipient = smtp_config.from_email
        
        try:
            # Create test message
            msg = MIMEMultipart()
            msg['Subject'] = "JobSearch App - SMTP Configuration Test"
            msg['From'] = f"{smtp_config.from_name} <{smtp_config.from_email}>" if smtp_config.from_name else smtp_config.from_email
            msg['To'] = test_recipient
            
            body = f"""
This is a test email from your JobSearch application.

SMTP Configuration: {smtp_config.name}
Server: {smtp_config.smtp_server}:{smtp_config.smtp_port}
TLS: {'Enabled' if smtp_config.use_tls else 'Disabled'}
SSL: {'Enabled' if smtp_config.use_ssl else 'Disabled'}

If you received this email, your SMTP configuration is working correctly!

Best regards,
JobSearch App
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send test email
            success, message = self._send_email(smtp_config, msg, test_recipient)
            
            if success:
                return True, f"Test email sent successfully to {test_recipient}"
            else:
                return False, message
                
        except Exception as e:
            return False, f"Error sending test email: {str(e)}"
    
    def _convert_to_html(self, text):
        """Convert plain text to basic HTML"""
        # Simple conversion - replace line breaks with <br> tags
        html = text.replace('\n', '<br>\n')
        
        # Wrap in basic HTML structure
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .email-content {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
    </style>
</head>
<body>
    <div class="email-content">
        {html}
    </div>
</body>
</html>
        """.strip()
        
        return html_template
