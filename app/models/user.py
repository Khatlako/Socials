from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json

class User(UserMixin, db.Model):
    """User model with Facebook Business account info"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    facebook_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(500))
    
    # Facebook OAuth tokens
    access_token = db.Column(db.Text, nullable=False)  # User access token (short-lived)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    
    # Page access token (long-lived - never expires)
    page_access_token = db.Column(db.Text)  # Long-lived page token for posting
    
    # Business account info
    facebook_business_accounts = db.Column(db.JSON, default=list)  # List of business accounts
    facebook_pages = db.Column(db.JSON, default=list)  # List of available pages with tokens
    selected_business_account_id = db.Column(db.String(255))  # Currently selected account
    selected_page_id = db.Column(db.String(255))  # Currently selected page
    selected_page_name = db.Column(db.String(255))  # Page name for display
    
    # User settings
    timezone = db.Column(db.String(50), default='UTC')
    notification_enabled = db.Column(db.Boolean, default=True)
    ai_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    portfolios = db.relationship('Portfolio', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    media = db.relationship('Media', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    scheduled_posts = db.relationship('ScheduledPost', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analytics = db.relationship('PostAnalytics', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_token_expired(self):
        """Check if access token is expired"""
        if self.token_expires_at:
            return datetime.utcnow() >= self.token_expires_at
        return False
    
    def get_id(self):
        """Override for Flask-Login"""
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
