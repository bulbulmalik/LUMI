import os
import sys

# Make sure we can find our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app, db

app = create_app()

with app.app_context():
    # Import all models so tables get created
    from models.user import User
    from models.device_state import DeviceState
    from models.fraud_log import FraudLog
    from models.transaction import Transaction
    db.create_all()
    print("✅ Database ready")

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║            🌟 LUMI IS RUNNING 🌟         ║
    ║   AI Assistant for Visually Impaired     ║
    ║                                          ║
    ║   API:  http://localhost:5000            ║
    ║   Health: /api/health                    ║
    ╚══════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)