@echo off
echo 🚀 Preparing AI-Powered Earnings Calendar for deployment...

REM Check if git is initialized
if not exist ".git" (
    echo 📝 Initializing git repository...
    git init
    git add .
    git commit -m "Initial hackathon submission: AI-Powered Earnings Calendar"
    echo ✅ Git repository initialized
) else (
    echo 📝 Adding latest changes to git...
    git add .
    git commit -m "Updated for hackathon deployment %date% %time%"
    echo ✅ Changes committed
)

REM Build the frontend
echo 🏗️ Building React frontend...
call npm run build

if %errorlevel% equ 0 (
    echo ✅ Frontend build successful
) else (
    echo ❌ Frontend build failed
    exit /b 1
)

REM Test backend
echo 🧪 Testing Flask backend...
python -c "import app; print('Backend imports successfully')"

if %errorlevel% equ 0 (
    echo ✅ Backend test successful
) else (
    echo ❌ Backend test failed
    exit /b 1
)

echo.
echo 🎉 Deployment preparation complete!
echo.
echo Next steps:
echo 1. Push to GitHub: git remote add origin ^<your-repo-url^> ^&^& git push -u origin main
echo 2. Deploy to Vercel/Railway/Render using the DEPLOYMENT.md guide
echo 3. Add your API keys to the deployment platform
echo 4. Test the live URL before submitting!
echo.
echo 🏆 Good luck with your hackathon!
pause