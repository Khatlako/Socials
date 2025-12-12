from app.services.facebook_service import facebook_service
from app.models import Post, PostAnalytics
from app import db
from datetime import datetime

class PostService:
    """Handle post operations"""
    
    @staticmethod
    def create_post(user, content, post_type='manual', media_ids=None, hashtags=None):
        """Create a new post"""
        post = Post(
            user_id=user.id,
            content=content,
            post_type=post_type,
            hashtags=hashtags,
            original_content=content
        )
        
        if media_ids:
            from app.models import Media
            media = Media.query.filter(Media.id.in_(media_ids), Media.user_id == user.id).all()
            for m in media:
                post.media_items.append(m)
        
        db.session.add(post)
        db.session.commit()
        
        return post
    
    @staticmethod
    def approve_post(post, user):
        """Approve a post for publishing"""
        post.mark_as_approved(user)
        return post
    
    @staticmethod
    def publish_post(post, user):
        """Publish post to Facebook immediately using PAGE ACCESS TOKEN"""
        try:
            # Get user's selected page
            page_id = user.selected_page_id
            page_token = user.page_access_token
            
            if not page_id:
                raise Exception('No Facebook page selected. Please select a page.')
            
            if not page_token:
                raise Exception('No page access token available. Please re-authenticate.')
            
            # Publish via Facebook API using PAGE ACCESS TOKEN (long-lived)
            result = facebook_service.publish_post(
                page_id,
                post.content,
                page_token,  # Use page token instead of user token!
                image_url=post.preview_url if post.preview_url else None
            )
            
            # Update post with Facebook info
            post.mark_as_posted(
                result.get('id'),
                f"https://facebook.com/{result.get('id')}"
            )
            
            # Create analytics record
            analytics = PostAnalytics(
                user_id=user.id,
                post_id=post.id
            )
            db.session.add(analytics)
            db.session.commit()
            
            return post
        except Exception as e:
            raise Exception(f'Failed to publish post: {str(e)}')
    
    @staticmethod
    def reject_post(post, reason=None):
        """Reject a post"""
        post.status = 'rejected'
        post.rejection_reason = reason
        db.session.commit()
        return post
    
    @staticmethod
    def edit_post(post, content, hashtags=None, user=None):
        """Edit an existing post"""
        post.content = content
        if hashtags:
            post.hashtags = hashtags
        post.last_edited_at = datetime.utcnow()
        post.edit_count += 1
        if user:
            post.updated_at = datetime.utcnow()
        db.session.commit()
        return post

post_service = PostService()
