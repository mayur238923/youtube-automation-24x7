#!/usr/bin/env python3
"""
Complete YouTube Automation Bot - Single File
- Never stops running (24/7)
- 5-8 videos per day automatically
- Copyright protection
- AI content generation
- Auto upload to YouTube
"""

import os
import random
import time
import json
import pickle
import schedule
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import yt_dlp
from moviepy.editor import VideoFileClip
import requests

load_dotenv()

class YouTubeBot:
    def __init__(self):
        # API Keys
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.client_id = os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # YouTube APIs
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        self.upload_youtube = None
        
        # Daily tracking - 10 videos total (5 tech + 5 entertainment)
        self.daily_tech_uploads = 0
        self.daily_entertainment_uploads = 0
        self.max_tech_uploads = 5
        self.max_entertainment_uploads = 5

        # Load processed videos from file (permanent storage)
        self.processed_videos = self._load_processed_videos()
        self.uploaded_titles = self._load_uploaded_titles()
        
        # Create directories
        os.makedirs('downloads', exist_ok=True)
        os.makedirs('shorts', exist_ok=True)
        os.makedirs('credentials', exist_ok=True)
        
        print(f"🤖 YouTube Bot Ready! Target: {self.max_tech_uploads} Tech + {self.max_entertainment_uploads} Entertainment = 10 videos today")
        print(f"📋 Already processed: {len(self.processed_videos)} videos")

    def _load_processed_videos(self):
        """Load processed video IDs from file"""
        try:
            with open('processed_videos.txt', 'r') as f:
                videos = set(line.strip() for line in f if line.strip())
                print(f"📋 Loaded {len(videos)} processed videos from file")
                return videos
        except FileNotFoundError:
            print("📋 No processed videos file found, starting fresh")
            return set()

    def _save_processed_video(self, video_id):
        """Save processed video ID to file"""
        with open('processed_videos.txt', 'a') as f:
            f.write(f"{video_id}\n")

    def _load_uploaded_titles(self):
        """Load uploaded titles from file"""
        try:
            with open('uploaded_titles.txt', 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            return set()

    def _save_uploaded_title(self, title):
        """Save uploaded title to file"""
        with open('uploaded_titles.txt', 'a', encoding='utf-8') as f:
            f.write(f"{title}\n")

    def send_telegram_message(self, message):
        """Send message to Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            return False

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
    
    def get_trending_videos_by_category(self, category_id):
        """Get trending videos for specific category"""
        category_name = "Tech" if category_id == '28' else "Entertainment"
        print(f"🔍 Finding trending {category_name} videos...")

        try:
            regions = ['US', 'IN', 'GB']
            videos = []
            
            for region in regions:
                try:
                    request = self.youtube.videos().list(
                        part='snippet,statistics,contentDetails',
                        chart='mostPopular',
                        regionCode=region,
                        maxResults=10,
                        videoCategoryId=category_id
                    )

                    response = request.execute()
                    print(f"🔍 API Response for {region}/{category_name}: {len(response.get('items', []))} videos")

                    for item in response['items']:
                        if item['id'] in self.processed_videos:
                            continue

                        duration = self._parse_duration(item['contentDetails']['duration'])
                        print(f"⏱️ Duration check: {item['snippet']['title'][:30]}... = {duration}s")

                        if 15 <= duration <= 600:  # 15 seconds to 10 minutes (includes shorts)
                            views = int(item['statistics'].get('viewCount', 0))

                            # Debug: Show all videos found
                            print(f"📊 Found: {item['snippet']['title'][:40]}... | {views:,} views")

                            # Temporary: Accept any video with 100k+ views for testing
                            if views >= 100000:
                                video_data = {
                                    'id': item['id'],
                                    'title': item['snippet']['title'],
                                    'channel': item['snippet']['channelTitle'],
                                    'views': views,
                                    'duration': duration,
                                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                                }

                                if self._is_safe_content(video_data):
                                    videos.append(video_data)
                                    print(f"✅ PASSED: {video_data['title'][:30]}...")
                                else:
                                    print(f"🚫 BLOCKED: {video_data['title'][:30]}...")

                    time.sleep(0.1)

                except Exception as e:
                    continue
            
            # Sort by views
            videos.sort(key=lambda x: x['views'], reverse=True)
            return videos[:10]
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def _parse_duration(self, duration_str):
        """Parse YouTube duration"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _is_safe_content(self, video_data):
        """ULTRA STRONG Copyright protection - Maximum Safety"""
        
        # MEGA STRICT copyright protection
        copyright_flags = [
            # Music related
            'official music video', 'vevo', 'records', 'soundtrack', 'music video',
            'song', 'album', 'artist', 'band', 'music', 'audio', 'lyrics', 'karaoke',
            'cover song', 'remix', 'mashup', 'acoustic', 'live performance', 'concert',
            'ft.', 'feat.', 'featuring', 'vs', 'x ', ' x ', 'collaboration',
            
            # Movie/TV related
            'movie trailer', 'full movie', 'tv show', 'netflix', 'disney', 'hbo',
            'warner bros', 'universal pictures', 'sony pictures', 'paramount',
            'marvel', 'dc comics', 'pixar', 'dreamworks', 'mgm', '20th century',
            'trailer', 'teaser', 'clip', 'scene', 'episode', 'season', 'series',
            'film', 'cinema', 'hollywood', 'bollywood', 'movie', 'documentary',
            
            # Copyright terms
            'copyrighted', 'all rights reserved', 'licensed content', 'exclusive',
            'official', 'original', 'premiere', 'first look', 'behind the scenes',
            'making of', 'interview', 'press conference', 'red carpet',
            
            # Sports/Events
            'fifa', 'nfl', 'nba', 'premier league', 'champions league', 'olympics',
            'world cup', 'super bowl', 'match highlights', 'goal', 'touchdown',
            
            # News/Media
            'breaking news', 'live news', 'cnn', 'bbc', 'fox news', 'reuters',
            'associated press', 'news report', 'press release', 'announcement',
            
            # Gaming (risky ones)
            'gameplay', 'walkthrough', 'let\'s play', 'game trailer', 'cutscene',
            'nintendo', 'playstation', 'xbox', 'steam', 'epic games',
            
            # Brands/Companies
            'apple', 'google', 'microsoft', 'amazon', 'facebook', 'tesla',
            'samsung', 'iphone', 'android', 'windows', 'mac', 'ios'
        ]
        
        text = f"{video_data['title']} {video_data['channel']}".lower()
        
        # Check each flag
        for flag in copyright_flags:
            if flag in text:
                print(f"🚫 BLOCKED by flag: '{flag}' in '{video_data['title'][:30]}...'")
                return False
        
        # MEGA STRICT Channel blacklist
        blacklisted_channels = [
            # Music labels
            'vevo', 'records', 'music', 'entertainment', 'official', 'label',
            'sony', 'universal', 'warner', 'emi', 'atlantic', 'capitol',
            
            # Movie studios
            'films', 'movies', 'studios', 'pictures', 'cinema', 'production',
            'marvel', 'disney', 'pixar', 'dreamworks', 'paramount', 'mgm',
            
            # TV networks
            'network', 'channel', 'broadcasting', 'television', 'tv', 'media',
            'news', 'sports', 'espn', 'cnn', 'bbc', 'fox', 'nbc', 'abc', 'cbs',
            
            # Gaming companies
            'nintendo', 'playstation', 'xbox', 'ubisoft', 'ea', 'activision',
            
            # Tech companies
            'apple', 'google', 'microsoft', 'amazon', 'facebook', 'tesla',
            'samsung', 'huawei', 'xiaomi', 'oneplus'
        ]
        
        channel_lower = video_data['channel'].lower()
        
        for blacklist in blacklisted_channels:
            if blacklist in channel_lower:
                print(f"🚫 BLOCKED by channel: '{blacklist}' in '{video_data['channel']}'")
                return False
        
        # STRICT view requirement - only viral content
        if video_data['views'] < 1000000:  # 1M+ views minimum
            print(f"🚫 BLOCKED by views: {video_data['views']:,} < 1M")
            return False
        
        # Additional safety checks
        title_words = text.split()
        
        # Block if title has suspicious patterns
        suspicious_patterns = [
            'ft', 'feat', 'vs', 'x', '©', '®', '™', 'official', 'exclusive',
            'premiere', 'trailer', 'teaser', 'clip', 'full', 'complete',
            'hd', '4k', '1080p', 'remastered', 'director\'s cut'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in title_words:
                print(f"🚫 BLOCKED by pattern: '{pattern}' in title")
                return False
        
        # Block channels with numbers (often official channels)
        if any(char.isdigit() for char in video_data['channel']):
            print(f"🚫 BLOCKED: Channel has numbers '{video_data['channel']}'")
            return False
        
        # Block very short channel names (often official)
        if len(video_data['channel']) < 5:
            print(f"🚫 BLOCKED: Channel name too short '{video_data['channel']}'")
            return False
        
        print(f"✅ ULTRA SAFE: {video_data['title'][:30]}... by {video_data['channel']}")
        return True
    
    def _generate_emergency_title(self, video_data):
        """Generate unique title when AI fails - using Groq backup"""
        try:
            # Emergency Groq call with simpler prompt
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            # Multiple creative prompts to try
            prompts = [
                f"Create a unique, catchy YouTube Shorts title (max 50 chars) for content about: {video_data['title'][:40]}",
                f"Generate viral YouTube title for: {video_data['channel']} content. Make it unique and engaging.",
                f"Create clickbait title for trending video. Original: {video_data['title'][:30]}. Make it different and viral.",
                f"Generate unique YouTube Shorts title. Topic: {video_data['title'][:35]}. Make it catchy and original.",
                f"Create engaging title for viral content. Channel: {video_data['channel']}. Make it unique and trending."
            ]
            
            # Try each prompt
            for prompt in prompts:
                try:
                    data = {
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 80,
                        "temperature": 0.9
                    }
                    
                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    
                    if response.status_code == 200:
                        ai_title = response.json()['choices'][0]['message']['content'].strip()
                        
                        # Clean the title
                        ai_title = ai_title.replace('"', '').replace("'", "").strip()
                        if ai_title.startswith('Title:'):
                            ai_title = ai_title.replace('Title:', '').strip()
                        
                        # Ensure it's not too long
                        if len(ai_title) > 60:
                            ai_title = ai_title[:57] + "..."
                        
                        if ai_title and len(ai_title) > 10:  # Valid title
                            # Generate unique tags
                            unique_tags = self._generate_unique_tags(video_data, ai_title)
                            description = f"Amazing viral content! 🔥\n\nOriginal by: {video_data['channel']}\n\n{unique_tags}"
                            print(f"🤖 Emergency AI title: {ai_title}")
                            return ai_title, description
                            
                except Exception as e:
                    print(f"❌ Prompt failed: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Emergency AI failed: {e}")
        
        # Ultimate fallback - creative unique titles
        import time
        import random
        
        # Creative title templates
        templates = [
            "Mind-Blowing Moment #{id} 🤯",
            "Epic Discovery #{id} 🔥", 
            "Incredible Find #{id} ⚡",
            "Amazing Revelation #{id} 🚀",
            "Shocking Truth #{id} 😱",
            "Unbelievable Fact #{id} 🤔",
            "Crazy Reality #{id} 🌟",
            "Wild Discovery #{id} 🎯",
            "Insane Moment #{id} 💥",
            "Stunning Truth #{id} ✨",
            "Jaw-Dropping #{id} 🎪",
            "Game Changer #{id} 🎮",
            "Plot Twist #{id} 🌀",
            "Hidden Secret #{id} 🔍",
            "Life Hack #{id} 💡"
        ]
        
        # Generate unique ID
        unique_id = int(time.time()) % 10000
        template = random.choice(templates)
        title = template.replace("{id}", str(unique_id))
        
        # Generate unique tags for fallback
        unique_tags = self._generate_unique_tags(video_data, title)
        description = f"Incredible content that will blow your mind! 🤯\n\nFrom: {video_data['channel']}\n\n{unique_tags}"
        
        print(f"🎲 Fallback title: {title}")
        return title, description
    
    def _generate_unique_tags(self, video_data, title):
        """Generate unique hashtags based on content"""
        import random
        import time
        
        # Base tags (always included)
        base_tags = ["#shorts", "#viral", "#trending"]
        
        # Category-based tags
        category_tags = {
            'tech': ["#technology", "#innovation", "#gadgets", "#tech", "#future", "#ai", "#coding", "#programming"],
            'entertainment': ["#entertainment", "#fun", "#comedy", "#amazing", "#cool", "#awesome", "#epic", "#wow"],
            'general': ["#content", "#creator", "#youtube", "#fyp", "#explore", "#discover", "#watch", "#video"]
        }
        
        # Emotion/Action tags
        emotion_tags = ["#mindblown", "#incredible", "#shocking", "#unbelievable", "#amazing", "#epic", "#crazy", "#wild", "#insane", "#stunning"]
        
        # Time-based unique tags
        current_time = int(time.time())
        time_tags = [
            f"#{current_time % 1000}viral",
            f"#trend{current_time % 100}",
            f"#moment{current_time % 500}",
            f"#epic{current_time % 200}"
        ]
        
        # Content-based tags (from title keywords)
        title_lower = title.lower()
        content_tags = []
        
        # Smart tag generation based on title content
        if any(word in title_lower for word in ['mind', 'brain', 'think']):
            content_tags.extend(["#mindblowing", "#psychology", "#brain"])
        if any(word in title_lower for word in ['secret', 'hidden', 'mystery']):
            content_tags.extend(["#secrets", "#mystery", "#hidden", "#reveal"])
        if any(word in title_lower for word in ['fact', 'truth', 'real']):
            content_tags.extend(["#facts", "#truth", "#reality", "#knowledge"])
        if any(word in title_lower for word in ['hack', 'tip', 'trick']):
            content_tags.extend(["#lifehacks", "#tips", "#tricks", "#hacks"])
        if any(word in title_lower for word in ['game', 'play', 'win']):
            content_tags.extend(["#gaming", "#games", "#play", "#win"])
        
        # Channel-based tags
        channel_tags = []
        channel_lower = video_data['channel'].lower()
        if len(channel_lower) > 3:
            # Create unique channel-based tag
            channel_tag = f"#{channel_lower[:8].replace(' ', '')}"
            if channel_tag.isalnum() or '#' in channel_tag:
                channel_tags.append(channel_tag)
        
        # Views-based tags
        views = video_data['views']
        if views > 10000000:  # 10M+
            view_tags = ["#viral10m", "#megaviral", "#trending10m"]
        elif views > 5000000:  # 5M+
            view_tags = ["#viral5m", "#superviral", "#trending5m"]
        elif views > 1000000:  # 1M+
            view_tags = ["#viral1m", "#millionviews", "#trending1m"]
        else:
            view_tags = ["#viralcontent", "#trending"]
        
        # Random unique tags
        random_tags = [
            f"#unique{random.randint(100, 999)}",
            f"#content{random.randint(10, 99)}",
            f"#viral{random.randint(1000, 9999)}",
            f"#trend{random.randint(100, 999)}"
        ]
        
        # Combine all tags
        all_tags = []
        all_tags.extend(base_tags)
        all_tags.extend(random.sample(emotion_tags, 2))  # 2 random emotion tags
        all_tags.extend(random.sample(time_tags, 1))     # 1 time-based tag
        all_tags.extend(content_tags[:3])                # Max 3 content tags
        all_tags.extend(channel_tags[:1])                # Max 1 channel tag
        all_tags.extend(random.sample(view_tags, 1))     # 1 view-based tag
        all_tags.extend(random.sample(random_tags, 2))   # 2 random unique tags
        
        # Add category tags based on video type
        if 'tech' in video_data.get('category', '').lower():
            all_tags.extend(random.sample(category_tags['tech'], 2))
        elif 'entertainment' in video_data.get('category', '').lower():
            all_tags.extend(random.sample(category_tags['entertainment'], 2))
        else:
            all_tags.extend(random.sample(category_tags['general'], 2))
        
        # Remove duplicates and limit to 25 tags (YouTube limit is 30)
        unique_tags = list(dict.fromkeys(all_tags))[:25]
        
        # Join tags with spaces
        tag_string = " ".join(unique_tags)
        
        print(f"🏷️ Generated {len(unique_tags)} unique tags")
        return tag_string
    
    def download_video(self, url, video_id):
        """Download video"""
        try:
            filename = f"downloads/{video_id}.mp4"
            
            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[ext=mp4]',
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return filename if os.path.exists(filename) else None
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def create_short(self, video_path, video_id):
        """Smart short creation - cut videos, keep shorts as-is"""
        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration

                print(f"⏱️ Video duration: {duration:.1f}s")

                # Smart processing based on duration
                if duration <= 60:
                    # It's already a short - don't cut, just resize if needed
                    print("📱 Source is already a short - keeping full video")
                    clip = video
                else:
                    # It's a long video - cut to 60 seconds
                    print("✂️ Long video detected - cutting to 60 seconds")

                    # Smart segment selection for long videos
                    if duration > 120:
                        # Skip intro (first 30s) and outro (last 30s)
                        start_time = random.uniform(30, duration - 90)
                    else:
                        # For videos 60-120s, start from 10s
                        start_time = 10

                    end_time = min(start_time + 60, duration - 10)
                    clip = video.subclip(start_time, end_time)
                    print(f"✂️ Cut segment: {start_time:.1f}s to {end_time:.1f}s")

                # Resize for shorts format (9:16)
                resized_clip = self._resize_for_shorts(clip)

                output_path = f"shorts/short_{video_id}.mp4"
                resized_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=30,
                    verbose=False,
                    logger=None
                )

                print(f"✅ Short created: {output_path}")
                return output_path

        except Exception as e:
            print(f"❌ Short creation failed: {e}")
            return None
    
    def _resize_for_shorts(self, clip):
        """Resize for 9:16 format"""
        target_width, target_height = 1080, 1920
        current_width, current_height = clip.size
        current_ratio = current_width / current_height
        target_ratio = target_width / target_height
        
        if current_ratio > target_ratio:
            new_width = int(current_height * target_ratio)
            x_center = current_width // 2
            x1 = x_center - new_width // 2
            x2 = x_center + new_width // 2
            clip = clip.crop(x1=x1, x2=x2)
        else:
            new_height = int(current_width / target_ratio)
            y_center = current_height // 2
            y1 = y_center - new_height // 2
            y2 = y_center + new_height // 2
            clip = clip.crop(y1=y1, y2=y2)
        
        return clip.resize((target_width, target_height))
    
    def generate_viral_content(self, video_data):
        """Generate viral titles with AI"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Create viral YouTube Shorts content:

Original: "{video_data['title']}" by {video_data['channel']}
Views: {video_data['views']:,}

Create:
TITLE: (max 60 chars, viral, clickbait)
DESCRIPTION: (2-3 lines with hashtags)

Make it trending and viral!"""

            data = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.9
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                
                title = ""
                description = ""
                
                for line in content.split('\n'):
                    if line.startswith('TITLE:'):
                        title = line.replace('TITLE:', '').strip()
                    elif line.startswith('DESCRIPTION:'):
                        description = line.replace('DESCRIPTION:', '').strip()
                
                if title and description:
                    # Add unique tags to AI generated content
                    unique_tags = self._generate_unique_tags(video_data, title)
                    description = description + f"\n\n{unique_tags}"
                    return title, description
            
        except Exception as e:
            print(f"❌ AI failed: {e}")
        
        # If AI fails, try again with simpler prompt
        try:
            simple_prompt = f"Create viral YouTube title for: {video_data['title'][:50]}"
            simple_data = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": simple_prompt}],
                "max_tokens": 100,
                "temperature": 0.8
            }

            response = requests.post(url, headers=headers, json=simple_data)
            if response.status_code == 200:
                ai_title = response.json()['choices'][0]['message']['content'].strip()
                if ai_title:
                    unique_tags = self._generate_unique_tags(video_data, ai_title)
                    description = f"Amazing content from {video_data['channel']}! 🔥\n\n{unique_tags}"
                    return ai_title, description
        except:
            pass

        # Last resort - generate unique title with Groq AI
        return self._generate_emergency_title(video_data)

    def authenticate_youtube(self):
        """YouTube authentication"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        creds = None
        token_file = 'credentials/token.pickle'

        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    print("🔄 Creating new authentication...")
                    creds = None
            
            if not creds or not creds.valid:
                credentials_info = {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
                    }
                }

                with open('credentials/credentials.json', 'w') as f:
                    json.dump(credentials_info, f)

                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.upload_youtube = build('youtube', 'v3', credentials=creds)
        return True

    def upload_short(self, video_path, title, description):
        """Upload to YouTube"""
        if not self.upload_youtube:
            if not self.authenticate_youtube():
                return False

        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': ['shorts', 'viral', 'trending', 'fyp'],
                    'categoryId': '24'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.upload_youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = request.execute()
            return f"https://www.youtube.com/watch?v={response['id']}"

        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False

    def process_tech_video(self):
        """Process one tech video"""
        if self.daily_tech_uploads >= self.max_tech_uploads:
            print(f"✅ Tech limit reached: {self.daily_tech_uploads}/{self.max_tech_uploads}")
            return False

        print(f"\n🔧 Processing Tech video {self.daily_tech_uploads + 1}/{self.max_tech_uploads}")

        # Get tech videos
        videos = self.get_trending_videos_by_category('28')  # Science & Technology
        if not videos:
            return False

        return self._process_video_from_list(videos, 'tech')

    def process_entertainment_video(self):
        """Process one entertainment video"""
        if self.daily_entertainment_uploads >= self.max_entertainment_uploads:
            print(f"✅ Entertainment limit reached: {self.daily_entertainment_uploads}/{self.max_entertainment_uploads}")
            return False

        print(f"\n🎬 Processing Entertainment video {self.daily_entertainment_uploads + 1}/{self.max_entertainment_uploads}")

        # Get entertainment videos
        videos = self.get_trending_videos_by_category('24')  # Entertainment
        if not videos:
            return False

        return self._process_video_from_list(videos, 'entertainment')

    def _process_video_from_list(self, videos, category_type):
        """Process video from given list"""

        # Process first available
        for video in videos:
            if video['id'] in self.processed_videos:
                print(f"⏭️ Skipping already processed: {video['title'][:30]}...")
                continue

            print(f"📹 {video['title'][:40]}... ({video['views']:,} views)")

            # Download
            video_path = self.download_video(video['url'], video['id'])
            if not video_path:
                continue

            # Create short
            short_path = self.create_short(video_path, video['id'])
            if not short_path:
                self._cleanup(video_path)
                continue

            # Generate content with uniqueness check
            title, description = self.generate_viral_content(video)

            # Ensure title is unique
            original_title = title
            counter = 1
            while title.lower() in [t.lower() for t in self.uploaded_titles]:
                title = f"{original_title} #{counter}"
                counter += 1

            print(f"📝 {title}")

            # Upload
            upload_url = self.upload_short(short_path, title, description)

            if upload_url:
                # Update counters based on category
                if category_type == 'tech':
                    self.daily_tech_uploads += 1
                    category_emoji = "🔧"
                else:
                    self.daily_entertainment_uploads += 1
                    category_emoji = "🎬"

                # Save to permanent storage
                self.processed_videos.add(video['id'])
                self.uploaded_titles.add(title)
                self._save_processed_video(video['id'])
                self._save_uploaded_title(title)
                print(f"💾 Saved video ID: {video['id']} to processed list")

                # Log
                with open('upload_log.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now()}: [{category_type.upper()}] {title} - {upload_url}\n")

                total_today = self.daily_tech_uploads + self.daily_entertainment_uploads
                print(f"🎉 {category_emoji} {category_type.upper()} UPLOADED!")
                print(f"📊 Today: {self.daily_tech_uploads}/5 Tech + {self.daily_entertainment_uploads}/5 Entertainment = {total_today}/10 Total")
                print(f"🔗 {upload_url}")

                # Send Telegram notification
                telegram_msg = f"""
