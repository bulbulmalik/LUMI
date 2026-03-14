from extensions import db          # ← CHANGED
from datetime import datetime


class FraudLog(db.Model):
    __tablename__ = 'fraud_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    detection_type = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(10), default='INR')
    expected_amount = db.Column(db.Float, nullable=True)
    detected_amount = db.Column(db.Float, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    image_path = db.Column(db.String(256), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_fraud = db.Column(db.Boolean, default=False)
    action_taken = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'detection_type': self.detection_type,
            'currency': self.currency,
            'expected_amount': self.expected_amount,
            'detected_amount': self.detected_amount,
            'confidence_score': self.confidence_score,
            'description': self.description,
            'is_fraud': self.is_fraud,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat()
        }