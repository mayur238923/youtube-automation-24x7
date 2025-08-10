#!/usr/bin/env python3
"""
Deta Space compatible Telegram Bot
"""

import os
from telegram_bot import TelegramYouTubeBot

# Deta Space entry point
def main():
    print("🚀 Starting Telegram Bot on Deta Space...")
    bot = TelegramYouTubeBot()
    bot.run_forever()

if __name__ == "__main__":
    main()