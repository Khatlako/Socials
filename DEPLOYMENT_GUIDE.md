# Deploying Socials to Production

## Pre-Deployment Checklist

- [ ] Update all environment variables
- [ ] Configure database (PostgreSQL recommended)
- [ ] Generate secure SECRET_KEY
- [ ] Enable HTTPS only
- [ ] Configure email notifications
- [ ] Set up logging
- [ ] Enable rate limiting
- [ ] Configure backup strategy

## Environment Setup

Create `.env.production`:
```bash
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/socials

# Security
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Facebook OAuth
FACEBOOK_APP_ID=your_production_app_id
FACEBOOK_APP_SECRET=your_production_app_secret
FACEBOOK_REDIRECT_URI=https://yourdomain.com/auth/facebook/callback

# AI
ANTHROPIC_API_KEY=your_api_key

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

## Database Setup (PostgreSQL)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb socials
sudo -u postgres createuser socials_user
sudo -u postgres psql -c "ALTER USER socials_user WITH PASSWORD 'strong_password';"
sudo -u postgres psql -c "ALTER ROLE socials_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE socials_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE socials_user SET default_transaction_deferrable TO on;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE socials TO socials_user;"
```

## Installation on Server

```bash
# Clone repository
git clone <repo-url> /var/www/socials
cd /var/www/socials

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads
chmod 755 uploads

# Initialize database
python << EOF
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
EOF
```

## Gunicorn Setup (WSGI Server)

Install gunicorn:
```bash
pip install gunicorn
```

Create `/etc/systemd/system/socials.service`:
```ini
[Unit]
Description=Socials Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/socials
Environment="PATH=/var/www/socials/venv/bin"
ExecStart=/var/www/socials/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --access-logfile /var/log/socials/access.log \
    --error-logfile /var/log/socials/error.log \
    run:app

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable socials
sudo systemctl start socials
sudo systemctl status socials
```

## Nginx Configuration

Create `/etc/nginx/sites-available/socials`:
```nginx
upstream socials_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    location / {
        proxy_pass http://socials_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/socials/app/static/;
        expires 30d;
    }

    location /uploads/ {
        alias /var/www/socials/uploads/;
        expires 7d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/socials /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

Auto-renewal:
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Monitoring

Install Supervisor for process management:
```bash
sudo apt-get install supervisor
```

Create `/etc/supervisor/conf.d/socials.conf`:
```ini
[program:socials]
command=/var/www/socials/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
directory=/var/www/socials
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/socials/gunicorn.log
stderr_logfile=/var/log/socials/error.log
```

## Backup Strategy

Daily database backup:
```bash
#!/bin/bash
# /usr/local/bin/backup-socials.sh
BACKUP_DIR="/var/backups/socials"
mkdir -p $BACKUP_DIR
pg_dump socials | gzip > $BACKUP_DIR/socials_$(date +%Y%m%d_%H%M%S).sql.gz
# Keep last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /usr/local/bin/backup-socials.sh
```

## Monitoring & Logging

Configure application logging in production:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/socials.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Socials startup')
```

## Performance Optimization

1. **Enable Caching**
   - Cache static assets (CSS, JS, images)
   - Use Redis for session storage

2. **Database Optimization**
   - Create indexes on frequently queried columns
   - Use connection pooling
   - Monitor slow queries

3. **CDN Integration**
   - Serve static files from CDN
   - Cache images globally

4. **Compression**
   - Enable gzip compression in Nginx
   - Minify CSS/JS

## Security Hardening

1. Configure security headers in Nginx
2. Enable CORS if needed
3. Implement rate limiting
4. Regular security updates
5. Monitor error logs
6. Use Web Application Firewall (WAF)

## Health Check

```bash
# Test application
curl -I https://yourdomain.com
curl -I https://yourdomain.com/dashboard
```

Monitor application:
```bash
sudo journalctl -u socials -f
tail -f /var/log/socials/access.log
tail -f /var/log/socials/error.log
```

## Troubleshooting

### 502 Bad Gateway
- Check if Gunicorn is running: `sudo systemctl status socials`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Increase Gunicorn timeout

### Database Connection Error
- Check PostgreSQL is running
- Verify DATABASE_URL
- Check database permissions

### Out of Memory
- Increase server RAM
- Optimize queries
- Reduce worker count in Gunicorn
