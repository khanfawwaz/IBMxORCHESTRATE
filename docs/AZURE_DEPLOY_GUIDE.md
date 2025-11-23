# ☁️ Deploying to Azure Linux VM

This guide will help you deploy the Warehouse AI Assistant to an Azure Linux VM (Ubuntu 20.04/22.04).

## 📋 Prerequisites

1.  **Azure VM:** An Ubuntu 20.04 or 22.04 LTS VM.
2.  **SSH Access:** You need to be able to SSH into the VM.
3.  **Domain Name (Optional):** If you want HTTPS (highly recommended).

## 🚀 Step 1: Prepare the VM

SSH into your VM:
```bash
ssh username@your-vm-ip
```

## 🚀 Step 2: Clone the Repository

```bash
git clone https://github.com/khanfawwaz/IBMxORCHESTRATE.git
cd IBMxORCHESTRATE
```

## 🚀 Step 3: Run the Deployment Script

I have created a script `scripts/deploy_azure.sh` that automates the installation.

1.  **Make it executable:**
    ```bash
    chmod +x scripts/deploy_azure.sh
    ```

2.  **Run it:**
    ```bash
    sudo ./scripts/deploy_azure.sh
    ```

    *This script will:*
    *   Update the system
    *   Install Python 3.10+, Node.js 18+, Nginx, and Git
    *   Set up the Python backend (venv, requirements)
    *   Build the React frontend
    *   Configure Nginx as a reverse proxy
    *   Set up a systemd service for the backend
    *   Configure the firewall (UFW)

## 🚀 Step 4: Configure Environment

1.  **Create .env file:**
    ```bash
    cp .env.example .env
    nano .env
    ```
2.  **Add your API Key:**
    ```bash
    GEMINI_API_KEY="your-key-here"
    ```
3.  **Restart Backend:**
    ```bash
    sudo systemctl restart warehouse-backend
    ```

## 🌐 Accessing the App

Open your browser and go to:
`http://your-vm-ip`

## 🔒 Enabling HTTPS (Recommended)

If you have a domain pointing to your VM IP:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🛠️ Troubleshooting

**Check Backend Status:**
```bash
sudo systemctl status warehouse-backend
```

**Check Backend Logs:**
```bash
sudo journalctl -u warehouse-backend -f
```

**Check Nginx Status:**
```bash
sudo systemctl status nginx
```

**Check Nginx Logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```
