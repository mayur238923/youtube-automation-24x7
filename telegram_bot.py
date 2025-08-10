#!/usr/bin/env python3
"""
Telegram Bot for YouTube Automation Control
24/7 running with commands and notifications
"""

import os
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
import requests
from youtube_bot import YouTubeBot

load_dotenv()

class TelegramYouTubeBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.youtube_bot = YouTubeBot()
        self.is_running = False
        self.last_update_id = 0
        
        print("🤖 Telegram YouTube Bot Initialized!")
        print(f"📱 Bot Token: {self.telegram_token[:10]}...")
        print(f"💬 Chat ID: {self.telegram_chat_id}")
    
    def send_message(self, message):
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def get_updates(self):
        """Get updates from Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            return []
        except Exception as e:
            print(f"❌ Get updates error: {e}")
            return []
    
    def handle_command(self, message):
        """Handle Telegram commands"""
        text = message.get('text', '').lower().strip()
        chat_id = message['chat']['id']
        
        # Store chat ID if not set
        if not self.telegram_chat_id:
            self.telegram_chat_id = str(chat_id)
        
        if text == '/start' or text == 'start':
            if not self.is_running:
                self.is_running = True
                welcome_msg = """
🚀 <b>YouTube Automation STARTED!</b>

📋 <b>Available Commands:</b>
• <b>start</b> - Start automation
• <b>stop</b> - Stop automation  
• <b>status</b> - Current status
• <b>logs</b> - Recent uploads
• <b>upload tech</b> - Upload tech video now
• <b>upload entertainment</b> - Upload entertainment video

🤖 <b>Bot is now running 24/7!</b>
You'll get notifications for every upload.
"""
                self.send_message(welcome_msg)
            else:
                self.send_message("✅ <b>Automation is already running!</b>")
            
        elif text == '/status' or text == 'status':
            total = self.youtube_bot.daily_tech_uploads + self.youtube_bot.daily_entertainment_uploads
            status_msg = f"""
📊 <b>Current Status:</b>

🔧 <b>Tech:</b> {self.youtube_bot.daily_tech_uploads}/5
🎬 <b>Entertainment:</b> {self.youtube_bot.daily_entertainment_uploads}/5
📈 <b>Total Today:</b> {total}/10

🤖 <b>Bot Status:</b> {'🟢 Running' if self.is_running else '🔴 Stopped'}
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
📋 <b>Processed Videos:</b> {len(self.youtube_bot.processed_videos)}
"""
            self.send_message(status_msg)
            
        elif text == '/upload_tech' or text == 'upload tech':
            self.send_message("🔧 <b>Processing Tech Video...</b>")
            success = self.youtube_bot.process_tech_video()
            if success:
                self.send_message("✅ <b>Tech video uploaded successfully!</b>")
            else:
                self.send_message("❌ <b>Tech video upload failed!</b>")
                
        elif text == '/upload_entertainment' or text == 'upload entertainment':
            self.send_message("🎬 <b>Processing Entertainment Video...</b>")
            success = self.youtube_bot.process_entertainment_video()
            if success:
                self.send_message("✅ <b>Entertainment video uploaded successfully!</b>")
            else:
                self.send_message("❌ <b>Entertainment video upload failed!</b>")
                
        elif text == '/logs' or text == 'logs':
            try:
                with open('upload_log.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_logs = lines[-5:]  # Last 5 uploads
                    
                logs_msg = "<b>📋 Recent Uploads:</b>\n\n"
                for line in recent_logs:
                    logs_msg += f"• {line.strip()}\n"
                    
                self.send_message(logs_msg)
            except:
                self.send_message("❌ <b>No logs found!</b>")
                
        elif text == '/stop' or text == 'stop':
            if self.is_running:
                self.is_running = False
                self.send_message("⏸️ <b>Automation STOPPED!</b>")
            else:
                self.send_message("⏸️ <b>Automation is already stopped!</b>")
            
        elif text == '/resume' or text == 'resume':
            if not self.is_running:
                self.is_running = True
                self.send_message("▶️ <b>Automation RESUMED!</b>")
            else:
                self.send_message("▶️ <b>Automation is already running!</b>")
            
        elif text == '/help' or text == 'help':
            help_msg = """
🤖 <b>YouTube Automation Bot Help</b>

<b>Simple Commands:</b>
• <b>start</b> - Start automation
• <b>stop</b> - Stop automation  
• <b>status</b> - Check progress
• <b>logs</b> - View recent uploads
• <b>upload tech</b> - Manual tech upload
• <b>upload entertainment</b> - Manual entertainment upload

<b>Features:</b>
• 24/7 automated uploads
• 5 Tech + 5 Entertainment daily
• Smart video processing
• Duplicate prevention
• Real-time notifications

<b>Schedule:</b>
Tech: 08:00, 12:00, 16:00, 20:00, 23:00
Entertainment: 10:00, 14:00, 18:00, 21:00, 23:30
"""
            self.send_message(help_msg)
        else:
            self.send_message("❓ <b>Unknown command!</b>\n\nSimple commands:\n• <b>start</b> - Start automation\n• <b>stop</b> - Stop automation\n• <b>status</b> - Check status")
    
    def run_forever(self):
        """Run Telegram bot forever"""
        print("🚀 Starting Telegram YouTube Bot...")
        
        # Bot starts in STOPPED state - wait for user command
        self.is_running = False
        self.send_message("🤖 <b>YouTube Bot Ready!</b>\n\n📱 Send <b>'start'</b> to begin automation\n📱 Send <b>'stop'</b> to stop automation")
        
        print("🤖 Telegram bot is running...")
        print("💬 Bot is STOPPED - Send 'start' command to begin automation!")
        
        # Main bot loop
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        self.handle_command(update['message'])
                
                time.sleep(1)  # Small delay
                
            except KeyboardInterrupt:
                print("\n⏹️ Bot stopped by user")
                self.send_message("⏹️ <b>Bot stopped by admin!</b>")
                break
            except Exception as e:
                print(f"❌ Bot error: {e}")
                time.sleep(30)  # Wait 30 seconds on error

if __name__ == "__main__":
    print("🤖 TELEGRAM YOUTUBE AUTOMATION BOT")
    print("🔥 24/7 running with commands!")
    print("📱 Control via Telegram messages")
    
    bot = TelegramYouTubeBot()
    bot.run_forever()
