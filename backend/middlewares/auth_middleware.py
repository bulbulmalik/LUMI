from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return jsonify({'error': 'Unauthorized'}), 401
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Admin verification failed: {str(e)}")
            return jsonify({'error': 'Admin access required'}), 403
    return decorated_function