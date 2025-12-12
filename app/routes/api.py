from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Media, Post, Portfolio
from app import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/media/list')
@login_required
def get_media():
    """Get media list"""
    media_type = request.args.get('type', 'all')
    
    query = Media.query.filter_by(user_id=current_user.id)
    
    if media_type in ['image', 'video']:
        query = query.filter_by(media_type=media_type)
    
    media = query.all()
    
    return jsonify([{
        'id': m.id,
        'filename': m.filename,
        'media_type': m.media_type,
        'title': m.title,
        'file_path': m.file_path,
        'thumbnail_path': m.thumbnail_path or m.file_path,
        'width': m.width,
        'height': m.height
    } for m in media])

@api_bp.route('/posts/<int:post_id>/preview')
@login_required
def get_post_preview(post_id):
    """Get post preview data"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    return jsonify({
        'id': post.id,
        'content': post.content,
        'hashtags': post.hashtags,
        'status': post.status,
        'media_count': len(list(post.media_items)),
        'created_at': post.created_at.isoformat()
    })
