# Deployment Guide

This guide covers deploying the Task Management System to production environments.

## Prerequisites

- Server with Ubuntu 20.04+ or similar Linux distribution
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database
- Node.js 14+ and npm
- Python 3.8+

## Production Architecture

```
Internet
    │
    ▼
[Nginx Reverse Proxy] :80, :443
    │
    ├─► [React Frontend] (Static Files)
    │
    └─► [Gunicorn + Flask Backend] :5000
            │
            ▼
        [PostgreSQL] :5432
```

## Backend Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y

# Create application user
sudo useradd -m -s /bin/bash taskapp
sudo su - taskapp
```

### 2. Clone and Setup Application

```bash
# Clone repository (or upload files)
git clone <your-repo-url> ~/task-manager
cd ~/task-manager/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE taskmanager;
CREATE USER taskapp WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskapp;
\q
```

### 4. Environment Configuration

Create production `.env` file:

```bash
# backend/.env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your_very_long_random_secret_key_here
JWT_SECRET_KEY=another_very_long_random_secret_key_here
DATABASE_URL=postgresql://taskapp:your_secure_password@localhost/taskmanager
```

**Generate secure keys:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize Database

```bash
cd ~/task-manager/database
python3 migrate.py
```

### 6. Create Systemd Service

Create `/etc/systemd/system/taskmanager.service`:

```ini
[Unit]
Description=Task Manager Flask Application
After=network.target

[Service]
User=taskapp
Group=taskapp
WorkingDirectory=/home/taskapp/task-manager/backend
Environment="PATH=/home/taskapp/task-manager/backend/venv/bin"
ExecStart=/home/taskapp/task-manager/backend/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/taskmanager/access.log \
    --error-logfile /var/log/taskmanager/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7. Create Log Directory

```bash
sudo mkdir -p /var/log/taskmanager
sudo chown taskapp:taskapp /var/log/taskmanager
```

### 8. Start Backend Service

```bash
sudo systemctl daemon-reload
sudo systemctl start taskmanager
sudo systemctl enable taskmanager
sudo systemctl status taskmanager
```

## Frontend Deployment

### 1. Build React Application

```bash
cd ~/task-manager/frontend

# Update API URL for production
echo "REACT_APP_API_URL=https://yourdomain.com/api" > .env

# Install dependencies and build
npm install
npm run build
```

### 2. Move Build Files

```bash
sudo mkdir -p /var/www/taskmanager
sudo cp -r build/* /var/www/taskmanager/
sudo chown -R www-data:www-data /var/www/taskmanager
```

## Nginx Configuration

### 1. Create Nginx Config

Create `/etc/nginx/sites-available/taskmanager`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (after obtaining certificate)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend - React SPA
    location / {
        root /var/www/taskmanager;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/taskmanager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

## Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Monitoring and Maintenance

### 1. Log Rotation

Create `/etc/logrotate.d/taskmanager`:

```
/var/log/taskmanager/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 taskapp taskapp
    sharedscripts
    postrotate
        systemctl reload taskmanager > /dev/null 2>&1 || true
    endscript
}
```

### 2. Database Backups

Create backup script `/home/taskapp/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/taskapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U taskapp taskmanager > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete

echo "Backup completed: db_backup_$DATE.sql"
```

Add to crontab:
```bash
chmod +x /home/taskapp/backup.sh
crontab -e
# Add: 0 2 * * * /home/taskapp/backup.sh
```

### 3. Monitoring

Check service status:
```bash
sudo systemctl status taskmanager
sudo systemctl status nginx
```

View logs:
```bash
sudo tail -f /var/log/taskmanager/error.log
sudo tail -f /var/log/nginx/error.log
```

## Environment Variables Summary

### Backend (.env)
```
FLASK_ENV=production
SECRET_KEY=<random-key>
JWT_SECRET_KEY=<random-key>
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Frontend (.env)
```
REACT_APP_API_URL=https://yourdomain.com/api
```

## Performance Optimization

### 1. Gunicorn Workers
Calculate workers: `(2 x CPU cores) + 1`
```bash
# For 2 CPU cores
--workers 5
```

### 2. PostgreSQL Tuning
Edit `/etc/postgresql/*/main/postgresql.conf`:
```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
```

### 3. Nginx Caching
Add to nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
}
```

## Troubleshooting

### Backend not starting
```bash
# Check logs
sudo journalctl -u taskmanager -n 50
# Check permissions
ls -la /home/taskapp/task-manager/backend
# Test manually
source venv/bin/activate
python app.py
```

### Database connection issues
```bash
# Test connection
psql -U taskapp -d taskmanager -h localhost
# Check PostgreSQL status
sudo systemctl status postgresql
```

### Nginx 502 Bad Gateway
```bash
# Check if backend is running
curl http://127.0.0.1:5000/api/health
# Check nginx error log
sudo tail -f /var/log/nginx/error.log
```

## Security Checklist

- ✅ Strong SECRET_KEY and JWT_SECRET_KEY
- ✅ HTTPS enabled with valid certificate
- ✅ Firewall configured (only necessary ports open)
- ✅ Database user with limited privileges
- ✅ Regular backups configured
- ✅ Security headers enabled
- ✅ Rate limiting configured
- ✅ Log rotation enabled
- ✅ Keep software updated

## Scaling Considerations

### Horizontal Scaling
- Multiple Gunicorn instances with load balancer
- Redis for shared session storage
- PostgreSQL read replicas

### Vertical Scaling
- Increase Gunicorn workers
- Optimize database queries
- Add database indexes

## Support

For issues or questions:
1. Check application logs
2. Review nginx logs
3. Test API endpoints directly
4. Verify database connectivity
