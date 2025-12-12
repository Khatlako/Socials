# Facebook Business OAuth Setup Guide

## Prerequisites
1. Facebook Business Account
2. Facebook App ID and Secret
3. Your application's callback URL

## Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new app → Select "Consumer"
3. Choose "Facebook Login" as the product
4. Complete the setup wizard

## Step 2: Get App Credentials

1. Go to Settings → Basic
2. Copy your **App ID** and **App Secret**
3. Add to `.env`:
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

## Step 3: Configure OAuth Redirect URI

1. Go to Facebook Login → Settings
2. Add Redirect URIs:
   - Development: `http://localhost:5000/auth/facebook/callback`
   - Production: `https://yourdomain.com/auth/facebook/callback`

3. Update `.env`:
```
FACEBOOK_REDIRECT_URI=http://localhost:5000/auth/facebook/callback
```

## Step 4: Request Permissions

In your Facebook app settings, request these permissions:
- `email` - User email access
- `public_profile` - User profile info
- `pages_manage_posts` - Publish to pages
- `pages_read_engagement` - Read page insights

## Step 5: Enable Required Permissions in App Roles

1. Go to Settings → App Roles
2. Add your test user account
3. Assign "Tester" or "Developer" role

## Step 6: Test Login Flow

1. Run the application: `python run.py`
2. Click "Login with Facebook"
3. Authorize the app
4. Should redirect to dashboard

## Troubleshooting

### "Invalid OAuth Access Token"
- Check app is in development/live mode
- Verify app secret is correct
- Ensure callback URL matches exactly

### "App Not Set Up"
- Verify app is in development mode
- Check app settings in Facebook dashboard
- Ensure all required fields are filled

### "Redirect URI Mismatch"
- Check callback URL matches exactly (including http/https and port)
- Whitelist domain in app settings

## Using Facebook Graph API

Once authenticated, you can use the user's access token to:

### Publish a Post
```python
facebook_service.publish_post(
    page_id="123456",
    message="Your post content",
    access_token=user.access_token
)
```

### Schedule a Post
```python
facebook_service.schedule_post(
    page_id="123456",
    message="Your post",
    scheduled_time=datetime(2024, 1, 15, 10, 0),
    access_token=user.access_token
)
```

### Get Post Analytics
```python
analytics = facebook_service.get_post_analytics(
    post_id="123456_789",
    access_token=user.access_token
)
```

## For Production

1. Submit app for review
2. Change app mode to "Live"
3. Use production redirect URI
4. Implement token refresh mechanism
5. Add rate limiting
6. Log all API calls

## Reference
- [Facebook Login Docs](https://developers.facebook.com/docs/facebook-login)
- [Graph API Reference](https://developers.facebook.com/docs/graph-api)
- [OAuth 2.0](https://tools.ietf.org/html/rfc6749)
