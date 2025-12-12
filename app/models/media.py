from app import db
from datetime import datetime

class Media(db.Model):
    """Media library for images and videos"""
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)  # image, video
    file_extension = db.Column(db.String(10))
    file_size = db.Column(db.Integer)  # in bytes
    
    # Media metadata
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Thumbnail for images/videos
    thumbnail_path = db.Column(db.String(500))
    
    # Media info
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration = db.Column(db.Float)  # Duration in seconds for videos
    
    # Relationships - Many-to-Many through post_media table
    posts = db.relationship('Post', secondary='post_media', backref=db.backref('media_items', lazy='dynamic'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Media {self.filename}>'


# Association table for Post-Media relationship
post_media = db.Table('post_media',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('media_id', db.Integer, db.ForeignKey('media.id'), primary_key=True),
    db.Column('order', db.Integer, default=0)  # Order in which media appears in post
)
