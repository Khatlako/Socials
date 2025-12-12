# 📱 Socials - Facebook Social Media Management Platform

A comprehensive, professional-grade web application for managing Facebook business posts, scheduling content, generating AI-powered posts, and tracking real-time engagement analytics.

## 🎯 Quick Overview

**What This App Does:**
- Authenticate with Facebook Business accounts using OAuth
- Create, edit, and manage social media posts
- Generate intelligent posts using AI (Claude)
- Upload and organize media files (images/videos)
- Schedule posts for future publishing
- Publish posts immediately to Facebook
- Track engagement metrics in real-time
- View analytics dashboards with trends

---

## ✨ Core Features Explained

### 1. 🔐 **Facebook Authentication (OAuth 2.0)**

**How it works:**
- Users click "Login with Facebook" button
- App redirects to Facebook's login page
- After approval, users return to the app with an access token
- The app stores the token securely in the database
- Users can manage multiple Facebook business accounts and pages

**What you get:**
- Secure, token-based authentication
- No password storage required
- Multiple business account support
- Token refresh capabilities for long-term access

**Where to find it:**
- Landing page → "Login with Facebook" button
- `/auth/login` route
- Required for: Everything else in the app

---

### 2. 📝 **Post Management System**

**How it works:**
The app uses a workflow-based system:

1. **Create Post**
   - Write content manually in the post editor
   - Add hashtags, captions, and emojis
   - Preview how the post will look on Facebook
   - Select images/videos from your media library
   - Save as "Pending" for review

2. **Edit Posts**
   - Modify pending posts before approval
   - Track edit history (number of edits, timestamps)
   - Preserve original content for comparison
   - Update hashtags and media attachments

3. **Approve/Reject Posts**
   - Review pending posts in the dashboard
   - Approve for publishing or reject with reason
   - Rejected posts stored with feedback

4. **Publish Immediately**
   - Send post to Facebook instantly
   - Post appears on your page immediately
   - Track Facebook post ID for analytics

5. **Schedule Posts**
   - Choose future date and time
   - Posts queue automatically
   - Background system publishes at scheduled time
   - Retry mechanism if publishing fails

**Post Status Flow:**
```
Pending → Approved → Posted (to Facebook)
   ↓
Pending → Rejected (with reason)
```

**Where to find it:**
- Dashboard → "Create Post" button
- `/posts/create` - Create new post
- `/posts/` - View all posts by status
- `/posts/<id>/edit` - Edit pending post
- `/posts/<id>/publish` - Publish immediately
- `/posts/<id>/schedule` - Schedule for later

---

### 3. 🤖 **AI Post Generation**

**How it works:**
- Upload business documents (PDF, Word, images, text)
- App extracts text using OCR and document parsing
- Claude AI analyzes the content
- AI generates 3 relevant, engaging post ideas automatically
- Review and refine generated posts before publishing

**Supported file types:**
- PDF documents
- Word documents (.docx)
- Images (text extraction via OCR)
- Plain text files

**Example workflow:**
1. Upload your company brochure (PDF)
2. App extracts: "Company founded in 2020, specializes in web design, won 5 awards"
3. AI generates posts like:
   - "Exciting news! We just celebrated our 5th anniversary with award recognition! 🎉"
   - "Our team's dedication to excellence has been recognized with industry awards. Proud moment! 🏆"
   - "Starting a journey in 2020, now recognized as leaders in web design. Thank you to our amazing clients!"

**Where to find it:**
- Dashboard → "Portfolio" or click "Portfolios" in sidebar
- `/portfolios/` - Upload and manage documents
- `/portfolios/<id>/generate-posts` - Generate AI posts from portfolio
- Generated posts appear in your Posts list

---

### 4. 🎨 **Media Library**

**How it works:**
- Upload images and videos to your media library
- Automatic thumbnail generation for images
- Metadata tracking (dimensions, duration, file size)
- Drag-and-drop upload interface
- Organize with titles, descriptions, and tags
- Select from library when creating posts

