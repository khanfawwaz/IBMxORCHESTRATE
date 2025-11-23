# API Configuration Guide

## Frontend API URL

The frontend automatically detects the environment and uses the correct API URL:

### **Development (Localhost)**
- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:9000`
- Auto-detected when running locally

### **Production**
Edit `frontend/index.html` line ~465:
```javascript
const API_CONFIG = {
    BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:9000'
        : 'https://your-production-url.com',  // ← Change this
    ...
};
```

## CORS Configuration

### **Backend (Already Configured) ✅**

File: `backend/orchestrator/app.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
```

**For Production:**
Change `allow_origins=["*"]` to specific domains:
```python
allow_origins=[
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com"
]
```

## Testing CORS

### **1. Check Backend CORS Headers**
```bash
curl -i -X OPTIONS http://localhost:9000/api/v1/chat \
  -H "Origin: http://localhost:8080" \
  -H "Access-Control-Request-Method: POST"
```

Should return:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### **2. Test from Frontend**
Open browser console (F12) and run:
```javascript
fetch('http://localhost:9000/api/v1/health')
  .then(r => r.json())
  .then(d => console.log('✅ CORS working:', d))
  .catch(e => console.error('❌ CORS error:', e));
```

## Current Setup

✅ **Backend CORS:** Configured (allows all origins)  
✅ **Frontend API URL:** Auto-detects localhost  
✅ **Ready to use:** No changes needed for development  

## For Production Deployment

1. **Update Frontend API URL:**
   - Edit `frontend/index.html`
   - Change `BASE_URL` to your production backend URL

2. **Restrict Backend CORS:**
   - Edit `backend/orchestrator/app.py`
   - Set `allow_origins` to your frontend domain(s)

3. **Use HTTPS:**
   - Both frontend and backend should use HTTPS
   - Mixed content (HTTP + HTTPS) will be blocked by browsers

---

**Everything is already configured for local development!** 🎉
