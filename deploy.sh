#!/bin/bash

# Quick deployment preparation script for hackathons

echo "🚀 Preparing AI-Powered Earnings Calendar for deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial hackathon submission: AI-Powered Earnings Calendar"
    echo "✅ Git repository initialized"
else
    echo "📝 Adding latest changes to git..."
    git add .
    git commit -m "Updated for hackathon deployment $(date)"
    echo "✅ Changes committed"
fi

# Build the frontend
echo "🏗️  Building React frontend..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi

# Test backend
echo "🧪 Testing Flask backend..."
python -c "import app; print('Backend imports successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Backend test successful"
else
    echo "❌ Backend test failed"
    exit 1
fi

echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub: git remote add origin <your-repo-url> && git push -u origin main"
echo "2. Deploy to Vercel/Railway/Render using the DEPLOYMENT.md guide"
echo "3. Add your API keys to the deployment platform"
echo "4. Test the live URL before submitting!"
echo ""
echo "🏆 Good luck with your hackathon!"