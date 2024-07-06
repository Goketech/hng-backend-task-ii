import os
import uuid

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from flask_migrate import Migrate
from models import db, User, Organisation
from validate import Validate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({'message': 'Missing JWT token'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid JWT token'}), 401

@app.route('/')
def home():
    return 'Hiiiii'

@app.route('/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    try:
        validated_data = Validate.validate_user(data)
        if isinstance(validated_data, tuple):
            return validated_data
        validated_data['password'] = generate_password_hash(validated_data['password'])
        validated_data['userId'] = str(uuid.uuid4())
        user = Validate.save_user(validated_data)

        access_token = create_access_token(identity=user.userId)

        response = {
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone
                }
            }
        }

        return jsonify(response), 201
    except BadRequest as e:
        response = {
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }
        return jsonify(response), 400
    
@app.route('/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
         response = {
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }
         return jsonify(response), 401
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        response = {
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }
        return jsonify(response), 401
    access_token = create_access_token(identity=user.userId)
    response = {
        "status": "success",
        "message": "Login successful",
        "data": {
            "accessToken": access_token,
            "user": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone
            }
        }
    }
    return jsonify(response), 200

@app.route('/api/users/<id>', methods=['GET'])
@jwt_required()
def get_user(id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(userId=current_user_id).first()

    if not current_user:
        return jsonify({'message': 'Current user not found'}), 404

    user = User.query.filter_by(userId=id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user not in current_user.organisations and user != current_user:
        return jsonify({'message': 'You do not have permission to view this user'}), 403

    response = {
        "status": "success",
        "message": "User retrieved successfully",
        "data": {
            "userId": user.userId,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone": user.phone
        }
    }
    return jsonify(response), 200

@app.route('/api/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    user_id = get_jwt_identity()
    user = User.query.filter_by(userId=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    organisations = user.organisations
    organisation_list = [{
        "orgId": org.orgId,
        "name": org.name,
        "description": org.description
    } for org in organisations]

    response = {
        "status": "success",
        "message": "Organisations retrieved successfully",
        "data": {
            "organisations": organisation_list
        }
    }
    return jsonify(response), 200

@app.route('/api/organisations/<orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    user_id = get_jwt_identity()
    user = User.query.filter_by(userId=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    organisation = Organisation.query.filter_by(orgId=orgId).first()

    if not organisation:
        return jsonify({'message': 'Organisation not found'}), 404

    # Check if the logged-in user belongs to the organisation
    if user not in organisation.users:
        return jsonify({'message': 'You do not have permission to view this organisation'}), 403

    response = {
        "status": "success",
        "message": "Organisation retrieved successfully",
        "data": {
            "orgId": organisation.orgId,
            "name": organisation.name,
            "description": organisation.description
        }
    }
    return jsonify(response), 200

@app.route('/api/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    user_id = get_jwt_identity()
    user = User.query.filter_by(userId=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    if not data or not data.get('name'):
        response = {
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400
        }
        return jsonify(response), 400

    name = data['name']
    description = data.get('description', '')

    organisation = Organisation(name=name, description=description)
    organisation.users.append(user)

    try:
        db.session.add(organisation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        response = {
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400
        }
        return jsonify(response), 400

    response = {
        "status": "success",
        "message": "Organisation created successfully",
        "data": {
            "orgId": organisation.orgId,
            "name": organisation.name,
            "description": organisation.description
        }
    }
    return jsonify(response), 201

@app.route('/api/organisations/<orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    user_id = get_jwt_identity()
    user = User.query.filter_by(userId=user_id).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    if not data or not data.get('userId'):
        response = {
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400
        }
        return jsonify(response), 400

    target_user = User.query.filter_by(userId=data['userId']).first()
    if not target_user:
        response = {
            "status": "Bad request",
            "message": "User not found",
            "statusCode": 404
        }
        return jsonify(response), 404

    organisation = Organisation.query.filter_by(orgId=orgId).first()
    if not organisation:
        response = {
            "status": "Bad request",
            "message": "Organisation not found",
            "statusCode": 404
        }
        return jsonify(response), 404

    # Check if the logged-in user belongs to the organisation
    if user not in organisation.users:
        return jsonify({'message': 'You do not have permission to add users to this organisation'}), 403

    organisation.users.append(target_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()       
        response = {
            "status": "Bad request",
            "message": "Client error",
            "statusCode": 400
        }
        return jsonify(response), 400

    response = {
        "status": "success",
        "message": "User added to organisation successfully"
    }
    return jsonify(response), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
