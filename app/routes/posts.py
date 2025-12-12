from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Post, Media, ScheduledPost, PostAnalytics
from app import db
from app.services.post_service import post_service
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/')
@login_required
def index():
    """View all posts"""
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Post.query.filter_by(user_id=current_user.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=12)
    
    return render_template('posts/index.html', posts=posts, status=status)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new post"""
    if request.method == 'POST':
        content = request.form.get('content')
        post_type = request.form.get('post_type', 'manual')
        media_ids = request.form.getlist('media_ids[]')
        hashtags = request.form.get('hashtags')
        
        if not content or len(content.strip()) == 0:
            return jsonify({'success': False, 'error': 'Post content is required'}), 400
        
        try:
            post = post_service.create_post(current_user, content, post_type, media_ids, hashtags)
            flash(f'Post created and added to pending queue', 'success')
            return redirect(url_for('posts.view', post_id=post.id))
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    # Get available media
    media = Media.query.filter_by(user_id=current_user.id).all()
    
    return render_template('posts/create.html', media=media)

@posts_bp.route('/<int:post_id>')
@login_required
def view(post_id):
    """View single post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    # Get analytics if available
    analytics = PostAnalytics.query.filter_by(post_id=post_id).first()
    
    # Get related media
    media = post.media_items
    
    return render_template('posts/view.html', post=post, analytics=analytics, media=media)

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    """Edit post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    # Can only edit pending or approved posts
    if post.status not in ['pending', 'approved']:
        flash('Cannot edit posted or rejected content', 'warning')
        return redirect(url_for('posts.view', post_id=post_id))
    
    if request.method == 'POST':
        content = request.form.get('content')
        hashtags = request.form.get('hashtags')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        try:
            post_service.edit_post(post, content, hashtags, current_user)
            flash('Post updated', 'success')
            return redirect(url_for('posts.view', post_id=post_id))
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    media = Media.query.filter_by(user_id=current_user.id).all()
    
    return render_template('posts/edit.html', post=post, media=media)

@posts_bp.route('/<int:post_id>/approve', methods=['POST'])
@login_required
def approve(post_id):
    """Approve post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    if post.status != 'pending':
        return jsonify({'success': False, 'error': 'Only pending posts can be approved'}), 400
    
    try:
        post_service.approve_post(post, current_user)
        flash('Post approved!', 'success')
        return jsonify({'success': True, 'message': 'Post approved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@posts_bp.route('/<int:post_id>/publish', methods=['POST'])
@login_required
def publish(post_id):
    """Publish post immediately to Facebook"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    if post.status not in ['pending', 'approved']:
        return jsonify({'success': False, 'error': 'Cannot publish this post'}), 400
    
    try:
        post_service.publish_post(post, current_user)
        flash('Post published to Facebook!', 'success')
        return jsonify({'success': True, 'message': 'Post published'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@posts_bp.route('/<int:post_id>/schedule', methods=['POST'])
@login_required
def schedule(post_id):
    """Schedule post for future publishing"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    scheduled_time_str = request.json.get('scheduled_time')
    
    if not scheduled_time_str:
        return jsonify({'success': False, 'error': 'Scheduled time is required'}), 400
    
    try:
        scheduled_time = datetime.fromisoformat(scheduled_time_str)
        
        # Validate time is in future
        if scheduled_time <= datetime.utcnow():
            return jsonify({'success': False, 'error': 'Scheduled time must be in the future'}), 400
        
        # Create scheduled post
        scheduled = ScheduledPost(
            user_id=current_user.id,
            post_id=post.id,
            scheduled_at=scheduled_time
        )
        
        post.status = 'approved'  # Auto-approve when scheduling
        db.session.add(scheduled)
        db.session.commit()
        
        flash(f'Post scheduled for {scheduled_time.strftime("%Y-%m-%d %H:%M")}', 'success')
        return jsonify({'success': True, 'message': 'Post scheduled'})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid datetime format'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@posts_bp.route('/<int:post_id>/reject', methods=['POST'])
@login_required
def reject(post_id):
    """Reject post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    reason = request.json.get('reason', '')
    
    try:
        post_service.reject_post(post, reason)
        flash('Post rejected', 'info')
        return jsonify({'success': True, 'message': 'Post rejected'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    """Delete post"""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    if post.status == 'posted':
        return jsonify({'success': False, 'error': 'Cannot delete published posts'}), 400
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', 'info')
        return jsonify({'success': True, 'message': 'Post deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
