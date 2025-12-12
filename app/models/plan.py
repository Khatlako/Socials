from app import db
from datetime import datetime
import json

class Plan(db.Model):
    """Subscription pricing plans (Free, Pro, Business, Enterprise)"""
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)  # free, pro, business, enterprise
    display_name = db.Column(db.String(100), nullable=False)  # Free, Pro, Business, Enterprise
    slug = db.Column(db.String(50), unique=True, nullable=False)  # for URLs
    description = db.Column(db.Text)
    
    # Pricing
    monthly_price = db.Column(db.Float, default=0)  # in USD cents (29.00 = $29)
    annual_price = db.Column(db.Float)  # in USD cents
    annual_discount_percent = db.Column(db.Float, default=0)  # e.g., 17 for 17% off
    
    # Trial settings
    trial_days = db.Column(db.Integer, default=0)  # 0 = no trial, 14 = 14-day trial
    require_card_for_trial = db.Column(db.Boolean, default=False)  # Pro=False, Business=True
    
    # Feature limits (stored as JSON for flexibility)
    features = db.Column(db.JSON, default={
        'pages': 1,
        'team_members': 1,
        'posts_per_month': 30,
        'scheduled_posts': 10,
        'media_storage_gb': 0.05,  # 50MB
        'analytics_history_days': 30,
        'ai_captions_per_month': 0,
        'support_response_hours': None,
        'api_access': False,
        'advanced_analytics': False,
        'competitor_analysis': False,
        'export_reports': False,
    })
    
    # Ecocash USSD push pricing in ZWL
    ecocash_monthly_price = db.Column(db.Float)  # in ZWL
    ecocash_annual_price = db.Column(db.Float)   # in ZWL
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)  # For ordering on pricing page (0=Free, 1=Pro, 2=Business, 3=Enterprise)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Plan {self.display_name}>'
    
    def get_feature(self, feature_name):
        """Get a specific feature limit"""
        return self.features.get(feature_name)
    
    def annual_savings(self):
        """Calculate annual savings vs monthly"""
        if self.annual_price and self.monthly_price:
            monthly_annual_cost = self.monthly_price * 12
            savings = monthly_annual_cost - self.annual_price
            return savings
        return 0


class Subscription(db.Model):
    """User subscriptions to plans"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    
    # Ecocash specific
    phone_number = db.Column(db.String(20))  # Phone number for Ecocash payments
    ecocash_transaction_id = db.Column(db.String(255), unique=True)  # Ecocash API transaction ID
    
    # Subscription status: active, past_due, canceled, paused, trialing, pending (for ecocash)
    status = db.Column(db.String(50), default='trialing', index=True)
    
    # Billing cycle
    billing_interval = db.Column(db.String(50), default='monthly')  # monthly or annual
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    
    # Trial
    trial_start = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)
    trial_days_remaining = db.Column(db.Integer, default=0)
    
    # Cancellation
    canceled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.String(255))
    cancel_at_period_end = db.Column(db.Boolean, default=False)  # Downgrade after current period
    
    # Amount (in USD cents for Stripe, ZWL for Ecocash)
    amount_billed = db.Column(db.Float)  # Last billed amount
    currency = db.Column(db.String(10), default='USD')  # USD or ZWL
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='subscriptions', lazy='joined', foreign_keys=[user_id])
    invoices = db.relationship('Invoice', backref='subscription', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subscription {self.user_id} - {self.plan.display_name}>'
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active'
    
    def is_trialing(self):
        """Check if in trial period"""
        return self.status == 'trialing'
    
    def is_canceled(self):
        """Check if subscription is canceled"""
        return self.status == 'canceled'
    
    def days_until_renewal(self):
        """Days until next billing date"""
        if self.current_period_end:
            delta = self.current_period_end - datetime.utcnow()
            return delta.days
        return 0


class Invoice(db.Model):
    """Billing invoices"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    
    # Ecocash reference
    ecocash_transaction_id = db.Column(db.String(255), unique=True)
    
    # Invoice details
    invoice_number = db.Column(db.String(100), unique=True)  # INV-2025-001, etc
    status = db.Column(db.String(50), default='draft')  # draft, open, paid, void, uncollectible
    amount_due = db.Column(db.Float)  # in USD cents
    amount_paid = db.Column(db.Float, default=0)  # in USD cents
    amount_remaining = db.Column(db.Float)
    
    # Dates
    issued_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    paid_date = db.Column(db.DateTime)
    
    # Payment attempt info
    attempted = db.Column(db.Boolean, default=False)
    attempt_count = db.Column(db.Integer, default=0)
    next_payment_attempt = db.Column(db.DateTime)
    
    # Invoice lines (stored as JSON)
    lines = db.Column(db.JSON)  # [{description, amount, period_start, period_end}]
    
    # Metadata
    currency = db.Column(db.String(3), default='ZWL')
    description = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='invoices')
    payments = db.relationship('Payment', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.status}>'
    
    def is_paid(self):
        return self.status == 'paid'
    
    def is_overdue(self):
        if self.due_date and not self.is_paid():
            return datetime.utcnow() > self.due_date
        return False


class Payment(db.Model):
    """Payment records for tracking transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    
    # Ecocash reference
    ecocash_transaction_id = db.Column(db.String(255), unique=True)
    
    # Payment details
    amount = db.Column(db.Float)  # in ZWL
    currency = db.Column(db.String(3), default='ZWL')
    status = db.Column(db.String(50))  # succeeded, processing, requires_action, canceled, failed
    
    # Payment method
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    
    # Failure info
    failure_code = db.Column(db.String(100))
    failure_message = db.Column(db.String(500))
    
    # Metadata
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.ecocash_transaction_id} - {self.status}>'


class PaymentMethod(db.Model):
    """Saved phone numbers for Ecocash"""
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Ecocash phone number
    phone_number = db.Column(db.String(20), unique=True)
    phone_number_verified = db.Column(db.Boolean, default=False)
    
    # Status
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='ecocash_numbers')
    
    def __repr__(self):
        return f'<PaymentMethod {self.phone_number}>'
