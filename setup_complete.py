#!/usr/bin/env python3
"""
Complete Setup Verification Script
Checks if everything is ready for deployment
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = [
        'YOUTUBE_API_KEY',
        'YOUTUBE_CLIENT_ID', 
        'YOUTUBE_CLIENT_SECRET',
        'GROQ_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Missing")
        else:
            print(f"✅ {var}: Set ({value[:10]}...)")
    
    if missing_vars:
        print(f"\n⚠️ Missing variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_youtube_api():
    """Test YouTube API connection"""
    print("\n🔍 Testing YouTube API...")
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ YouTube API key not found")
        return False
    
    try:
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&maxResults=1&key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ YouTube API working!")
            return True
        else:
            print(f"❌ YouTube API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        return False

def test_groq_api():
    """Test Groq API connection"""
    print("\n🔍 Testing Groq API...")
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Groq API key not found")
        return False
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Groq API working!")
            return True
        else:
            print(f"❌ Groq API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        return False

def test_telegram_bot():
    """Test Telegram bot connection"""
    print("\n🔍 Testing Telegram Bot...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Telegram credentials not found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            bot_name = bot_info['result']['username']
            print(f"✅ Telegram bot working! (@{bot_name})")
            
            # Test sending message
            test_url = f"https://api.telegram.org/bot{token}/sendMessage"
            test_data = {
                'chat_id': chat_id,
                'text': '🧪 Setup Test: Bot is working!',
                'parse_mode': 'HTML'
            }
            
            test_response = requests.post(test_url, data=test_data, timeout=10)
            if test_response.status_code == 200:
                print("✅ Test message sent successfully!")
                return True
            else:
                print("⚠️ Bot works but couldn't send test message")
                return False
        else:
            print(f"❌ Telegram bot error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False

def check_required_files():
    """Check if all required files exist"""
    print("\n🔍 Checking Required Files...")
    
    required_files = [
        'render_bot.py',
        'youtube_bot.py',
        'requirements.txt',
        'render.yaml',
        'Procfile',
        'cloudflare_worker_scheduler.js',
        'wrangler.toml',
        '.env'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: Found")
        else:
            missing_files.append(file)
            print(f"❌ {file}: Missing")
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present!")
    return True

def generate_deployment_urls():
    """Generate deployment URLs and commands"""
    print("\n🚀 Deployment Information:")
    print("=" * 50)
    
    print("\n📋 **STEP 1: GitHub Repository**")
    print("1. Create new repository on GitHub")
    print("2. Upload all files from current directory")
    print("3. Copy repository URL")
    
    print("\n📋 **STEP 2: Render Deployment**")
    print("1. Go to: https://render.com")
    print("2. Connect GitHub repository")
    print("3. Use these settings:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python render_bot.py")
    print("   - Environment: Python 3")
    
    print("\n📋 **STEP 3: Cloudflare Workers**")
    print("1. Go to: https://workers.cloudflare.com")
    print("2. Create new worker")
    print("3. Copy code from: cloudflare_worker_scheduler.js")
    print("4. Set environment variables")
    print("5. Add cron triggers")
    
    print("\n📋 **STEP 4: UptimeRobot**")
    print("1. Go to: https://uptimerobot.com")
    print("2. Add monitor for your Render URL")
    print("3. Set interval to 5 minutes")
    
    print("\n🎯 **Expected Results:**")
    print("- 10 videos uploaded daily")
    print("- 24/7 automation")
    print("- Telegram notifications")
    print("- 100% free hosting")

def main():
    """Run complete setup verification"""
    print("🚀 YouTube Automation Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check environment variables
    if not check_environment_variables():
        all_good = False
    
    # Check required files
    if not check_required_files():
        all_good = False
    
    # Test APIs
    if not test_youtube_api():
        all_good = False
    
    if not test_groq_api():
        all_good = False
    
    if not test_telegram_bot():
        all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 **SETUP VERIFICATION PASSED!**")
        print("✅ All systems are ready for deployment")
        print("\n🚀 Ready to deploy on Render + Cloudflare!")
        generate_deployment_urls()
    else:
        print("❌ **SETUP VERIFICATION FAILED!**")
        print("⚠️ Please fix the issues above before deployment")
        print("\n📋 Common fixes:")
        print("- Check .env file for missing variables")
        print("- Verify API keys are correct")
        print("- Ensure all files are present")
    
    print("\n📞 Need help? Check DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()