#!/usr/bin/env python3
"""
Startup script for AI-Powered Earnings Calendar
Handles environment setup and launches the application
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required. Current version:", 
              f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_node_version():
    """Check if Node.js is available and version is compatible"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print("❌ Node.js not found. Please install Node.js 16+")
            return False
        
        version = result.stdout.strip()
        major_version = int(version.lstrip('v').split('.')[0])
        if major_version < 16:
            print(f"❌ Node.js 16+ is required. Current version: {version}")
            return False
        
        print(f"✅ Node.js version: {version}")
        return True
    except Exception as e:
        print(f"❌ Error checking Node.js: {e}")
        return False

def install_python_deps():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Python dependencies: {e}")
        return False

def install_node_deps():
    """Install Node.js dependencies"""
    print("📦 Installing Node.js dependencies...")
    try:
        subprocess.run(['npm', 'install'], check=True, shell=True)
        print("✅ Node.js dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Node.js dependencies: {e}")
        return False

def build_frontend():
    """Build React frontend"""
    print("🏗️ Building React frontend...")
    try:
        subprocess.run(['npm', 'run', 'build'], check=True, shell=True)
        print("✅ Frontend built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building frontend: {e}")
        return False

def start_application(mode='production'):
    """Start the application"""
    if mode == 'development':
        print("🚀 Starting development servers...")
        try:
            # Start Flask backend
            flask_process = subprocess.Popen([sys.executable, 'app.py'])
            print("✅ Flask backend started on http://localhost:5000")
            
            # Start Vite dev server
            vite_process = subprocess.Popen(['npm', 'run', 'dev'], shell=True)
            print("✅ Vite dev server started on http://localhost:5173")
            
            print("\n🌟 Development servers running!")
            print("   - Backend: http://localhost:5000")
            print("   - Frontend: http://localhost:5173")
            print("   - Press Ctrl+C to stop both servers")
            
            try:
                flask_process.wait()
                vite_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping servers...")
                flask_process.terminate()
                vite_process.terminate()
                
        except Exception as e:
            print(f"❌ Error starting development servers: {e}")
    else:
        print("🚀 Starting production server...")
        try:
            subprocess.run([sys.executable, 'app.py'])
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

def main():
    """Main startup function"""
    print("🎯 AI-Powered Earnings Calendar - Setup & Launch")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_python_deps():
        sys.exit(1)
        
    if not install_node_deps():
        sys.exit(1)
    
    # Ask user for mode
    print("\n🔧 Setup Mode:")
    print("1. Production (build frontend, run on Flask server)")
    print("2. Development (separate dev servers)")
    
    try:
        choice = input("Choose mode (1 or 2, default=1): ").strip()
        if choice == '2':
            start_application('development')
        else:
            if build_frontend():
                start_application('production')
            else:
                sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled")
        sys.exit(1)

if __name__ == "__main__":
    main()