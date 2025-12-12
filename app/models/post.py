from app import db
from datetime import datetime

class Post(db.Model):
    """Social media posts (AI-generated or manual)"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    caption = db.Column(db.String(255))
    
    # Post metadata
    post_type = db.Column(db.String(50), default='manual', nullable=False)  # ai_generated, manual
    source_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'))  # For AI-generated posts
    
    # Status
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)  
    # pending -> approved -> posted OR rejected
    rejection_reason = db.Column(db.Text)
    
    # Edit history
    original_content = db.Column(db.Text)  # Before any edits
    edit_count = db.Column(db.Integer, default=0)
    last_edited_at = db.Column(db.DateTime)
    
    # AI metadata
    ai_confidence = db.Column(db.Float)  # 0-1 confidence score
    ai_model_used = db.Column(db.String(100))
    
    # Hashtags and captions
    hashtags = db.Column(db.String(500))
    auto_caption = db.Column(db.String(500))
    
    # Preview URL (for image thumbnails)
    preview_url = db.Column(db.String(500))
    
    # Facebook posting
    facebook_post_id = db.Column(db.String(255), unique=True)
    facebook_url = db.Column(db.String(500))
    posted_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    analytics = db.relationship('PostAnalytics', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    scheduled_posts = db.relationship('ScheduledPost', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.id} - {self.status}>'
    
    def mark_as_approved(self, user):
        """Mark post as approved"""
        self.status = 'approved'
        self.approved_at = datetime.utcnow()
        self.approved_by_id = user.id
        db.session.commit()
    
    def mark_as_posted(self, facebook_post_id, facebook_url):
        """Mark post as posted on Facebook"""
        self.status = 'posted'
        self.facebook_post_id = facebook_post_id
        self.facebook_url = facebook_url
        self.posted_at = datetime.utcnow()
        db.session.commit()
