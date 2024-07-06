from flask import jsonify
from werkzeug.exceptions import BadRequest
from models import db, User, Organisation
import uuid

class Validate():

    @staticmethod
    def validate_user(data):
        errors = []
        if not data.get('firstName'):
            errors.append({'field': 'firstName', 'message': 'First name is required'})
        if not data.get('lastName'):
            errors.append({'field': 'lastName', 'message': 'Last name is required'})
        if not data.get('email'):
            errors.append({'field': 'email', 'message': 'Email is required'})
        if not data.get('password'):
            errors.append({'field': 'password', 'message': 'Password is required'})
        if errors:
            return jsonify({'errors': errors}), 422
        return data
    
    @staticmethod
    def save_user(user_data):
        user = User(**user_data)
        try:
            db.session.add(user)
            db.session.commit()

            # Create an organisation for the user
            organisation_name = f"{user.firstName}'s Organisation"
            organisation = Organisation(
                orgId=str(uuid.uuid4()),
                name=organisation_name,
                description=f"{user.firstName} {user.lastName}'s organisation"
            )
            user.organisations.append(organisation)
            db.session.add(organisation)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            error_message = str(e)
            raise BadRequest(f"Validation error: {error_message}")

        return user
