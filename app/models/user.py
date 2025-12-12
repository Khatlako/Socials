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
    page_access_token = db.Column(db.Text)
    
    # Business account info
    facebook_business_accounts = db.Column(db.JSON, default=list)
    facebook_pages = db.Column(db.JSON, default=list)
    selected_business_account_id = db.Column(db.String(255))
    selected_page_id = db.Column(db.String(255))
    selected_page_name = db.Column(db.String(255))
    
    # User settings
    timezone = db.Column(db.String(50), default='UTC')
    notification_enabled = db.Column(db.Boolean, default=True)
    ai_enabled = db.Column(db.Boolean, default=True)
    
    # Subscription & Billing
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id', name='fk_users_plan_id'))
    ecocash_phone_number = db.Column(db.String(20))
    current_subscription_id = db.Column(
        db.Integer, 
        db.ForeignKey('subscriptions.id', name='fk_users_subscription_id')
    )
    subscription_status = db.Column(db.String(50), default='none')
    subscription_ends_at = db.Column(db.DateTime)
    billing_email = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    portfolios = db.relationship(
        'Portfolio', backref='owner', lazy='dynamic', cascade='all, delete-orphan'
    )
    media = db.relationship(
        'Media', backref='owner', lazy='dynamic', cascade='all, delete-orphan'
    )
    posts = db.relationship(
        'Post', backref='creator', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Post.user_id'
    )
    scheduled_posts = db.relationship(
        'ScheduledPost', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    analytics = db.relationship(
        'PostAnalytics', backref='user', lazy='dynamic', cascade='all, delete-orphan'
    )
    
    # Subscription relationships
    plan = db.relationship('Plan', backref='users')
    current_subscription = db.relationship('Subscription', foreign_keys=[current_subscription_id], uselist=False)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def is_token_expired(self):
        if self.token_expires_at:
            return datetime.utcnow() >= self.token_expires_at
        return False
    
    def get_id(self):
        return str(self.id)
    
    def get_current_plan(self):
        if self.current_subscription and self.current_subscription.is_active():
            return self.current_subscription.plan
        from app.models.plan import Plan
        return Plan.query.filter_by(name='free').first()
    
    def has_feature(self, feature_name):
        plan = self.get_current_plan()
        if plan:
            return plan.get_feature(feature_name)
        return None
    
    def is_on_free_plan(self):
        plan = self.get_current_plan()
        return plan and plan.name == 'free'
    
    def is_paid_subscriber(self):
        if self.current_subscription:
            return self.current_subscription.is_active() and self.current_subscription.plan.name != 'free'
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
