#!/bin/bash

# Socials Application Setup & Deployment Script

set -e

echo "======================================"
echo "Socials - Setup & Deployment Guide"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Python ${python_version}${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate || . venv/Scripts/activate
echo -e "${GREEN}Virtual environment created${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed${NC}"

# Setup environment file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  Please update .env with your credentials${NC}"
    echo "  - FACEBOOK_APP_ID"
    echo "  - FACEBOOK_APP_SECRET"
    echo "  - SECRET_KEY"
    echo "  - ANTHROPIC_API_KEY"
fi

# Create uploads directory
mkdir -p uploads

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✓ Database initialized')
EOF

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env with your Facebook app credentials"
echo "2. Run: python run.py"
echo "3. Visit: http://localhost:5000"
echo ""
echo -e "${YELLOW}For production deployment:${NC}"
echo "  - Set FLASK_ENV=production"
echo "  - Use PostgreSQL instead of SQLite"
echo "  - Deploy with gunicorn (production WSGI server)"
echo "  - Use HTTPS only"
echo "  - Enable secure cookies"
