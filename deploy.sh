#!/bin/bash

# Bangladesh Legal RAG Assistant - Deployment Script
# Author: ameensunny242@gmail.com

echo "🏛️ Bangladesh Legal RAG Assistant - Deployment Script"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Set variables
IMAGE_NAME="bangladesh-legal-rag"
GITHUB_REPO="bangladesh-legal-rag-assistant"
DOCKER_TAG="latest"

echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME:$DOCKER_TAG .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

echo "🔍 Docker image details:"
docker images | grep $IMAGE_NAME

echo ""
echo "🐙 Setting up Git repository..."

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/*.log
*.log

# Vector store (too large for git)
vectorstore/

# Temporary files
*.tmp
*.temp
EOF
    echo "✅ .gitignore created"
fi

# Add all files
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    git commit -m "Initial commit: Bangladesh Legal RAG Assistant

- Fixed all compatibility issues
- Added Docker support
- Complete deployment package
- Bengali language support
- 2049+ legal documents indexed
- Multiple AI modes (Lawyer, Research, Simple, Argument)
- Production-ready configuration

Author: ameensunny242@gmail.com"
    echo "✅ Changes committed to Git"
fi

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: $GITHUB_REPO"
echo "   - Make it public (for free Streamlit deployment)"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Add GitHub remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/$GITHUB_REPO.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Deploy on Streamlit Cloud:"
echo "   - Go to https://share.streamlit.io"
echo "   - Sign in with GitHub"
echo "   - Click 'New app'"
echo "   - Select your repository: $GITHUB_REPO"
echo "   - Main file path: app.py"
echo "   - Add your Google Gemini API key in secrets"
echo ""
echo "4. Or run locally with Docker:"
echo "   export GOOGLE_API_KEY='your_api_key_here'"
echo "   docker-compose up -d"
echo ""
echo "📧 Contact: ameensunny242@gmail.com"
echo "🎉 Your Bangladesh Legal RAG Assistant is ready for deployment!"