from extensions import db          # ← CHANGED
from datetime import datetime


class DeviceState(db.Model):
    __tablename__ = 'device_states'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    battery_level = db.Column(db.Integer, nullable=True)
    brightness = db.Column(db.Integer, nullable=True)
    volume = db.Column(db.Integer, nullable=True)
    wifi_connected = db.Column(db.Boolean, default=False)
    bluetooth_connected = db.Column(db.Boolean, default=False)
    gps_enabled = db.Column(db.Boolean, default=False)
    current_app = db.Column(db.String(120), nullable=True)
    screen_reader_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_type': self.device_type,
            'battery_level': self.battery_level,
            'brightness': self.brightness,
            'volume': self.volume,
            'wifi_connected': self.wifi_connected,
            'bluetooth_connected': self.bluetooth_connected,
            'gps_enabled': self.gps_enabled,
            'current_app': self.current_app,
            'screen_reader_active': self.screen_reader_active,
            'last_updated': self.last_updated.isoformat()
        }