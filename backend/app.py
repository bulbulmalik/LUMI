from flask import Flask
from flask_cors import CORS
import logging
import os

from config import config_by_name
from extensions import db, jwt


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure folders exist
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('LOG_DIR', 'logs'), exist_ok=True)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Register Blueprints - INSIDE the function to avoid circular imports
    from routes.audio_routes import audio_bp
    from routes.auth_routes import auth_bp
    from routes.vision_routes import vision_bp
    from routes.payment_routes import payment_bp
    from routes.navigation_routes import navigation_bp

    app.register_blueprint(audio_bp, url_prefix='/api/audio')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vision_bp, url_prefix='/api/vision')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    app.register_blueprint(navigation_bp)

    # Error handlers
    from middlewares.error_handler import register_error_handlers
    register_error_handlers(app)

    # Health check
    @app.route('/api/health')
    def health_check():
        return {
            'status': 'healthy',
            'app': 'LUMI',
            'version': '1.0.0'
        }

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)