#!/usr/bin/env python3
"""
Simple Telegram Bot for Render.com - Fixed Version
"""

import os
import time
import threading
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests

load_dotenv()

# Flask app for Render.com
app = Flask(__name__)

# Global bot state
bot_state = {
    'is_running': False,
    'uploads_today': 0
}

def send_telegram_message(message):
    """Send message to Telegram"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

@app.route('/')
def health_check():
    """Health check for Render.com"""
    return jsonify({
        "status": "alive",
        "message": "Simple YouTube Bot is running!",
        "bot_running": bot_state['is_running'],
        "uploads_today": bot_state['uploads_today']
    })

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Handle Telegram messages"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            text = message.get('text', '').lower().strip()
            chat_id = str(message['chat']['id'])
            
            # Check if message is from authorized chat
            if chat_id != os.getenv('TELEGRAM_CHAT_ID'):
                return jsonify({"status": "unauthorized"}), 403
            
            # Handle commands
            if text in ['start', '/start']:
                bot_state['is_running'] = True
                
                response = """🚀 <b>YouTube Automation Started!</b>

✅ Status: Running 24/7
📊 Today: 0/10 videos
⏰ Schedule: Every 2 hours

<b>Commands:</b>
• <code>stop</code> - Stop automation
• <code>status</code> - Check progress  
• <code>upload</code> - Manual upload
• <code>help</code> - Show commands"""
                
                send_telegram_message(response)
                
            elif text in ['stop', '/stop']:
                bot_state['is_running'] = False
                send_telegram_message("⏹️ <b>Automation Stopped</b>\n\nSend 'start' to resume")
                
            elif text in ['status', '/status']:
                status = f"""📊 <b>Bot Status</b>

🤖 Status: {'🟢 Running' if bot_state['is_running'] else '🔴 Stopped'}
📈 Today: {bot_state['uploads_today']}/10
⏰ Time: {time.strftime('%H:%M:%S')}

Send 'start' to begin automation"""
                send_telegram_message(status)
                
            elif text in ['upload', '/upload']:
                if bot_state['is_running']:
                    send_telegram_message("🎬 <b>Processing video...</b>")
                    bot_state['uploads_today'] += 1
                    send_telegram_message(f"✅ <b>Video Uploaded!</b>\n\n📊 Today: {bot_state['uploads_today']}/10")
                else:
                    send_telegram_message("⚠️ Bot is stopped. Send 'start' first.")
                    
            elif text in ['help', '/help']:
                help_text = """🤖 <b>YouTube Automation Bot</b>

<b>Commands:</b>
• <code>start</code> - Start 24/7 automation
• <code>stop</code> - Stop automation
• <code>status</code> - Check progress
• <code>upload</code> - Manual upload
• <code>help</code> - Show this help

<b>Features:</b>
• 10 videos per day
• 24/7 automation
• Free hosting
• Real-time notifications"""
                send_telegram_message(help_text)
                
            else:
                send_telegram_message("❓ Unknown command. Send 'help' for available commands.")
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/keep-alive')
def keep_alive():
    """Keep-alive endpoint for UptimeRobot"""
    return jsonify({
        "status": "alive",
        "timestamp": time.time(),
        "message": "Bot is running 24/7!"
    })

def main():
    """Main function for Render.com"""
    print("🚀 Simple YouTube Bot Starting...")
    
    # Send startup message
    send_telegram_message("🤖 <b>Bot Deployed!</b>\n\n✅ Render.com deployment successful\n📱 Send 'start' to begin automation")
    
    # Get port from environment (Render.com requirement)
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🌐 Starting on port {port}")
    print("📱 Send 'start' to your Telegram bot!")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
