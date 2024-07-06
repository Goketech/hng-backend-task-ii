from flask import jsonify
from werkzeug.exceptions import BadRequest
from models import db, User, Organisation
import uuid

class Validate(User):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def validate_user(data):
        errors = []
        if not data.get('userId'):
            errors.append({'field': 'userId', 'message': 'User ID is required'})
        if not data.get('firstName'):
            errors.append({'field': 'firstName', 'message': 'First name is required'})
        if not data.get('lastName'):
            errors.append({'field': 'lastName', 'message': 'Last name is required'})
        if not data.get('email'):
            errors.append({'field': 'email', 'message': 'Email is required'})
        if not data.get('password'):
            errors.append({'field': 'password', 'message': 'Password is required'})
        if errors:
            raise BadRequest(jsonify({'errors': errors}), 422)
        return data
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()

            # Create an organisation for the user
            organisation_name = f"{self.firstName}'s Organisation"
            organisation = Organisation(
                orgId=str(uuid.uuid4()),
                name=organisation_name,
                description=f"{self.firstName} {self.lastName}'s organisation"
            )
            self.organisations.append(organisation)
            db.session.add(organisation)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            error_message = str(e)
            raise BadRequest(f"Validation error: {error_message}")
