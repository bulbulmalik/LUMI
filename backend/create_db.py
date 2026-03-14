import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

app = create_app()

with app.app_context():
    from models.user import User
    from models.device_state import DeviceState
    from models.fraud_log import FraudLog
    from models.transaction import Transaction

    db.create_all()
    print("✅ Database tables created successfully!")