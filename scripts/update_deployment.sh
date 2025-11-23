#!/bin/bash

# Update Script
echo "🔄 Updating Deployment..."

# Pull latest code
git pull origin main

# Update Backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart warehouse-backend

# Update Frontend
cd frontend/app
npm install
npm run build
cd ../..

echo "✅ Update Complete!"
