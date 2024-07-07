import os
import unittest
from app import app, db
from models import User
from dotenv import load_dotenv
from flask import current_app

load_dotenv()

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_URI')
        self.app = app.test_client()
        
        # Push the application context
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
        # Pop the application context
        self.app_context.pop()


    def test_register_user_success(self):
        response = self.app.post('/auth/register', json={
            'userId': 'testuser',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertIn('accessToken', data['data'])
        self.assertIn('userId', data['data']['user'])
        self.assertIn('John\'s Organisation', data['data']['user']['firstName'] + '\'s Organisation')

    def test_register_user_missing_field(self):
        response = self.app.post('/auth/register', json={
            'userId': 'testuser',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 422)

    def test_register_duplicate_email(self):
        self.app.post('/auth/register', json={
            'userId': 'testuser',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })
        response = self.app.post('/auth/register', json={
            'userId': 'testuser2',
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '0987654321'
        })
        self.assertEqual(response.status_code, 400)

    def test_login_user_success(self):
        self.app.post('/auth/register', json={
            'userId': 'testuser',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })
        response = self.app.post('/auth/login', json={
            'email': 'john.doe@example.com',
            'password': 'password123'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('accessToken', data['data'])

    def test_login_user_failure(self):
        response = self.app.post('/auth/login', json={
            'email': 'john.doe@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
