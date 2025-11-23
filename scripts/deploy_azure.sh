#!/bin/bash

# Azure Deployment Script for Warehouse AI Assistant
# Runs on Ubuntu 20.04/22.04

set -e  # Exit on error

echo "🚀 Starting Deployment..."

# 1. Update System
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install Dependencies
echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv nginx git curl build-essential

# 3. Install Node.js (v18)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 4. Setup Backend
echo "🔧 Setting up Backend..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Build Frontend
echo "🔧 Building Frontend..."
cd frontend/app
npm install
npm run build
cd ../..

# 6. Configure Nginx
echo "🌐 Configuring Nginx..."
sudo rm -f /etc/nginx/sites-enabled/default

# Create Nginx Config
cat <<EOF | sudo tee /etc/nginx/sites-available/warehouse-ai
server {
    listen 80;
    server_name _;

    root $(pwd)/frontend/app/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:9000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/warehouse-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 7. Setup Systemd Service
echo "⚙️ Creating Systemd Service..."
cat <<EOF | sudo tee /etc/systemd/system/warehouse-backend.service
[Unit]
Description=Warehouse AI Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python backend/orchestrator/app.py
Restart=always
Environment="PATH=$(pwd)/venv/bin:/usr/bin"
# Load env vars from .env file if it exists
EnvironmentFile=$(pwd)/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable warehouse-backend
sudo systemctl restart warehouse-backend

# 8. Firewall
echo "🛡️ Configuring Firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp

echo "✅ Deployment Complete!"
echo "👉 Access your app at: http://$(curl -s ifconfig.me)"
echo "⚠️  Don't forget to edit .env and add your GEMINI_API_KEY!"
