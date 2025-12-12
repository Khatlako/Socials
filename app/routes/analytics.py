from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Post, PostAnalytics, ScheduledPost
from app import db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    """Analytics dashboard"""
    # Get all posts with analytics
    posts_with_analytics = db.session.query(Post, PostAnalytics).outerjoin(
        PostAnalytics, Post.id == PostAnalytics.post_id
    ).filter(Post.user_id == current_user.id, Post.status == 'posted').all()
    
    # Calculate overall stats
    total_engagement = {
        'likes': 0,
        'comments': 0,
        'shares': 0,
        'reaches': 0
    }
    
    top_posts = []
    
    for post, analytics in posts_with_analytics:
        if analytics:
            total_engagement['likes'] += analytics.likes or 0
            total_engagement['comments'] += analytics.comments or 0
            total_engagement['shares'] += analytics.shares or 0
            total_engagement['reaches'] += analytics.reach or 0
            
            top_posts.append({
                'post': post,
                'analytics': analytics,
                'total_engagement': (analytics.likes or 0) + (analytics.comments or 0) + (analytics.shares or 0)
            })
    
    # Sort by engagement
    top_posts.sort(key=lambda x: x['total_engagement'], reverse=True)
    top_posts = top_posts[:10]
    
    # Get weekly stats
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    weekly_posts = Post.query.filter(
        Post.user_id == current_user.id,
        Post.status == 'posted',
        Post.posted_at >= seven_days_ago
    ).count()
    
    # Get engagement trend
    daily_stats = db.session.query(
        db.func.date(PostAnalytics.updated_at).label('date'),
        db.func.sum(PostAnalytics.likes).label('likes'),
        db.func.sum(PostAnalytics.comments).label('comments'),
        db.func.sum(PostAnalytics.shares).label('shares')
    ).filter(
        PostAnalytics.user_id == current_user.id,
        PostAnalytics.updated_at >= seven_days_ago
    ).group_by(db.func.date(PostAnalytics.updated_at)).all()
    
    engagement_trend = {
        'dates': [str(stat[0]) for stat in daily_stats],
        'likes': [stat[1] or 0 for stat in daily_stats],
        'comments': [stat[2] or 0 for stat in daily_stats],
        'shares': [stat[3] or 0 for stat in daily_stats]
    }
    
    return render_template('analytics/index.html',
                          total_engagement=total_engagement,
                          top_posts=top_posts,
                          weekly_posts=weekly_posts,
                          engagement_trend=engagement_trend)

@analytics_bp.route('/api/performance')
@login_required
def get_performance():
    """Get performance metrics as JSON"""
    # Best performing posts
    best_posts = db.session.query(
        Post.id,
        Post.content,
        PostAnalytics.likes,
        PostAnalytics.comments,
        PostAnalytics.shares
    ).join(PostAnalytics, Post.id == PostAnalytics.post_id).filter(
        Post.user_id == current_user.id
    ).order_by((PostAnalytics.likes + PostAnalytics.comments + PostAnalytics.shares).desc()).limit(5).all()
    
    # Best posting times
    posting_time_stats = db.session.query(
        db.func.hour(Post.posted_at).label('hour'),
        db.func.avg(PostAnalytics.likes + PostAnalytics.comments + PostAnalytics.shares).label('avg_engagement')
    ).join(PostAnalytics, Post.id == PostAnalytics.post_id).filter(
        Post.user_id == current_user.id
    ).group_by(db.func.hour(Post.posted_at)).all()
    
    return jsonify({
        'best_posts': [{
            'id': p[0],
            'content': p[1][:100],
            'likes': p[2] or 0,
            'comments': p[3] or 0,
            'shares': p[4] or 0
        } for p in best_posts],
        'best_hours': [{
            'hour': h,
            'avg_engagement': float(e or 0)
        } for h, e in posting_time_stats]
    })
