from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from extensions import db          # ← CHANGED from "from app import db"
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'No data provided',
            'audio_message': 'Registration failed. No information was provided.'
        }), 400

    required = ['name', 'email', 'password']
    for field in required:
        if field not in data:
            return jsonify({
                'error': f'{field} is required',
                'audio_message': f'Please provide your {field} to register.'
            }), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email already registered',
            'audio_message': 'This email is already registered. Please log in instead.'
        }), 409

    user = User(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        preferred_language=data.get('preferred_language', 'en'),
        voice_speed=data.get('voice_speed', 1.0),
        emergency_contact=data.get('emergency_contact')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'audio_message': f'Welcome to LUMI, {user.name}! Your account has been created successfully.'
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'error': 'Email and password required',
            'audio_message': 'Please provide your email and password to log in.'
        }), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({
            'error': 'Invalid credentials',
            'audio_message': 'Login failed. The email or password is incorrect.'
        }), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'audio_message': f'Welcome back, {user.name}! You are now logged in.'
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'user': user.to_dict(),
        'audio_message': f"Your profile: Name is {user.name}, Email is {user.email}."
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    updatable = ['name', 'phone', 'preferred_language', 'voice_speed', 'emergency_contact']

    for field in updatable:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()

    return jsonify({
        'user': user.to_dict(),
        'audio_message': 'Your profile has been updated successfully.'
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}), 200