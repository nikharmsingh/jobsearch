#!/usr/bin/env python3
"""
Simple script to create database tables
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app components
from flask import Flask
from config import Config
from app import db, login_manager, migrate

# Import all models to ensure they're registered
from app.models import User, SMTPConfig, EmailTemplate, JobSearch

def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    return app

def create_tables():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Print table info
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")

if __name__ == '__main__':
    create_tables()
