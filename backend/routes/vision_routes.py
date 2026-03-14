from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.vision_service import VisionService
from services.navigation_service import NavigationService
import openai
import os

vision_bp = Blueprint('vision', __name__)
vision_service = VisionService()
navigation_service = NavigationService()

@vision_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'response': 'Please say something.'}), 400
    
    try:
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are LUMI, a friendly AI assistant for visually impaired people. Respond helpfully and empathetically. Keep responses brief for voice."},
                {"role": "user", "content": message}
            ],
            max_tokens=100
        )
        ai_response = response.choices[0].message.content.strip()
        return jsonify({'response': ai_response}), 200
    except Exception as e:
        return jsonify({'response': 'Sorry, I could not process that right now.'}), 500


@vision_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_frame():
    """
    Analyze a camera frame.
    Accepts: multipart/form-data with 'image' file and optional 'context' field
    """
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please send a camera image for me to analyze.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()
    context = request.form.get('context', 'general')

    result = vision_service.analyze_frame(image_data, context=context)

    return jsonify(result), 200


@vision_bp.route('/navigate', methods=['POST'])
@jwt_required()
def navigate():
    """
    Real-time navigation assistance.
    Accepts camera frame and returns path guidance.
    """
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please send a camera image for navigation guidance.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()

    # First analyze what the camera sees
    vision_result = vision_service.analyze_frame(image_data, context='navigation')

    # Then generate navigation instructions
    nav_result = navigation_service.analyze_path(vision_result)

    return jsonify({
        'vision': vision_result,
        'navigation': nav_result,
        'audio_message': nav_result['audio_message']
    }), 200


@vision_bp.route('/read', methods=['POST'])
@jwt_required()
def read_text():
    """
    Read text from an image (OCR).
    """
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please point the camera at the text you want me to read.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()

    result = vision_service.read_text_from_image(image_data)

    return jsonify(result), 200


@vision_bp.route('/describe', methods=['POST'])
@jwt_required()
def describe_scene():
    """
    Describe the current scene in detail.
    """
    if 'image' not in request.files:
        return jsonify({
            'error': 'No image provided',
            'audio_message': 'Please send an image for me to describe.'
        }), 400

    image_file = request.files['image']
    image_data = image_file.read()

    result = vision_service.analyze_frame(image_data, context='general')

    return jsonify(result), 200


@vision_bp.route('/direction', methods=['POST'])
@jwt_required()
def get_direction():
    """
    Get direction guidance to a destination.
    Expects JSON with 'current_location' and 'destination'.
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'error': 'Location data required',
            'audio_message': 'I need your current location and destination to guide you.'
        }), 400

    current = data.get('current_location', {})
    destination = data.get('destination', {})

    if not current.get('lat') or not current.get('lng'):
        return jsonify({
            'error': 'Current location required',
            'audio_message': 'I need your current GPS location. Please enable location services.'
        }), 400

    result = navigation_service.get_direction_guidance(current, destination)

    return jsonify(result), 200