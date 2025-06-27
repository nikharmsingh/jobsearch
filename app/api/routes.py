from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import bp
from app.services import CompanyDomainFinder, EmailFinder, EmailSender, SerpHRFinder
from app.models import SMTPConfig, EmailTemplate
from app import db

@bp.route('/find-company-domain', methods=['POST'])
@login_required
def find_company_domain():
    """API endpoint to find company domain"""
    data = request.get_json()
    company_name = data.get('company_name')
    
    if not company_name:
        return jsonify({'error': 'Company name is required'}), 400
    
    try:
        finder = CompanyDomainFinder()
        domain = finder.find_domain(company_name)
        
        if domain:
            return jsonify({
                'success': True,
                'domain': domain,
                'company_name': company_name
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not find domain for this company'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/find-hr-emails', methods=['POST'])
@login_required
def find_hr_emails():
    """API endpoint to find HR emails"""
    data = request.get_json()
    company_name = data.get('company_name')
    company_domain = data.get('company_domain')
    
    if not company_name:
        return jsonify({'error': 'Company name is required'}), 400
    
    try:
        finder = EmailFinder()
        emails = finder.find_hr_emails(company_name, company_domain)
        
        return jsonify({
            'success': True,
            'emails': emails,
            'count': len(emails)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/find-hr-emails-serp', methods=['POST'])
@login_required
def find_hr_emails_serp():
    """API endpoint to find HR emails using SERP API (India-focused)"""
    data = request.get_json()
    company_name = data.get('company_name')
    company_domain = data.get('company_domain')

    if not company_name:
        return jsonify({'error': 'Company name is required'}), 400

    try:
        serp_finder = SerpHRFinder()
        emails = serp_finder.find_hr_professionals(company_name, company_domain)

        return jsonify({
            'success': True,
            'emails': emails,
            'count': len(emails),
            'source': 'SERP API',
            'focus': 'India-based HR professionals',
            'api_info': {
                'service': 'SerpApi',
                'search_engine': 'Google',
                'geo_location': 'India',
                'specialization': 'HR professionals search'
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/test-smtp', methods=['POST'])
@login_required
def test_smtp():
    """API endpoint to test SMTP configuration"""
    data = request.get_json()
    config_id = data.get('config_id')
    
    if not config_id:
        return jsonify({'error': 'SMTP configuration ID is required'}), 400
    
    smtp_config = SMTPConfig.query.filter_by(
        id=config_id, 
        user_id=current_user.id
    ).first()
    
    if not smtp_config:
        return jsonify({'error': 'SMTP configuration not found'}), 404
    
    try:
        sender = EmailSender()
        success, message = sender.test_smtp_connection(smtp_config)
        
        if success:
            # Update verification status
            smtp_config.is_verified = True
            db.session.commit()
        
        return jsonify({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/send-test-email', methods=['POST'])
@login_required
def send_test_email():
    """API endpoint to send test email"""
    data = request.get_json()
    config_id = data.get('config_id')
    test_recipient = data.get('test_recipient')
    
    if not config_id:
        return jsonify({'error': 'SMTP configuration ID is required'}), 400
    
    smtp_config = SMTPConfig.query.filter_by(
        id=config_id, 
        user_id=current_user.id
    ).first()
    
    if not smtp_config:
        return jsonify({'error': 'SMTP configuration not found'}), 404
    
    try:
        sender = EmailSender()
        success, message = sender.send_test_email(smtp_config, test_recipient)
        
        return jsonify({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/send-job-email', methods=['POST'])
@login_required
def send_job_email():
    """API endpoint to send job application email"""
    data = request.get_json()
    
    required_fields = ['template_id', 'smtp_config_id', 'hr_email']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Get template and SMTP config
    template = EmailTemplate.query.filter_by(
        id=data['template_id'],
        user_id=current_user.id
    ).first()
    
    smtp_config = SMTPConfig.query.filter_by(
        id=data['smtp_config_id'],
        user_id=current_user.id
    ).first()
    
    if not template:
        return jsonify({'error': 'Email template not found'}), 404
    
    if not smtp_config:
        return jsonify({'error': 'SMTP configuration not found'}), 404
    
    try:
        # Parse email addresses (support both single and multiple)
        hr_email_input = data['hr_email']
        if isinstance(hr_email_input, str):
            # Split by comma or semicolon and clean up
            import re
            email_list = re.split(r'[,;]', hr_email_input)
            email_list = [email.strip() for email in email_list if email.strip()]
        else:
            email_list = [hr_email_input] if hr_email_input else []

        if not email_list:
            return jsonify({'error': 'No valid email addresses provided'}), 400

        # Parse names if provided
        hr_name_input = data.get('hr_name', '')
        if hr_name_input:
            name_list = [name.strip() for name in hr_name_input.split(',') if name.strip()]
        else:
            name_list = []

        # Prepare base template variables
        base_template_variables = {
            'company_name': data.get('company_name', ''),
            'company_domain': data.get('company_domain', ''),
            'position': data.get('position', ''),
            'user_phone': data.get('user_phone', '')
        }

        # Send emails to each recipient
        sender = EmailSender()
        successful_sends = []
        failed_sends = []

        for i, email in enumerate(email_list):
            # Get corresponding name if available
            recipient_name = name_list[i] if i < len(name_list) else ''

            # Prepare template variables for this recipient
            template_variables = base_template_variables.copy()
            template_variables['hr_name'] = recipient_name

            # Send email to this recipient
            success, message = sender.send_templated_email(
                smtp_config=smtp_config,
                email_template=template,
                recipient_email=email,
                template_variables=template_variables,
                recipient_name=recipient_name
            )

            if success:
                successful_sends.append(email)
            else:
                failed_sends.append({'email': email, 'error': message})

        # Return results
        if successful_sends and not failed_sends:
            return jsonify({
                'success': True,
                'message': f'Successfully sent to {len(successful_sends)} recipient(s)',
                'successful_sends': successful_sends
            })
        elif successful_sends and failed_sends:
            return jsonify({
                'success': True,
                'message': f'Partially successful: {len(successful_sends)} sent, {len(failed_sends)} failed',
                'successful_sends': successful_sends,
                'failed_sends': failed_sends
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to send to all {len(failed_sends)} recipient(s)',
                'failed_sends': failed_sends
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