**Features:**
- Upload multiple files at once
- Auto-generated thumbnails (saved as separate files)
- Image metadata: width, height, file size
- Video metadata: duration (in seconds), file size
- Search and filter by tags
- Edit metadata without re-uploading

**Where to find it:**
- Click "Media" in sidebar
- `/media/` - View media library
- `/media/upload` - Upload new files
- `/media/<id>` - View media details
- Select media when creating posts

---

### 5. 📊 **Analytics Dashboard**

**How it works:**
1. Posts are published to Facebook with engagement tracking enabled
2. Real-time metrics are fetched from Facebook Graph API
3. Analytics are calculated and stored:
   - Likes, comments, shares
   - Impressions, reach, clicks
   - Engagement rate (engagement/impressions × 100)
   - Performance score (0-100)

4. Dashboard displays:
   - 7-day engagement trend chart
   - Top performing posts
   - Best times to post
   - Total engagement metrics

**Metrics tracked:**
- **Likes** - Number of reactions
- **Comments** - Direct feedback from audience
- **Shares** - How many people shared your content
- **Impressions** - Total times post was shown
- **Reach** - Unique people who saw it
- **Engagement Rate** - (Likes + Comments + Shares) / Impressions × 100
- **Performance Score** - Algorithmic rating 0-100

**Where to find it:**
- Dashboard → Analytics section
- `/analytics/` - Full analytics dashboard
- Individual post view → See that post's analytics

**Example dashboard view:**
```
Total Likes: 245
Total Comments: 18
Total Shares: 32
Average Engagement Rate: 3.2%

[Chart showing 7-day trend]
[Table of top 5 posts]
```

---

### 6. 📱 **Dashboard Overview**

**The main hub showing:**
- Quick stats cards (total posts, scheduled posts, pending review)
- 7-day engagement trend chart
- List of posts pending approval
- List of scheduled posts
- Quick action buttons
- Recent activity feed

**Where to find it:**
- `/dashboard/` - Main dashboard (after login)
- First page you see after authentication

---

### 7. 🛠️ **Post Preview**

**How it works:**
- While creating a post, see real-time Facebook preview
- Shows how post will appear on Facebook page
- See text, images, engagement buttons (Like, Comment, Share)
- Visual feedback before publishing

**Where to find it:**
- `/posts/create` - Right side of post creation form
- `/posts/<id>/edit` - Preview section

---

## 🔄 User Workflows

### **Workflow 1: Quick Post (Manual)**
```
1. Log in with Facebook
2. Dashboard → "Create Post"
3. Write post content
4. Select images from media library
5. Preview post
6. Click "Publish Now" → Goes live immediately
7. Check analytics dashboard to see engagement
```

### **Workflow 2: Scheduled Posting (Content Calendar)**
```
1. Dashboard → "Create Post"
2. Write content
3. Add images/videos
4. Click "Schedule"
5. Choose date and time
6. System publishes automatically at that time
7. You get notifications when posted
```

### **Workflow 3: AI-Powered Content Generation**
```
1. Click "Portfolios" → "Upload Portfolio"
2. Upload company brochure (PDF/Word)
3. Wait for text extraction
4. Click "Generate Posts"
5. Review 3 AI-suggested posts
6. Click "Use Post" for ones you like
7. Review in Pending Posts
8. Approve and publish or schedule
```

### **Workflow 4: Analytics & Optimization**
```
1. Create and publish several posts
2. Check Analytics dashboard
3. See which posts performed best
4. Check "Best Times" to post
5. Create similar posts at optimal times
6. Track improvement in engagement
```

---

## 🎮 Detailed Feature Breakdown

### **Authentication & Account Management**
| Feature | What it does |
|---------|-------------|
| Facebook OAuth Login | Securely connects your Facebook business account |
| Multiple Accounts | Manage different business accounts from one dashboard |
| Page Selection | Choose which Facebook page to post to |
| Token Management | Automatically refreshes access tokens |
| Session Management | Secure user sessions with Flask-Login |

