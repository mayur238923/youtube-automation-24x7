#!/usr/bin/env python3
"""
Render.com Compatible Bot - 24/7 Running
Laptop band kar ke bhi chalega!
"""

import os
import time
import threading
from flask import Flask, jsonify, request
from telegram_bot import TelegramYouTubeBot

# Flask app for Render.com
app = Flask(__name__)

# Global bot instance
bot_instance = None
bot_thread = None

@app.route('/')
def health_check():
    """Health check for Render.com"""
    return jsonify({
        "status": "alive",
        "message": "YouTube Automation Bot is running 24/7!",
        "bot_running": bot_instance.is_running if bot_instance else False,
        "uploads_today": bot_instance.youtube_bot.daily_tech_uploads + bot_instance.youtube_bot.daily_entertainment_uploads if bot_instance else 0
    })

@app.route('/webhook/process', methods=['POST'])
def webhook_process():
    """Webhook endpoint for external triggers"""
    try:
        data = request.get_json()
        action = data.get('action', 'status')
        
        if not bot_instance:
            return jsonify({"error": "Bot not initialized"}), 500
        
        if action == 'start':
            bot_instance.is_running = True
            return jsonify({"message": "Bot started!"})
        
        elif action == 'stop':
            bot_instance.is_running = False
            return jsonify({"message": "Bot stopped!"})
        
        elif action == 'status':
            return jsonify({
                "running": bot_instance.is_running,
                "tech_uploads": bot_instance.youtube_bot.daily_tech_uploads,
                "entertainment_uploads": bot_instance.youtube_bot.daily_entertainment_uploads,
                "total_uploads": bot_instance.youtube_bot.daily_tech_uploads + bot_instance.youtube_bot.daily_entertainment_uploads
            })
        
        elif action == 'upload_tech':
            if bot_instance.is_running:
                success = bot_instance.youtube_bot.process_tech_video()
                return jsonify({"success": success, "message": "Tech video processed"})
            else:
                return jsonify({"error": "Bot is stopped"}), 400
        
        elif action == 'upload_entertainment':
            if bot_instance.is_running:
                success = bot_instance.youtube_bot.process_entertainment_video()
                return jsonify({"success": success, "message": "Entertainment video processed"})
            else:
                return jsonify({"error": "Bot is stopped"}), 400
        
        else:
            return jsonify({"error": "Invalid action"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/keep-alive')
def keep_alive():
    """Keep-alive endpoint for UptimeRobot"""
    return jsonify({
        "status": "alive",
        "timestamp": time.time(),
        "message": "Bot is running 24/7!"
    })

def start_bot():
    """Start the Telegram bot in background"""
    global bot_instance
    try:
        print("🚀 Starting Telegram YouTube Bot...")
        bot_instance = TelegramYouTubeBot()
        
        # Send startup message
        bot_instance.send_message("🤖 <b>Bot Started!</b>\n\n✅ Render deployment successful\n📱 Send 'start' to begin automation")
        
        # Start the bot
        bot_instance.run_forever()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        # Send error message
        if bot_instance:
            bot_instance.send_message(f"❌ <b>Bot Error:</b>\n\n{str(e)}")
        time.sleep(30)
        start_bot()  # Restart on error

def main():
    """Main function for Render.com"""
    global bot_thread
    
    print("🌟 YouTube Automation Bot - Render.com Deployment")
    print("🔥 24/7 Running - Laptop band kar ke bhi chalega!")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Get port from environment (Render.com requirement)
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🌐 Flask server starting on port {port}")
    print("📱 Telegram bot running in background")
    print("✅ Ready for 24/7 automation!")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
