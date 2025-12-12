from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Post, ScheduledPost, PostAnalytics, Media, Portfolio
from app import db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard"""
    # Get dashboard statistics
    total_posts = Post.query.filter_by(user_id=current_user.id).count()
    pending_posts = Post.query.filter_by(user_id=current_user.id, status='pending').count()
    approved_posts = Post.query.filter_by(user_id=current_user.id, status='approved').count()
    posted_posts = Post.query.filter_by(user_id=current_user.id, status='posted').count()
    
    scheduled_posts = ScheduledPost.query.filter_by(user_id=current_user.id, publish_status='scheduled').count()
    
    # Get total engagement
    total_analytics = db.session.query(db.func.sum(PostAnalytics.likes),
                                       db.func.sum(PostAnalytics.comments),
                                       db.func.sum(PostAnalytics.shares)).filter(
                                       PostAnalytics.user_id == current_user.id).first()
    
    total_likes = total_analytics[0] or 0
    total_comments = total_analytics[1] or 0
    total_shares = total_analytics[2] or 0
    
    # Recent posts
    recent_posts = Post.query.filter_by(user_id=current_user.id).order_by(
        Post.created_at.desc()).limit(5).all()
    
    # Pending posts for review
    pending = Post.query.filter_by(user_id=current_user.id, status='pending').order_by(
        Post.created_at.desc()).limit(5).all()
    
    # Upcoming scheduled posts
    upcoming_scheduled = ScheduledPost.query.filter(
        ScheduledPost.user_id == current_user.id,
        ScheduledPost.publish_status == 'scheduled',
        ScheduledPost.scheduled_at > datetime.utcnow()
    ).order_by(ScheduledPost.scheduled_at).limit(5).all()
    
    # Get engagement trend (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.session.query(
        db.func.date(PostAnalytics.updated_at).label('date'),
        db.func.sum(PostAnalytics.likes).label('likes'),
        db.func.sum(PostAnalytics.comments).label('comments')
    ).filter(
        PostAnalytics.user_id == current_user.id,
        PostAnalytics.updated_at >= seven_days_ago
    ).group_by(db.func.date(PostAnalytics.updated_at)).all()
    
    engagement_data = {
        'dates': [str(stat[0]) for stat in daily_stats],
        'likes': [stat[1] or 0 for stat in daily_stats],
        'comments': [stat[2] or 0 for stat in daily_stats]
    }
    
    # Media library count
    media_count = Media.query.filter_by(user_id=current_user.id).count()
    
    # Portfolio count
    portfolio_count = Portfolio.query.filter_by(user_id=current_user.id).count()
    
    stats = {
        'total_posts': total_posts,
        'pending_posts': pending_posts,
        'approved_posts': approved_posts,
        'posted_posts': posted_posts,
        'scheduled_posts': scheduled_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_shares': total_shares,
        'media_count': media_count,
        'portfolio_count': portfolio_count
    }
    
    return render_template('dashboard/index.html',
                          stats=stats,
                          recent_posts=recent_posts,
                          pending_posts=pending,
                          upcoming_scheduled=upcoming_scheduled,
                          engagement_data=engagement_data)

@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    """Get dashboard stats as JSON"""
    total_posts = Post.query.filter_by(user_id=current_user.id).count()
    pending = Post.query.filter_by(user_id=current_user.id, status='pending').count()
    approved = Post.query.filter_by(user_id=current_user.id, status='approved').count()
    posted = Post.query.filter_by(user_id=current_user.id, status='posted').count()
    scheduled = ScheduledPost.query.filter_by(user_id=current_user.id, publish_status='scheduled').count()
    
    return jsonify({
        'total_posts': total_posts,
        'pending': pending,
        'approved': approved,
        'posted': posted,
        'scheduled': scheduled
    })
