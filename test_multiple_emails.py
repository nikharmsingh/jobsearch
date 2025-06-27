#!/usr/bin/env python3
"""
Test script for multiple email functionality in Send Manual Email feature.
This script tests the form validation and email parsing logic.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main.forms import SendEmailForm, validate_multiple_emails
from wtforms.validators import ValidationError


class TestMultipleEmailFunctionality(unittest.TestCase):
    """Test cases for multiple email functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.form_data = {
            'template_id': 1,
            'smtp_config_id': 1,
            'company_name': 'Test Company',
            'company_domain': 'test.com',
            'position': 'Software Engineer'
        }
    
    def test_single_email_validation(self):
        """Test validation with a single valid email"""
        # Create a mock field
        class MockField:
            def __init__(self, data):
                self.data = data
        
        # Test valid single email
        field = MockField('test@example.com')
        form = Mock()
        
        # Should not raise ValidationError
        try:
            validate_multiple_emails(form, field)
        except ValidationError:
            self.fail("validate_multiple_emails raised ValidationError for valid single email")
    
    def test_multiple_emails_validation(self):
        """Test validation with multiple valid emails"""
        class MockField:
            def __init__(self, data):
                self.data = data
        
        # Test multiple valid emails with comma
        field = MockField('test1@example.com, test2@example.com, test3@example.com')
        form = Mock()
        
        try:
            validate_multiple_emails(form, field)
        except ValidationError:
            self.fail("validate_multiple_emails raised ValidationError for valid multiple emails")
        
        # Test multiple valid emails with semicolon
        field = MockField('test1@example.com; test2@example.com; test3@example.com')
        
        try:
            validate_multiple_emails(form, field)
        except ValidationError:
            self.fail("validate_multiple_emails raised ValidationError for valid multiple emails with semicolon")
    
    def test_invalid_email_validation(self):
        """Test validation with invalid emails"""
        class MockField:
            def __init__(self, data):
                self.data = data
        
        # Test single invalid email
        field = MockField('invalid-email')
        form = Mock()
        
        with self.assertRaises(ValidationError):
            validate_multiple_emails(form, field)
        
        # Test mix of valid and invalid emails
        field = MockField('valid@example.com, invalid-email, another@example.com')
        
        with self.assertRaises(ValidationError):
            validate_multiple_emails(form, field)
    
    def test_empty_email_field(self):
        """Test validation with empty email field"""
        class MockField:
            def __init__(self, data):
                self.data = data
        
        # Test empty field
        field = MockField('')
        form = Mock()
        
        # Should not raise ValidationError for empty field (handled by DataRequired)
        try:
            validate_multiple_emails(form, field)
        except ValidationError:
            self.fail("validate_multiple_emails raised ValidationError for empty field")
    
    def test_email_parsing(self):
        """Test email parsing functionality"""
        # Mock the form with email data
        form = Mock()
        form.hr_email = Mock()
        
        # Test single email parsing
        form.hr_email.data = 'test@example.com'
        
        # Create a SendEmailForm instance (we'll mock the __init__ method)
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_email = form.hr_email
            
            emails = send_form.get_email_list()
            self.assertEqual(emails, ['test@example.com'])
        
        # Test multiple emails with comma
        form.hr_email.data = 'test1@example.com, test2@example.com, test3@example.com'
        
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_email = form.hr_email
            
            emails = send_form.get_email_list()
            expected = ['test1@example.com', 'test2@example.com', 'test3@example.com']
            self.assertEqual(emails, expected)
        
        # Test multiple emails with semicolon
        form.hr_email.data = 'test1@example.com; test2@example.com; test3@example.com'
        
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_email = form.hr_email
            
            emails = send_form.get_email_list()
            expected = ['test1@example.com', 'test2@example.com', 'test3@example.com']
            self.assertEqual(emails, expected)
        
        # Test mixed separators and extra spaces
        form.hr_email.data = ' test1@example.com , test2@example.com; test3@example.com '
        
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_email = form.hr_email
            
            emails = send_form.get_email_list()
            expected = ['test1@example.com', 'test2@example.com', 'test3@example.com']
            self.assertEqual(emails, expected)
    
    def test_name_parsing(self):
        """Test name parsing functionality"""
        # Mock the form with name data
        form = Mock()
        form.hr_name = Mock()
        
        # Test single name parsing
        form.hr_name.data = 'John Doe'
        
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_name = form.hr_name
            
            names = send_form.get_name_list()
            self.assertEqual(names, ['John Doe'])
        
        # Test multiple names
        form.hr_name.data = 'John Doe, Jane Smith, Bob Johnson'
        
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_name = form.hr_name
            
            names = send_form.get_name_list()
            expected = ['John Doe', 'Jane Smith', 'Bob Johnson']
            self.assertEqual(names, expected)
        
        # Test empty names
        form.hr_name.data = ''
        
        with patch.object(SendEmailForm, '__init__', lambda x, *args, **kwargs: None):
            send_form = SendEmailForm()
            send_form.hr_name = form.hr_name
            
            names = send_form.get_name_list()
            self.assertEqual(names, [])


def run_tests():
    """Run all tests and display results"""
    print("🧪 Testing Multiple Email Functionality")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMultipleEmailFunctionality)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Display summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed! Multiple email functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
