from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional

db = SQLAlchemy()

class URL(db.Model):
    """Model for storing URL mappings"""
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship to clicks
    clicks = db.relationship('Click', backref='url', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<URL {self.short_code}: {self.original_url}>'
    
    def to_dict(self):
        """Convert URL object to dictionary"""
        return {
            'id': self.id,
            'original_url': self.original_url,
            'short_code': self.short_code,
            'short_url': f'http://localhost:5000/{self.short_code}',
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'click_count': self.clicks.count()
        }
    
    def is_expired(self) -> bool:
        """Check if URL has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class Click(db.Model):
    """Model for tracking URL clicks"""
    __tablename__ = 'clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False, index=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    referrer = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Click {self.id}: URL {self.url_id} at {self.clicked_at}>'
    
    def to_dict(self):
        """Convert Click object to dictionary"""
        return {
            'id': self.id,
            'url_id': self.url_id,
            'clicked_at': self.clicked_at.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer
        }