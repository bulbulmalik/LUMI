from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.navigation_service import start_navigation

navigation_bp = Blueprint('navigation', __name__, url_prefix='/api/navigation')

@navigation_bp.route('/start', methods=['POST'])
@jwt_required()
def start_nav():
    data = request.get_json()
    command = data.get('command', '')
    user_id = get_jwt_identity()
    result = start_navigation(user_id, command)
    return jsonify({"message": result})