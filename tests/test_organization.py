import os
import unittest
from app import app, db
from models import User, Organisation
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv
from flask import current_app

load_dotenv()

class OrganisationTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_URI')
        self.app = app.test_client()
        
        # Push the application context
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()

        self.user = User(userId='testuser', firstName='John', lastName='Doe', email='john.doe@example.com', password='password123', phone='1234567890')
        self.another_user = User(userId='anotheruser', firstName='Jane', lastName='Doe', email='mark.hng@example.com', password='password123', phone='0987654321')
        db.session.add(self.user)
        self.organisation = Organisation(orgId='testorg', name='Test Organisation', description='A test organisation')
        self.organisation.users.append(self.user)
        self.organisation.users.append(self.another_user)
        db.session.add(self.organisation)
        db.session.commit()

        self.access_token = create_access_token(identity=self.user.userId)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
        # Pop the application context
        self.app_context.pop()

    def test_get_user_success(self):
        response = self.app.get(f'/api/users/{self.another_user.userId}', headers={'Authorization': f'Bearer {self.access_token}'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['userId'], self.another_user.userId)

    def test_get_user_not_found(self):
        response = self.app.get('/api/users/nonexistent', headers={'Authorization': f'Bearer {self.access_token}'})
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'User not found')

    def test_get_user_current_user_not_found(self):
        # Remove current user from the database
        db.session.delete(self.user)
        db.session.commit()

        response = self.app.get(f'/api/users/{self.another_user.userId}', headers={'Authorization': f'Bearer {self.access_token}'})
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Current user not found')

    def test_get_user_no_permission(self):
        new_user = User(userId='newuser', firstName='Jack', lastName='Smith', email='jack.smith@example.com', password='password123', phone='1231231234')
        db.session.add(new_user)
        db.session.commit()
        
        new_user_token = create_access_token(identity=new_user.userId)

        response = self.app.get(f'/api/users/{self.user.userId}', headers={'Authorization': f'Bearer {new_user_token}'})
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['message'], 'You do not have permission to view this user')

    def test_get_organisations(self):
        response = self.app.get('/api/organisations', headers={'Authorization': f'Bearer {self.access_token}'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['organisations']), 1)
        self.assertEqual(data['data']['organisations'][0]['name'], 'Test Organisation')

    def test_get_organisation_unauthorized(self):
        response = self.app.get('/api/organisations/testorg', headers={'Authorization': f'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)

    def test_create_organisation(self):
        response = self.app.post('/api/organisations', json={'name': 'New Organisation', 'description': 'A new organisation'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()['message'], 'Organisation created successfully')

    def test_add_user_to_organisation(self):
        new_user = User(userId='newuser', firstName='Jane', lastName='Doe', email='jane.doe@example.com', password='password123', phone='0987654321')
        db.session.add(new_user)
        db.session.commit()

        response = self.app.post('/api/organisations/testorg/users', json={'userId': 'newuser'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], 'User added to organisation successfully')

    def test_add_user_to_organisation_unauthorized(self):
        new_user = User(userId='newuser', firstName='Jane', lastName='Doe', email='jane.doe@example.com', password='password123', phone='0987654321')
        db.session.add(new_user)
        db.session.commit()

        response = self.app.post('/api/organisations/testorg/users', json={'userId': 'newuser'}, headers={'Authorization': f'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)

    def test_get_organisation_no_access(self):
        new_user = User(userId='newuser2', firstName='Jack', lastName='Smith', email='jack.smith@example.com', password='password123', phone='1231231234')
        db.session.add(new_user)
        db.session.commit()
        access_token_new_user = create_access_token(identity=new_user.userId)

        response = self.app.get('/api/organisations/testorg', headers={'Authorization': f'Bearer {access_token_new_user}'})
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
