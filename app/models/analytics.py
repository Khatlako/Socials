from app import db
from datetime import datetime

class PostAnalytics(db.Model):
    """Analytics data for posted content"""
    __tablename__ = 'post_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    
    # Engagement metrics
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    
    # Engagement rate
    engagement_rate = db.Column(db.Float, default=0.0)  # Percentage
    
    # Video specific (if applicable)
    views = db.Column(db.Integer, default=0)
    watch_time = db.Column(db.Integer, default=0)  # in seconds
    video_play_actions = db.Column(db.Integer, default=0)
    
    # Interaction breakdown
    like_sources = db.Column(db.JSON, default=dict)  # Organic vs paid, etc.
    comment_sentiment = db.Column(db.String(50))  # positive, neutral, negative
    top_countries = db.Column(db.JSON, default=dict)  # Top countries by engagement
    
    # Performance score (calculated)
    performance_score = db.Column(db.Float, default=0.0)  # 0-100
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<PostAnalytics post_id={self.post_id}>'
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate based on impressions"""
        if self.impressions > 0:
            total_engagement = self.likes + self.comments + self.shares
            self.engagement_rate = (total_engagement / self.impressions) * 100
        else:
            self.engagement_rate = 0.0
        return self.engagement_rate
    
    def calculate_performance_score(self):
        """Calculate overall performance score (0-100)"""
        # Weighted scoring
        like_weight = 0.4
        comment_weight = 0.35
        share_weight = 0.25
        
        base_score = (
            (self.likes / max(self.likes, 1)) * like_weight +
            (self.comments / max(self.comments, 1)) * comment_weight +
            (self.shares / max(self.shares, 1)) * share_weight
        )
        
        # Normalize to 0-100
        self.performance_score = min(base_score * 10, 100)
        return self.performance_score