### **Post Creation & Management**
| Feature | What it does |
|---------|-------------|
| Rich Text Editor | Write posts with formatting |
| Hashtag Support | Add up to 30 hashtags per post |
| Media Selection | Choose images/videos from library |
| Draft Saving | Auto-save drafts as you type |
| Status Workflow | Pending → Approved → Posted flow |
| Edit History | Track how many times a post was edited |
| Bulk Operations | Approve/reject multiple posts at once |

### **AI & Automation**
| Feature | What it does |
|---------|-------------|
| Document Upload | Import PDFs, Word docs, images |
| Text Extraction | OCR and document parsing |
| AI Generation | Claude generates 3 post ideas |
| Batch Generate | Create multiple posts from one document |
| Post Improvement | AI can enhance existing posts |
| Hashtag Suggestions | Auto-generate relevant hashtags |
| Caption Generation | Auto-create captions from images |

### **Media Management**
| Feature | What it does |
|---------|-------------|
| Drag & Drop Upload | Easy file uploads |
| Thumbnail Generation | Auto-create thumbnails for images |
| Metadata Tracking | Store file dimensions, duration, size |
| Media Organization | Tag and categorize media files |
| Reusable Library | Use same images in multiple posts |
| Media Preview | View before using in posts |

### **Scheduling & Publishing**
| Feature | What it does |
|---------|-------------|
| Instant Publish | Post goes live immediately |
| Schedule Posts | Set future date/time for posting |
| Automatic Publishing | Posts publish without manual action |
| Retry Mechanism | Retry failed publishes automatically |
| Publishing Queue | Manage multiple scheduled posts |
| Time Zone Support | Schedule for any time zone |

### **Analytics & Tracking**
| Feature | What it does |
|---------|-------------|
| Real-time Metrics | Pull engagement data from Facebook |
| Engagement Tracking | Likes, comments, shares, impressions |
| Performance Scoring | Algorithmic rating of post quality |
| Trend Analysis | See what's working over time |
| Top Posts | Identify your best performing content |
| Best Times | See when your audience is most active |
| Export Data | Get analytics in viewable format |

---

## 💾 Database Structure

The app stores everything in a SQLite database with 6 main tables:

**Users** - Facebook accounts
- Facebook ID, name, email, profile picture
- Access tokens for API calls
- Selected business account and page

**Portfolios** - Uploaded documents
- File path, type (PDF, Word, image)
- Extracted text content
- Processing status
- Number of AI posts generated

**Media** - Images and videos
- File path and type
- Thumbnails, dimensions, duration
- Tags, titles, descriptions
- Relationship to posts (many-to-many)

**Posts** - Social media content
- Post content, captions, hashtags
- Status (pending, approved, posted, rejected)
- AI confidence scores
- Facebook post ID and URL
- Edit history

**ScheduledPosts** - Queued content
- Post to be published
- Scheduled date/time
- Publishing status
- Retry count if failed

**PostAnalytics** - Engagement data
- Likes, comments, shares, clicks
- Impressions, reach
- Engagement rate, performance score
- Video-specific metrics
- Top countries, comment sentiment

---

## 🚀 How to Use

### **Getting Started**
1. Have Facebook Business Account ready
2. Run: `python run.py`
3. Visit: `http://127.0.0.1:5000`
4. Click "Login with Facebook"
5. Approve permissions

### **First Post**
1. Dashboard → "Create Post"
2. Write your message
3. (Optional) Add images from Media library
4. Click "Preview" to see Facebook preview
5. Click "Publish Now" or "Schedule"

### **Generate AI Posts**
1. Click "Portfolios"
2. Upload company document (PDF/Word)
3. Click "Generate Posts"
4. Review suggested posts
5. Click "Use" on posts you like
6. Approve and publish

### **Check Performance**
1. Click "Analytics"
2. See engagement metrics
3. View top performing posts
4. Check best times to post
5. Adjust strategy based on data

---

## 🔧 Technical Details

**Backend:**
- Flask 3.0.0 (Python web framework)
- SQLAlchemy 3.1.1 (Database ORM)
- Facebook Graph API v18.0 (Publishing & analytics)
- Claude AI API (Post generation)

