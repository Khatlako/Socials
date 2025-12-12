import requests
from requests_oauthlib import OAuth2Session
import json
from datetime import datetime, timedelta
from flask import current_app

class FacebookService:
    """Handle Facebook OAuth and Graph API operations"""
    
    FACEBOOK_AUTH_URL = 'https://www.facebook.com/v18.0/dialog/oauth'
    FACEBOOK_TOKEN_URL = 'https://graph.facebook.com/v18.0/oauth/access_token'
    FACEBOOK_GRAPH_API = 'https://graph.facebook.com/v18.0'
    
    def __init__(self):
        pass
    
    def get_oauth_session(self, redirect_uri=None):
        """Create OAuth2 session for Facebook"""
        if redirect_uri is None:
            redirect_uri = current_app.config['FACEBOOK_REDIRECT_URI']
        
        return OAuth2Session(
            client_id=current_app.config['FACEBOOK_APP_ID'],
            redirect_uri=redirect_uri,
            scope=['email', 'public_profile', 'pages_manage_posts', 'pages_read_engagement'],
            state='random_state_string'  # Use secure random state in production
        )
    
    def get_authorization_url(self):
        """Get Facebook authorization URL"""
        facebook = self.get_oauth_session()
        authorization_url, state = facebook.authorization_url(
            self.FACEBOOK_AUTH_URL
        )
        return authorization_url, state
    
    def exchange_code_for_token(self, code, redirect_uri=None):
        """Exchange authorization code for access token"""
        if redirect_uri is None:
            redirect_uri = current_app.config['FACEBOOK_REDIRECT_URI']
        
        try:
            response = requests.post(
                self.FACEBOOK_TOKEN_URL,
                data={
                    'client_id': current_app.config['FACEBOOK_APP_ID'],
                    'client_secret': current_app.config['FACEBOOK_APP_SECRET'],
                    'redirect_uri': redirect_uri,
                    'code': code
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to exchange code for token: {str(e)}')
    
    def get_user_info(self, access_token):
        """Get Facebook user information"""
        try:
            response = requests.get(
                f'{self.FACEBOOK_GRAPH_API}/me',
                params={
                    'fields': 'id,email,name,picture',
                    'access_token': access_token
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to get user info: {str(e)}')
    
    def get_user_pages(self, access_token):
        """Get pages the user manages (with page access tokens)"""
        try:
            response = requests.get(
                f'{self.FACEBOOK_GRAPH_API}/me/accounts',
                params={
                    'fields': 'id,name,picture,access_token',
                    'access_token': access_token,
                    'limit': 100
                }
            )
            response.raise_for_status()
            pages = response.json().get('data', [])
            return pages
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to get user pages: {str(e)}')
    
    def get_business_accounts(self, access_token):
        """Get user's business accounts"""
        try:
            response = requests.get(
                f'{self.FACEBOOK_GRAPH_API}/me/businesses',
                params={
                    'fields': 'id,name,picture',
                    'access_token': access_token
                }
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to get business accounts: {str(e)}')
    
    def get_page_access_token(self, page_id, access_token):
        """
        Get page access token for a specific page (long-lived).
        This is the critical method for long-term access.
        """
        try:
            # The page access token is returned with /me/accounts
            # So we fetch it directly from there
            response = requests.get(
                f'{self.FACEBOOK_GRAPH_API}/me/accounts',
                params={
                    'fields': 'id,name,access_token',
                    'access_token': access_token,
                    'limit': 100
                }
            )
            response.raise_for_status()
            pages = response.json().get('data', [])
            
            # Find the page with matching ID
            for page in pages:
                if page.get('id') == page_id:
                    return page.get('access_token')
            
            raise Exception(f'Page {page_id} not found in user accounts')
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to get page access token: {str(e)}')
    
    def get_pages(self, business_account_id, access_token):
        """Get pages for a business account"""
        try:
            response = requests.get(
                f'{self.FACEBOOK_GRAPH_API}/{business_account_id}/pages',
                params={
                    'fields': 'id,name,picture',
                    'access_token': access_token
                }
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to get pages: {str(e)}')
    
    def publish_post(self, page_id, message, page_access_token, image_url=None):
        """
        Publish a post to Facebook page using PAGE ACCESS TOKEN (long-lived).
        This token never expires and is specific to the page.
        """
        try:
            data = {
                'message': message,
                'access_token': page_access_token
            }
            
            if image_url:
                data['url'] = image_url
            
            response = requests.post(
                f'{self.FACEBOOK_GRAPH_API}/{page_id}/feed',
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to publish post: {str(e)}')
    
    def schedule_post(self, page_id, message, scheduled_time, page_access_token, image_url=None):
        """
        Schedule a post for future publishing using PAGE ACCESS TOKEN (long-lived).
        """
        try:
            data = {
                'message': message,
                'scheduled_publish_time': int(scheduled_time.timestamp()),
                'access_token': page_access_token
            }
            
            if image_url:
                data['url'] = image_url
            
            response = requests.post(
                f'{self.FACEBOOK_GRAPH_API}/{page_id}/feed',
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to schedule post: {str(e)}')
    
    def get_post_analytics(self, post_id, page_access_token):
        """
        Get analytics for a posted item using PAGE ACCESS TOKEN.
        """
        try:
            response = requests.get(
                f'{self.FACEBOOK_GRAPH_API}/{post_id}',
                params={
                    'fields': 'shares,likes.summary(true),comments.summary(true),type,status_type,message',
                    'access_token': page_access_token
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f'Failed to get post analytics: {str(e)}')

facebook_service = FacebookService()
