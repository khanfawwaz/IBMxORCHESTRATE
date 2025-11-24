# 🚀 Deploying to Linux VM with Tailscale

This guide will help you deploy the full application to a Linux VM and expose it using Tailscale.

## ✅ Prerequisites

1.  **Linux VM** (Ubuntu 20.04 or 22.04 recommended).
2.  **Tailscale** installed and logged in on the VM.
    ```bash
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up
    ```

## 🛠️ Step 1: Clone & Deploy

SSH into your VM and run these commands:

```bash
# 1. Clone the repository
git clone https://github.com/khanfawwaz/IBMxORCHESTRATE.git
cd IBMxORCHESTRATE

# 2. Run the automated deployment script
# This installs Python, Node.js, Nginx, builds the app, and starts the backend
chmod +x scripts/deploy_azure.sh
sudo ./scripts/deploy_azure.sh
```

## 🔑 Step 2: Configure API Key

1.  **Edit the .env file:**
    ```bash
    nano .env
    ```
2.  **Paste your Gemini API Key:**
    ```bash
    GEMINI_API_KEY="your-api-key-here"
    ```
3.  **Restart the backend:**
    ```bash
    sudo systemctl restart warehouse-backend
    ```

## 🌐 Step 3: Expose with Tailscale

Now that Nginx is serving your app on port 80 (locally), use Tailscale to expose it.

### **Option A: Expose to your Tailnet (Private)**
Only devices on your Tailscale network can access it.

```bash
sudo tailscale serve --bg --https=443 http://localhost:80
```

### **Option B: Expose to Internet (Funnel)**
Anyone on the internet can access it.

1.  **Enable Funnel:**
    ```bash
    sudo tailscale funnel --bg --https=443 http://localhost:80
    ```

2.  **Get your URL:**
    ```bash
    tailscale status
    ```
    Look for your machine name (e.g., `https://machine-name.tailnet.ts.net`).

## 🔄 Step 4: Update Frontend Config (Important!)

The frontend needs to know where to send API requests.

1.  **Edit the Nginx config** to ensure `/api` requests are proxied correctly (The script does this automatically!).
    *   The script sets up Nginx to forward `/api` to `localhost:9000`.
    *   This means your frontend can just send requests to `/api/...` relative to the domain.

2.  **Verify `frontend/app/src/App.jsx` on the VM:**
    Since we are serving via Nginx on the same domain, we should update the API URL to be relative.

    **On your VM:**
    ```bash
    nano frontend/app/src/App.jsx
    ```
    Change `BASE_URL` to an empty string or `/`:
    ```javascript
    const API_CONFIG = {
      BASE_URL: '',  // Relative path, uses the same domain
      ENDPOINTS: {
        CHAT: '/api/v1/chat'
      }
    };
    ```

3.  **Rebuild Frontend:**
    ```bash
    cd frontend/app
    npm run build
    sudo systemctl restart nginx
    ```

---

## 📝 Summary

1.  **Clone Repo**
2.  **Run `deploy_azure.sh`**
3.  **Set API Key**
4.  **Run `tailscale funnel --bg --https=443 http://localhost:80`**
5.  **Access your URL!**
