# 🚀 Quick Start Guide

## Running the Application

### 1. Start the Server
```bash
cd /workspaces/Socials
source venv/bin/activate
python run.py
```

Server will be available at: `http://localhost:5000`

### 2. Test the Authentication Flow

1. **Go to**: http://localhost:5000/auth/login
2. **Click**: "Login with Facebook"
3. **Approve**: The permissions request
4. **Select**: A Facebook page you manage
5. **Done**: Redirected to dashboard

### 3. Create and Publish a Post

1. **In Dashboard**: Click "New Post"
2. **Type**: Your post content
3. **Click**: "Publish"
4. **Check**: Your Facebook page - post should appear!

## Key Information

### Page Access Token Stored
After selecting a page during login, your `page_access_token` is stored in the database. This token:
- ✅ Never expires
- ✅ Is page-specific
- ✅ Is used for all posts to that page
- ✅ Is secure (limited permissions only)

### Token Location
In database `users` table:
```
- page_access_token: Long-lived token for API calls
- selected_page_id: Which page you selected
- selected_page_name: Display name of page
- facebook_pages: List of all pages you can manage
```

### All Requests Use Page Token
- Publishing posts ✅
- Scheduling posts ✅
- Getting analytics ✅
- All use `page_access_token` (never expires)

## Environment Setup

Your `.env` file already contains:
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:5000/auth/facebook/callback
```

## Database

The SQLite database includes tables for:
- **users** - User accounts with page tokens
- **posts** - Posts created in the app
- **scheduled_posts** - Posts scheduled for future publish
- **post_analytics** - Analytics data for each post
- **media** - Uploaded images/videos
- **portfolios** - Portfolio documents

## File Structure

```
/workspaces/Socials/
├── app/
│   ├── models/
│   │   ├── user.py          ← User model with page_access_token
│   │   ├── post.py
│   │   └── ...
│   ├── services/
│   │   ├── facebook_service.py  ← All API methods use page_access_token
│   │   ├── post_service.py      ← Uses page_access_token for publishing
│   │   └── ...
│   ├── routes/
│   │   ├── auth.py          ← OAuth + page selection flow
│   │   ├── dashboard.py
│   │   └── ...
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── select_page.html  ← Page selection UI
│   │   ├── dashboard.html
│   │   └── ...
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/
├── instance/
│   └── app.db              ← SQLite database
├── .env                    ← Configuration (not in git)
├── run.py                  ← Entry point
├── config.py              ← App configuration
├── requirements.txt        ← Python dependencies
└── README.md              ← Full documentation
```

## Verification

Run the verification script to ensure everything is installed correctly:

```bash
python verify_token_architecture.py
```

Expected output:
```
✅ ALL TESTS PASSED - IMPLEMENTATION IS CORRECT
```

## Common Operations

### View a Post
1. In dashboard, click on any post
2. See published status and analytics
3. View on Facebook by clicking "View Post"

### Schedule a Post
1. Create a post
2. Click "Schedule"
3. Select future date/time
4. Post will publish automatically at that time

### Get Post Analytics
1. View a published post
2. See likes, comments, shares, reach, impressions
3. Data syncs from Facebook

### Switch Pages
1. Currently selected page shown in dashboard header
2. To change: Log out and log back in
3. Select different page in page selection screen
4. All future posts go to new page

## Troubleshooting

### Issue: "No Facebook page selected"
- Go back to login
- Complete page selection flow again

### Issue: Post won't publish
- Check that you've selected a page
- Verify Facebook login is valid
- Check browser console for errors (F12)

### Issue: Can't see your Facebook page in selection
- The account must have management access to the page
- Check Facebook Business Manager
- Try a different Facebook account that's an admin of a page

## Next Steps

1. **Test Publishing**
   - Create a draft post
   - Publish it
   - Verify it appears on your Facebook page

2. **Schedule Posts**
   - Create and schedule posts for future times
   - Let system publish them automatically

3. **Monitor Analytics**
   - Check performance of published posts
   - Track engagement metrics

4. **Production**
   - When ready, deploy to production server
   - Update FACEBOOK_REDIRECT_URI to production domain
   - Submit app for Meta review

## Support

### Documentation Files
- `IMPLEMENTATION_COMPLETE.md` - Full implementation details
- `PAGE_TOKEN_ARCHITECTURE.md` - Token architecture explained
- `README.md` - Full feature list

### Architecture
The app uses:
- **Framework**: Flask 3.0.0
- **Database**: SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Auth**: Facebook OAuth 2.0
- **API**: Facebook Graph API v18.0

### Key Files to Know
- `app/services/facebook_service.py` - All Facebook API calls
- `app/routes/auth.py` - Authentication flow
- `app/models/user.py` - Database schema
- `app/services/post_service.py` - Post operations

---

**Ready to test?** Open http://localhost:5000 in your browser!
