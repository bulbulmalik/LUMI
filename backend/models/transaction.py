from extensions import db          # ← CHANGED
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    recipient = db.Column(db.String(120), nullable=True)
    sender = db.Column(db.String(120), nullable=True)
    upi_id = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default='pending')
    verified = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'currency': self.currency,
            'recipient': self.recipient,
            'sender': self.sender,
            'upi_id': self.upi_id,
            'status': self.status,
            'verified': self.verified,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }