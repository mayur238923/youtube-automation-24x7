#!/usr/bin/env python3
"""
YouTube Automation System
Automatically finds trending videos, creates shorts, and uploads them
"""

import os
import random
import time
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pytube import YouTube
from moviepy.editor import VideoFileClip
import requests

# Load environment variables
load_dotenv()

class YouTubeAutomation:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.client_id = os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')

        # YouTube API for reading (trending videos)
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)

        # YouTube API for uploading (OAuth)
        self.upload_youtube = None

        # Create directories
        os.makedirs('downloads', exist_ok=True)
        os.makedirs('shorts', exist_ok=True)
        os.makedirs('credentials', exist_ok=True)
        
    def get_trending_videos(self, max_results=10):
        """Get trending videos from YouTube"""
        print("🔍 Fetching trending videos...")
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                chart='mostPopular',
                regionCode='US',
                maxResults=max_results,
                videoCategoryId='24'  # Entertainment category
            )
            
            response = request.execute()
            videos = []
            
            for item in response['items']:
                # Parse duration
                duration = self._parse_duration(item['contentDetails']['duration'])
                
                # Filter videos (5-30 minutes)
                if 300 <= duration <= 1800:  # 5-30 minutes
                    video_data = {
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'channel': item['snippet']['channelTitle'],
                        'views': int(item['statistics'].get('viewCount', 0)),
                        'duration': duration,
                        'url': f"https://www.youtube.com/watch?v={item['id']}"
                    }
                    videos.append(video_data)
            
            print(f"✅ Found {len(videos)} suitable videos")
            return videos
            
        except Exception as e:
            print(f"❌ Error fetching trending videos: {e}")
            return []
    
    def _parse_duration(self, duration_str):
        """Parse YouTube duration format PT1H2M3S to seconds"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def download_video(self, url, video_id):
        """Download video from YouTube"""
        print(f"⬇️ Downloading video: {video_id}")
        
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            if not stream:
                print("❌ No suitable stream found")
                return None
            
            filename = f"downloads/{video_id}.mp4"
            stream.download(output_path='downloads', filename=f"{video_id}.mp4")
            
            print(f"✅ Downloaded: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def create_short(self, video_path, video_id):
        """Create a 60-second short from video"""
        print(f"✂️ Creating short from: {video_path}")
        
        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration
                
                # Find best 60-second segment (avoid first/last 30 seconds)
                start_time = random.uniform(30, max(30, duration - 90))
                end_time = min(start_time + 60, duration)
                
                # Extract clip
                clip = video.subclip(start_time, end_time)
                
                # Resize for shorts (9:16 aspect ratio)
                clip_resized = self._resize_for_shorts(clip)
                
                # Save short
                output_path = f"shorts/short_{video_id}.mp4"
                clip_resized.write_videofile(
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
            print(f"❌ Error creating short: {e}")
            return None
    
    def _resize_for_shorts(self, clip):
        """Resize video for YouTube Shorts (9:16)"""
        target_width = 1080
        target_height = 1920
        
        # Get current dimensions
        current_width, current_height = clip.size
        current_ratio = current_width / current_height
        target_ratio = target_width / target_height
        
        if current_ratio > target_ratio:
            # Video is too wide, crop sides
            new_width = int(current_height * target_ratio)
            x_center = current_width // 2
            x1 = x_center - new_width // 2
            x2 = x_center + new_width // 2
            clip = clip.crop(x1=x1, x2=x2)
        else:
            # Video is too tall, crop top/bottom  
            new_height = int(current_width / target_ratio)
            y_center = current_height // 2
            y1 = y_center - new_height // 2
            y2 = y_center + new_height // 2
            clip = clip.crop(y1=y1, y2=y2)
        
        # Resize to target dimensions
        return clip.resize((target_width, target_height))
    
    def generate_title_description(self, original_title, channel_name):
        """Generate AI title and description using Groq"""
        print("🤖 Generating AI content...")
        
        if not self.groq_api_key:
            # Fallback titles if no API key
            titles = [
                f"Amazing Moment from {channel_name} 🔥",
                f"You Won't Believe This! #{random.randint(1,100)}",
                f"Viral Content Alert! 🚨",
                f"Must Watch: {original_title[:30]}...",
                f"Trending Now: Epic Moment! ⚡"
            ]
            
            descriptions = [
                f"Epic moment from {channel_name}! 🔥\n\n#shorts #viral #trending #amazing",
                f"You have to see this! 😱\n\nOriginal: {channel_name}\n\n#shorts #viral #mustwatch",
                f"This is going viral! 🚀\n\n#shorts #trending #viral #epic"
            ]
            
            return random.choice(titles), random.choice(descriptions)
        
        try:
            # Use Groq API for better content
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Create a catchy YouTube Shorts title and description for a video clip from "{original_title}" by {channel_name}.

Requirements:
- Title: Max 60 characters, engaging, clickbait-style
- Description: 2-3 lines with relevant hashtags
- Make it viral and trending focused

Format:
TITLE: [your title]
DESCRIPTION: [your description]"""

            data = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.8
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                
                # Parse response
                lines = content.split('\n')
                title = ""
                description = ""
                
                for line in lines:
                    if line.startswith('TITLE:'):
                        title = line.replace('TITLE:', '').strip()
                    elif line.startswith('DESCRIPTION:'):
                        description = line.replace('DESCRIPTION:', '').strip()
                
                if title and description:
                    print(f"✅ AI content generated")
                    return title, description
            
        except Exception as e:
            print(f"❌ AI generation error: {e}")
        
        # Fallback
        return f"Amazing Moment! 🔥 #{random.randint(1,100)}", f"Epic content from {channel_name}! 🚀\n\n#shorts #viral #trending"

    def authenticate_upload(self):
        """Authenticate for YouTube upload"""
        print("🔐 Authenticating for YouTube upload...")

        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

        creds = None
        token_file = 'credentials/token.pickle'

        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Create credentials.json file
                credentials_info = {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
                    }
                }

                import json
                with open('credentials/credentials.json', 'w') as f:
                    json.dump(credentials_info, f)

                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        # Build YouTube service for uploading
        self.upload_youtube = build('youtube', 'v3', credentials=creds)
        print("✅ Authentication successful!")
        return True

    def upload_to_youtube(self, video_path, title, description):
        """Upload video to YouTube"""
        print(f"📤 Uploading: {title}")

        if not self.upload_youtube:
            if not self.authenticate_upload():
                return False

        try:
            tags = ["shorts", "viral", "trending", "entertainment", "funny"]

            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '24'  # Entertainment
                },
                'status': {
                    'privacyStatus': 'public',  # or 'private' for testing
                    'selfDeclaredMadeForKids': False
                }
            }

            # Upload video
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

            request = self.upload_youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = request.execute()

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            print(f"✅ Upload successful!")
            print(f"🔗 Video URL: {video_url}")

            return video_url

        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def run_automation(self):
        """Run the complete automation process"""
        print("🚀 Starting YouTube Automation...")
        
        # Get trending videos
        videos = self.get_trending_videos(5)
        
        if not videos:
            print("❌ No videos found")
            return
        
        # Process each video
        for i, video in enumerate(videos[:3]):  # Process max 3 videos
            print(f"\n📹 Processing video {i+1}/3: {video['title'][:50]}...")
            
            # Download video
            video_path = self.download_video(video['url'], video['id'])
            if not video_path:
                continue
            
            # Create short
            short_path = self.create_short(video_path, video['id'])
            if not short_path:
                continue
            
            # Generate content
            title, description = self.generate_title_description(video['title'], video['channel'])

            print(f"📝 Title: {title}")
            print(f"📝 Description: {description[:100]}...")

            # Upload to YouTube
            upload_url = self.upload_to_youtube(short_path, title, description)

            if upload_url:
                print(f"🎉 Successfully uploaded: {upload_url}")
            else:
                print(f"❌ Upload failed, but short saved: {short_path}")

            # Clean up files
            try:
                os.remove(video_path)
                if upload_url:  # Only delete if uploaded successfully
                    os.remove(short_path)
            except:
                pass

            # Wait between uploads (YouTube rate limiting)
            time.sleep(10)
        
        print("\n🎉 Automation complete! Check 'shorts' folder for videos.")

if __name__ == "__main__":
    automation = YouTubeAutomation()
    automation.run_automation()
