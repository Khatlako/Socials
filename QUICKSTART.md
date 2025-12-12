# 🚀 Quick Start Guide

## Installation (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your Facebook app credentials
```

**Required in .env:**
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
SECRET_KEY=your_secret_key_here
ANTHROPIC_API_KEY=your_claude_api_key
```

### 3. Create Database
```bash
python run.py
# Wait for the database to initialize
# Ctrl+C to stop
```

### 4. Start Server
```bash
python run.py
```

Visit: **http://localhost:5000**

---

## 📋 Getting Facebook Credentials

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new app → Select "Consumer"
3. Choose "Facebook Login"
4. Go to Settings → Basic
5. Copy **App ID** and **App Secret**
6. Add OAuth Redirect URI: `http://localhost:5000/auth/facebook/callback`

See [FACEBOOK_OAUTH_SETUP.md](FACEBOOK_OAUTH_SETUP.md) for detailed instructions.

---

## 🎯 Getting Claude API Key

1. Go to [Anthropic Console](https://console.anthropic.com)
2. Create API key
3. Add to .env: `ANTHROPIC_API_KEY=your_key`

---

## 📱 Main Features

### Dashboard
- Overview of all posts and metrics
- Quick stats on pending, scheduled, and posted content
- Engagement metrics at a glance

### Posts Management
- Create posts manually or from AI
- Draft, review, approve workflow
- Instant publish or schedule for later
- Edit posts before publishing

### Portfolio Upload
- Upload PDF, Word docs, images
- AI automatically extracts content
- Generate multiple posts automatically
- Track processed documents

### Media Library
- Drag-and-drop upload
- Organize images and videos
- Use in multiple posts
- Auto-generated thumbnails

### Scheduling
- Set specific date and time
- Automatic publishing via Facebook
- Timezone support
- View upcoming posts

### Analytics
- Track engagement metrics
- See top-performing posts
- Analyze trends over time
- Identify best posting times

---

## 💡 Workflow Example

1. **Login** → Facebook Business account
2. **Upload** → Portfolio (PDF/DOCX with business info)
3. **Generate** → Click "Generate Posts" → AI creates 3 posts
4. **Review** → Check pending posts, edit if needed
5. **Approve** → Click "Approve" to add to queue
6. **Schedule** → Set date/time for publishing
7. **Monitor** → Track engagement on dashboard

---

## 🔒 Security Notes

- Never commit `.env` to version control
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Keep dependencies updated
- Use PostgreSQL for production (not SQLite)

---

## 📊 File Structure

```
Socials/
├── app/
│   ├── models/           # Database models
│   ├── routes/           # URL routes and controllers
│   ├── services/         # Business logic
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── uploads/              # User uploads
├── run.py                # Entry point
├── config.py             # Configuration
├── requirements.txt      # Dependencies
└── .env.example          # Environment template
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Facebook login not working"
- Check FACEBOOK_APP_ID and SECRET in .env
- Verify callback URI in Facebook app settings
- Ensure app is in development mode

### "Database locked" (SQLite)
- SQLite has limitations
- Use PostgreSQL for production
- Close other connections to database

### "AI posts not generating"
- Check ANTHROPIC_API_KEY is set
- Verify API key is active
- Check portfolio has extracted text

---

## 📖 Documentation

- [Facebook OAuth Setup](FACEBOOK_OAUTH_SETUP.md) - Detailed Facebook integration
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production setup
- [README.md](README.md) - Full documentation

---

## 🤝 Support

For issues, check the logs:
```bash
tail -f *.log
```

---

**Happy posting! 🚀**
