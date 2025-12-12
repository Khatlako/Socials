from app import db
from datetime import datetime

class Portfolio(db.Model):
    """Portfolio documents uploaded by users"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, docx, image, etc.
    file_size = db.Column(db.Integer)  # in bytes
    
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    # Processing status
    status = db.Column(db.String(50), default='uploaded', nullable=False)  # uploaded, processing, completed, failed
    extracted_text = db.Column(db.Text)  # Extracted content from document
    
    # AI Processing
    ai_posts_generated = db.Column(db.Integer, default=0)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Relationships
    posts = db.relationship('Post', backref='source_portfolio', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Portfolio {self.filename}>'