🎉 <b>{category_emoji} {category_type.upper()} VIDEO UPLOADED!</b>

📝 <b>Title:</b> {title}
🔗 <b>Link:</b> {upload_url}
📊 <b>Progress:</b> {self.daily_tech_uploads}/5 Tech + {self.daily_entertainment_uploads}/5 Entertainment = {total_today}/10 Total
⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
                self.send_telegram_message(telegram_msg)

                self._cleanup(video_path, short_path)
                return True

            self._cleanup(video_path, short_path)

        return False

    def _cleanup(self, *files):
        """Clean files"""
        for file in files:
            try:
                if file and os.path.exists(file):
                    os.remove(file)
            except:
                pass

    def reset_daily(self):
        """Reset daily counters"""
        self.daily_tech_uploads = 0
        self.daily_entertainment_uploads = 0
        print(f"🔄 New day! Target: {self.max_tech_uploads} Tech + {self.max_entertainment_uploads} Entertainment = 10 videos")

    def run_forever(self):
        """Run continuous automation - NEVER STOPS"""
        print("🚀 YOUTUBE BOT STARTED!")
        print("⚡ NEVER STOPS RUNNING!")
        print("📅 5-8 videos per day")
        print("🛡️ Copyright protected")
        print("🤖 Full AI automation")
        print("=" * 40)

        # Schedule
        schedule.every().day.at("00:00").do(self.reset_daily)

        # Tech upload times (5 times daily)
        tech_times = ["08:00", "12:00", "16:00", "20:00", "23:00"]
        for time_slot in tech_times:
            schedule.every().day.at(time_slot).do(self.process_tech_video)

        # Entertainment upload times (5 times daily)
        entertainment_times = ["10:00", "14:00", "18:00", "21:00", "23:30"]
        for time_slot in entertainment_times:
            schedule.every().day.at(time_slot).do(self.process_entertainment_video)

        print(f"⏰ Tech uploads: {tech_times}")
        print(f"⏰ Entertainment uploads: {entertainment_times}")
        print("🎲 + Random uploads")
        print("\n🔄 Running forever...")

        # NEVER STOP LOOP
        while True:
            try:
                schedule.run_pending()

                # Random uploads
                if random.random() < 0.1:
                    total_today = self.daily_tech_uploads + self.daily_entertainment_uploads
                    if total_today < 10:
                        print("🎲 Random upload!")
                        # Randomly choose tech or entertainment
                        if self.daily_tech_uploads < 5 and (self.daily_entertainment_uploads >= 5 or random.choice([True, False])):
                            self.process_tech_video()
                        elif self.daily_entertainment_uploads < 5:
                            self.process_entertainment_video()

                time.sleep(60)

                # Hourly status
                if datetime.now().minute == 0:
                    total_today = self.daily_tech_uploads + self.daily_entertainment_uploads
                    print(f"⏰ {datetime.now().strftime('%H:%M')} - {self.daily_tech_uploads}/5 Tech + {self.daily_entertainment_uploads}/5 Entertainment = {total_today}/10 Total")

            except KeyboardInterrupt:
                print("\n⏹️ Bot stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(300)
                continue

# MAIN EXECUTION
if __name__ == "__main__":
    print("🎯 YOUTUBE AUTOMATION BOT")
    print("🔥 24/7 automation")
    print("📈 5-8 uploads daily")
    print("🛡️ Copyright safe")
    print("🤖 AI powered")

    # Choose mode
    mode = input("\n1. Run FOREVER (continuous)\n2. Test single video\nChoice (1/2): ").strip()

    bot = YouTubeBot()

    if mode == "2":
        print("\n🧪 TESTING SINGLE VIDEO...")
        print("Choose category:")
        print("1. Tech")
        print("2. Entertainment")
        cat_choice = input("Choice (1/2): ").strip()

        if cat_choice == "1":
            success = bot.process_tech_video()
        else:
            success = bot.process_entertainment_video()

        if success:
            print("🎉 TEST SUCCESSFUL!")
        else:
            print("❌ TEST FAILED")
    else:
        print("\n🚀 STARTING CONTINUOUS MODE...")
        time.sleep(3)
        bot.run_forever()
