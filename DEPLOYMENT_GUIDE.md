# Bangladesh Legal RAG Assistant - Deployment Guide

## 🚀 Deployment Options

Your application is now ready for deployment! Here are several options from easiest to most advanced:

## 1. 🌟 Streamlit Community Cloud (Recommended - FREE)

**Pros:** Free, easy, automatic HTTPS, custom domain support
**Cons:** Public repositories only, resource limitations

### Steps:
1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Bangladesh Legal RAG Assistant"
   git branch -M main
   git remote add origin https://github.com/yourusername/bangladesh-legal-rag.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard, go to your app settings
   - Add secrets in TOML format:
   ```toml
   GOOGLE_API_KEY = "your_actual_gemini_api_key_here"
   ```

**URL:** Your app will be available at `https://yourusername-bangladesh-legal-rag-main-app-xyz123.streamlit.app`

---

## 2. 🐳 Docker Deployment

### Create Dockerfile:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs vectorstore data

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml:
```yaml
version: '3.8'
services:
  legal-rag:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./vectorstore:/app/vectorstore
      - ./logs:/app/logs
    restart: unless-stopped
```

### Deploy:
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 3. ☁️ Cloud Platform Deployment

### A. **Heroku** (Easy, Paid)
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Deploy:
   ```bash
   heroku create bangladesh-legal-rag
   heroku config:set GOOGLE_API_KEY="your_api_key"
   git push heroku main
   ```

### B. **Google Cloud Run** (Scalable)
1. Build and push Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/legal-rag
   ```
2. Deploy:
   ```bash
   gcloud run deploy --image gcr.io/PROJECT_ID/legal-rag --platform managed
   ```

### C. **AWS ECS/Fargate** (Enterprise)
1. Push Docker image to ECR
2. Create ECS task definition
3. Deploy to Fargate cluster

---

## 4. 🖥️ VPS/Server Deployment

### Using Ubuntu Server:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx -y

# Clone your repository
git clone https://github.com/yourusername/bangladesh-legal-rag.git
cd bangladesh-legal-rag

# Install dependencies
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/legal-rag.service
```

**Service file content:**
```ini
[Unit]
Description=Bangladesh Legal RAG Assistant
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bangladesh-legal-rag
Environment=GOOGLE_API_KEY=your_api_key_here
ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable legal-rag
sudo systemctl start legal-rag
```

**Configure Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 5. 📱 Mobile-Friendly Deployment

### Add to app.py for better mobile experience:
```python
st.set_page_config(
    page_title="Bangladesh Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",  # Better for mobile
    menu_items={
        'Get Help': 'https://your-help-url.com',
        'Report a bug': 'https://your-bug-report-url.com',
        'About': "Bangladesh Legal RAG Assistant v1.0"
    }
)
```

---

## 🔒 Security Considerations

### 1. Environment Variables:
Never commit API keys to Git. Use environment variables:
```bash
export GOOGLE_API_KEY="your_key_here"
```

### 2. HTTPS:
Always use HTTPS in production. Most cloud platforms provide this automatically.

### 3. Rate Limiting:
Consider implementing rate limiting for API calls:
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=10):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'last_call' not in st.session_state:
                st.session_state.last_call = 0
            
            time_since_last = time.time() - st.session_state.last_call
            if time_since_last < 60/calls_per_minute:
                st.warning("Please wait before making another request.")
                return None
            
            st.session_state.last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 📊 Monitoring & Analytics

### Add basic analytics:
```python
# Add to app.py
import streamlit.components.v1 as components

# Google Analytics (optional)
components.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", height=0)
```

---

## 🎯 Recommended Deployment Path

**For beginners:** Start with Streamlit Community Cloud
**For production:** Use Docker + Cloud Run/AWS Fargate
**For enterprise:** VPS with proper monitoring and backup

---

## 📞 Support

If you encounter issues during deployment:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Ensure your API key has sufficient quota
4. Test locally first before deploying

Your Bangladesh Legal RAG Assistant is ready for the world! 🚀