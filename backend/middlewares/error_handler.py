from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad Request: {error}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(error),
            'audio_message': 'Sorry, the request was not understood. Please try again.'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized: {error}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required.',
            'audio_message': 'You need to log in first. Please authenticate.'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden: {error}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission.',
            'audio_message': 'Access denied. You do not have permission for this action.'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Not Found: {error}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'audio_message': 'Sorry, I could not find what you were looking for.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Something went wrong on our end.',
            'audio_message': 'An error occurred. Please try again in a moment.'
        }), 500