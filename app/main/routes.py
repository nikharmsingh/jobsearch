from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.forms import EmailTemplateForm, SMTPConfigForm, CompanySearchForm, SendEmailForm
from app.models import User, SMTPConfig, EmailTemplate, JobSearch
from app.services import CompanyDomainFinder, EmailFinder, EmailSender
from datetime import datetime

@bp.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='JobSearch - Find HR Contacts & Send Emails')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    # Get user's recent job searches
    recent_searches = JobSearch.query.filter_by(user_id=current_user.id)\
        .order_by(JobSearch.created_at.desc()).limit(5).all()
    
    # Get user's configurations
    smtp_configs = SMTPConfig.query.filter_by(user_id=current_user.id).all()
    email_templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
    
    # Statistics
    total_searches = JobSearch.query.filter_by(user_id=current_user.id).count()
    emails_sent = JobSearch.query.filter_by(user_id=current_user.id, email_sent=True).count()
    
    return render_template('main/dashboard.html', 
                         title='Dashboard',
                         recent_searches=recent_searches,
                         smtp_configs=smtp_configs,
                         email_templates=email_templates,
                         total_searches=total_searches,
                         emails_sent=emails_sent)

@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Company search page"""
    form = CompanySearchForm()
    
    if form.validate_on_submit():
        # Create new job search record
        job_search = JobSearch(
            user_id=current_user.id,
            company_name=form.company_name.data,
            position=form.position.data,
            notes=form.notes.data
        )
        
        try:
            # Find company domain
            domain_finder = CompanyDomainFinder()
            domain = domain_finder.find_domain(form.company_name.data)
            job_search.company_domain = domain
            
            # Find HR emails if domain found
            hr_emails = []
            if domain:
                email_finder = EmailFinder()
                hr_emails = email_finder.find_hr_emails(form.company_name.data, domain)
                
                # Store the best HR contact if found
                if hr_emails:
                    best_contact = hr_emails[0]  # First result is usually best
                    job_search.hr_name = best_contact.get('name')
                    job_search.hr_email = best_contact.get('email')
                    job_search.hr_linkedin = best_contact.get('linkedin_url')
            
            db.session.add(job_search)
            db.session.commit()
            
            flash(f'Search completed for {form.company_name.data}!', 'success')
            return redirect(url_for('main.job_detail', id=job_search.id))
            
        except Exception as e:
            flash(f'Error during search: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('main/search.html', title='Search Company', form=form)

@bp.route('/job/<int:id>')
@login_required
def job_detail(id):
    """Job search detail page"""
    job_search = JobSearch.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Get additional HR emails if not already found
    hr_emails = []
    if job_search.company_domain:
        try:
            email_finder = EmailFinder()
            hr_emails = email_finder.find_hr_emails(job_search.company_name, job_search.company_domain)
        except Exception as e:
            flash(f'Error finding additional emails: {str(e)}', 'warning')
    
    # Get user's email templates and SMTP configs for sending
    email_templates = EmailTemplate.query.filter_by(user_id=current_user.id, is_active=True).all()
    smtp_configs = SMTPConfig.query.filter_by(user_id=current_user.id, is_verified=True).all()
    
    return render_template('main/job_detail.html',
                         title=f'Job Search - {job_search.company_name}',
                         job_search=job_search,
                         hr_emails=hr_emails,
                         email_templates=email_templates,
                         smtp_configs=smtp_configs,
                         now=datetime.now())

@bp.route('/templates')
@login_required
def templates():
    """Email templates management page"""
    templates = EmailTemplate.query.filter_by(user_id=current_user.id)\
        .order_by(EmailTemplate.created_at.desc()).all()
    return render_template('main/templates.html', title='Email Templates', templates=templates)

@bp.route('/templates/new', methods=['GET', 'POST'])
@login_required
def new_template():
    """Create new email template"""
    form = EmailTemplateForm()
    
    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data:
            EmailTemplate.query.filter_by(user_id=current_user.id, is_default=True)\
                .update({'is_default': False})
        
        template = EmailTemplate(
            user_id=current_user.id,
            name=form.name.data,
            subject=form.subject.data,
            body=form.body.data,
            is_default=form.is_default.data
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Email template created successfully!', 'success')
        return redirect(url_for('main.templates'))
    
    return render_template('main/template_form.html', title='New Email Template', form=form)

@bp.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_template(id):
    """Edit email template"""
    template = EmailTemplate.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = EmailTemplateForm(obj=template)

    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data and not template.is_default:
            EmailTemplate.query.filter_by(user_id=current_user.id, is_default=True)\
                .update({'is_default': False})

        template.name = form.name.data
        template.subject = form.subject.data
        template.body = form.body.data
        template.is_default = form.is_default.data
        template.updated_at = datetime.utcnow()

        db.session.commit()

        flash('Email template updated successfully!', 'success')
        return redirect(url_for('main.templates'))

    return render_template('main/template_form.html', title='Edit Email Template', form=form, template=template)

@bp.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
def delete_template(id):
    """Delete email template"""
    template = EmailTemplate.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    db.session.delete(template)
    db.session.commit()

    flash('Email template deleted successfully!', 'success')
    return redirect(url_for('main.templates'))

@bp.route('/smtp-configs')
@login_required
def smtp_configs():
    """SMTP configurations management page"""
    configs = SMTPConfig.query.filter_by(user_id=current_user.id)\
        .order_by(SMTPConfig.created_at.desc()).all()
    return render_template('main/smtp_configs.html', title='SMTP Configurations', configs=configs)

@bp.route('/smtp-configs/new', methods=['GET', 'POST'])
@login_required
def new_smtp_config():
    """Create new SMTP configuration"""
    form = SMTPConfigForm()

    if form.validate_on_submit():
        # If setting as active, unset other active configs
        if form.is_active.data:
            SMTPConfig.query.filter_by(user_id=current_user.id, is_active=True)\
                .update({'is_active': False})

        config = SMTPConfig(
            user_id=current_user.id,
            name=form.name.data,
            smtp_server=form.smtp_server.data,
            smtp_port=form.smtp_port.data,
            use_tls=form.use_tls.data,
            use_ssl=form.use_ssl.data,
            username=form.username.data,
            password=form.password.data,  # Will be encrypted in __init__
            from_email=form.from_email.data,
            from_name=form.from_name.data,
            is_active=form.is_active.data
        )

        db.session.add(config)
        db.session.commit()

        flash('SMTP configuration created successfully!', 'success')
        return redirect(url_for('main.smtp_configs'))

    return render_template('main/smtp_config_form.html', title='New SMTP Configuration', form=form)

@bp.route('/smtp-configs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_smtp_config(id):
    """Edit SMTP configuration"""
    config = SMTPConfig.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SMTPConfigForm(obj=config)

    # Don't populate password field for security
    form.password.data = ''

    if form.validate_on_submit():
        # If setting as active, unset other active configs
        if form.is_active.data and not config.is_active:
            SMTPConfig.query.filter_by(user_id=current_user.id, is_active=True)\
                .update({'is_active': False})

        config.name = form.name.data
        config.smtp_server = form.smtp_server.data
        config.smtp_port = form.smtp_port.data
        config.use_tls = form.use_tls.data
        config.use_ssl = form.use_ssl.data
        config.username = form.username.data
        if form.password.data:  # Only update password if provided
            config.set_password(form.password.data)
        config.from_email = form.from_email.data
        config.from_name = form.from_name.data
        config.is_active = form.is_active.data
        config.updated_at = datetime.utcnow()
        config.is_verified = False  # Reset verification status

        db.session.commit()

        flash('SMTP configuration updated successfully!', 'success')
        return redirect(url_for('main.smtp_configs'))

    return render_template('main/smtp_config_form.html', title='Edit SMTP Configuration', form=form, config=config)

@bp.route('/smtp-configs/<int:id>/delete', methods=['POST'])
@login_required
def delete_smtp_config(id):
    """Delete SMTP configuration"""
    config = SMTPConfig.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    db.session.delete(config)
    db.session.commit()

    flash('SMTP configuration deleted successfully!', 'success')
    return redirect(url_for('main.smtp_configs'))

@bp.route('/job-searches')
@login_required
def job_searches():
    """Job searches history page"""
    page = request.args.get('page', 1, type=int)
    searches = JobSearch.query.filter_by(user_id=current_user.id)\
        .order_by(JobSearch.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)

    return render_template('main/job_searches.html', title='Job Searches', searches=searches)