**Frontend:**
- Bootstrap 5.3.0 (Responsive design)
- Chart.js 3.9.1 (Analytics charts)
- jQuery (Interactivity)
- Jinja2 templating (Dynamic pages)

**Database:**
- SQLite (Development)
- PostgreSQL (Production)

**Security:**
- OAuth 2.0 authentication
- Secure token storage
- CSRF protection on forms
- Session management
- Input validation

---

## 📋 Feature Checklist

✅ Facebook OAuth Login
✅ Multiple account support
✅ Create/Edit/Delete posts
✅ Post approval workflow
✅ Instant publishing to Facebook
✅ Schedule posts for future
✅ AI post generation from documents
✅ Media library with upload
✅ Real-time analytics
✅ Performance tracking
✅ Engagement metrics
✅ Dashboard overview
✅ Responsive mobile design
✅ Professional UI/UX
✅ Database with relationships
✅ API endpoints for AJAX
✅ Error handling
✅ Flash messages

---

## 🎨 User Interface

The app features a modern, professional design with:
- **Responsive Navigation** - Works on desktop and mobile
- **Clean Dashboard** - See stats at a glance
- **Intuitive Forms** - Easy post creation
- **Live Previews** - See posts before publishing
- **Analytics Charts** - Visual engagement data
- **Modal Dialogs** - Quick actions without page load
- **Toast Notifications** - Real-time feedback
- **Sidebar Navigation** - Quick access to features
- **Color-coded Badges** - Status indicators
- **Gradient Theme** - Professional purple/blue design

---

## 📊 Metrics You Can Track

Per post:
- Likes gained
- Comments received
- Shares
- Impressions (how many saw it)
- Reach (unique people)
- Clicks on the post
- Engagement rate %
- Performance score (0-100)

Across all posts:
- Total engagement trend (7-day chart)
- Best performing posts
- Worst performing posts
- Best times to post
- Audience growth
- Content type performance

---

## ✅ What You Can Do Now

1. **Create unlimited posts** - Write, edit, schedule, publish
2. **AI generation** - Upload docs, get post ideas automatically
3. **Manage media** - Upload, organize, reuse images/videos
4. **Schedule content** - Plan posts for specific dates/times
5. **Track analytics** - See what's working, optimize
6. **Multiple accounts** - Manage different businesses
7. **Approve workflow** - Review before publishing
8. **Mobile friendly** - Use on phone or tablet
9. **Professional look** - Modern, clean interface
10. **Secure authentication** - Safe Facebook integration

---

## 🔗 Key Routes

| Route | Purpose |
|-------|---------|
| `/` | Root - redirects to home |
| `/auth/login` | Facebook login |
| `/auth/facebook/callback` | OAuth callback |
| `/dashboard/` | Main dashboard |
| `/posts/create` | Create new post |
| `/posts/` | All posts |
| `/posts/<id>/publish` | Publish immediately |
| `/posts/<id>/schedule` | Schedule post |
| `/media/` | Media library |
| `/media/upload` | Upload media |
| `/portfolios/` | Portfolio documents |
| `/portfolios/<id>/generate-posts` | AI generation |
| `/analytics/` | Analytics dashboard |

---

## 💡 Use Cases

**Social Media Manager:**
- Manage multiple brand accounts
- Schedule content calendar
- Track engagement trends
- Generate ideas with AI

**Small Business:**
- Post daily updates
- Schedule in advance
- Monitor engagement
- Grow audience

**Marketing Agency:**
- Manage client accounts
- Bulk scheduling
- Performance reports
- Content generation

**Content Creator:**
- AI post generation
- Schedule posting calendar
- Analytics insights
- Professional workflow

---

## 🎯 Is This What You Needed?

**You wanted:**
✅ Upload portfolios → AI generates posts
✅ Create and manage posts
✅ Schedule and publish posts
✅ Track engagement
✅ Professional UI/UX
✅ Facebook business integration
✅ Media management
✅ Analytics dashboard

**This app provides:** All of the above and more!

Need to adjust anything? Let me know what features you'd like to add or modify.
