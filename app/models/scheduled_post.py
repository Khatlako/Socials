from app import db
from datetime import datetime

class ScheduledPost(db.Model):
    """Scheduled posts for automatic publishing"""
    __tablename__ = 'scheduled_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime, nullable=False, index=True)
    publish_status = db.Column(db.String(50), default='scheduled', nullable=False)
    # scheduled, published, failed, cancelled
    
    # Publishing info
    published_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    last_retry_at = db.Column(db.DateTime)
    
    # Notifications
    notification_sent_24h = db.Column(db.Boolean, default=False)
    notification_sent_1h = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScheduledPost {self.id} - {self.publish_status}>'
    
    def is_ready_to_publish(self):
        """Check if post is ready to be published"""
        return (self.publish_status == 'scheduled' and 
                datetime.utcnow() >= self.scheduled_at)
