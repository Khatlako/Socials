import anthropic
import json
from flask import current_app

class AIService:
    """Handle AI content generation for posts"""
    
    def __init__(self):
        self.client = anthropic.Anthropic()
    
    def generate_posts_from_portfolio(self, portfolio_text, num_posts=3):
        """Generate social media posts from portfolio content"""
        try:
            prompt = f"""
            You are a professional social media content creator. Based on the following business portfolio content, 
            generate {num_posts} engaging, unique Facebook posts that would appeal to business customers.
            
            Make them:
            - Professional yet conversational
            - Between 100-250 characters
            - Include relevant hashtags
            - Highlight key benefits or features
            - Be unique from each other
            
            Format as JSON array with 'content' and 'hashtags' fields.
            
            Portfolio Content:
            {portfolio_text[:2000]}  # Limit to first 2000 chars
            """
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Try to extract JSON
            try:
                # Look for JSON array in response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    posts = json.loads(json_str)
                    return posts
            except:
                pass
            
            # Fallback: return raw text as posts
            return [{"content": response_text, "hashtags": "#socialmedia"}]
            
        except Exception as e:
            raise Exception(f'Error generating posts: {str(e)}')
    
    def improve_post(self, post_content):
        """Improve or enhance existing post content"""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Please improve this Facebook post to make it more engaging and professional:
                        
                        Original: {post_content}
                        
                        Provide improved version only, no explanations.
                        """
                    }
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            raise Exception(f'Error improving post: {str(e)}')
    
    def suggest_hashtags(self, post_content):
        """Suggest hashtags for a post"""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Suggest 5-8 relevant hashtags for this post:
                        {post_content}
                        
                        Return as comma-separated list only.
                        """
                    }
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            raise Exception(f'Error suggesting hashtags: {str(e)}')
    
    def generate_auto_caption(self, image_description):
        """Generate auto-caption for an image"""
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Generate a short, engaging caption (max 100 chars) for this image:
                        {image_description}
                        
                        Return caption only.
                        """
                    }
                ]
            )
            
            return message.content[0].text.strip()
        except Exception as e:
            raise Exception(f'Error generating caption: {str(e)}')

ai_service = AIService()
