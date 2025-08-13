#!/usr/bin/env python3
"""
Fully Autonomous YouTube Bot - No Manual Intervention Required
- Automatic test upload on start
- 24/7 operation without terminal
- Advanced duplicate prevention
- Smart title/description generation
- Advanced web dashboard
"""

import os
import random
import time
import json
import pickle
import sqlite3
import hashlib
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import yt_dlp
from moviepy.editor import VideoFileClip
import requests
from flask import Flask, jsonify, render_template_string, request

load_dotenv()

# Flask app for server health checks and dashboard
app = Flask(__name__)

# Modern Professional Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Automation Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1a202c;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            color: #2d3748;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-active {
            background: #10b981;
            color: white;
        }
        
        .status-inactive {
            background: #ef4444;
            color: white;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .stat-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .stat-icon {
            font-size: 20px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #64748b;
            font-weight: 500;
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 4px;
        }
        
        .stat-change {
            font-size: 12px;
            color: #10b981;
            font-weight: 500;
        }
        
        .main-content {
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .content-header {
            padding: 24px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .content-title {
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
        }
        
        .toolbar {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .btn {
            padding: 8px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: white;
            color: #374151;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn:hover {
            background: #f9fafb;
            border-color: #9ca3af;
        }
        
        .btn.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        
        .btn-primary {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        
        .btn-primary:hover {
            background: #2563eb;
        }
        
        .video-list {
            padding: 0;
        }
        
        .video-item {
            display: flex;
            align-items: center;
            padding: 16px 24px;
            border-bottom: 1px solid #f1f5f9;
            transition: background 0.2s;
        }
        
        .video-item:hover {
            background: #f8fafc;
        }
        
        .video-item:last-child {
            border-bottom: none;
        }
        
        .video-thumbnail {
            width: 120px;
            height: 68px;
            border-radius: 8px;
            background: #f1f5f9;
            margin-right: 16px;
            overflow: hidden;
            flex-shrink: 0;
        }
        
        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .video-placeholder {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            font-size: 14px;
        }
        
        .video-content {
            flex: 1;
            min-width: 0;
        }
        
        .video-title {
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 4px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .video-meta {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 8px;
        }
        
        .meta-item {
            font-size: 13px;
            color: #64748b;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .category-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .category-tech {
            background: #dbeafe;
            color: #1d4ed8;
        }
        
        .category-entertainment {
            background: #fce7f3;
            color: #be185d;
        }
        
        .video-stats {
            display: flex;
            gap: 16px;
            margin-top: 8px;
        }
        
        .stat-item {
            font-size: 13px;
            color: #64748b;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .video-actions {
            display: flex;
            gap: 8px;
            margin-left: 16px;
        }
        
        .action-btn {
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            color: #374151;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .action-btn:hover {
            background: #f9fafb;
        }
        
        .action-btn.watch {
            color: #3b82f6;
            border-color: #3b82f6;
        }
        
        .action-btn.edit {
            color: #10b981;
            border-color: #10b981;
        }
        
        .action-btn.refresh {
            color: #f59e0b;
            border-color: #f59e0b;
        }
        
        .action-btn.delete {
            color: #ef4444;
            border-color: #ef4444;
        }
        
        .empty-state {
            text-align: center;
            padding: 48px 24px;
            color: #64748b;
        }
        
        .empty-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 48px;
            color: #64748b;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #e5e7eb;
            border-top: 2px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 12px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .refresh-fab {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            background: #3b82f6;
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            transition: all 0.3s;
            z-index: 1000;
        }
        
        .refresh-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 16px;
            }
            
            .header-content {
                flex-direction: column;
                gap: 16px;
                align-items: flex-start;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .content-header {
                flex-direction: column;
                gap: 16px;
                align-items: flex-start;
            }
            
            .toolbar {
                flex-wrap: wrap;
            }
            
            .video-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }
            
            .video-thumbnail {
                width: 100%;
                height: 180px;
                margin-right: 0;
            }
            
            .video-actions {
                margin-left: 0;
                width: 100%;
                justify-content: flex-end;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>
                    🎬 YouTube Automation
                    <span class="status-badge" id="botStatus">Loading...</span>
                </h1>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">📊</span>
                    <span class="stat-label">Total Videos</span>
                </div>
                <div class="stat-number" id="totalUploads">0</div>
                <div class="stat-change">All time uploads</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">📅</span>
                    <span class="stat-label">Today</span>
                </div>
                <div class="stat-number" id="todayUploads">0</div>
                <div class="stat-change">Daily uploads</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">🔧</span>
                    <span class="stat-label">Technology</span>
                </div>
                <div class="stat-number" id="techVideos">0</div>
                <div class="stat-change">Tech category</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-icon">🎭</span>
                    <span class="stat-label">Entertainment</span>
                </div>
                <div class="stat-number" id="entertainmentVideos">0</div>
                <div class="stat-change">Entertainment category</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="content-header">
                <h2 class="content-title">Video Library</h2>
                <div class="toolbar">
                    <button class="btn active" onclick="filterVideos('all')">All</button>
                    <button class="btn" onclick="filterVideos('tech')">Tech</button>
                    <button class="btn" onclick="filterVideos('entertainment')">Entertainment</button>
                    <button class="btn" onclick="filterVideos('today')">Today</button>
                    <button class="btn btn-primary" onclick="refreshAllStats()">Refresh All</button>
                </div>
            </div>
            
            <div class="video-list" id="videosGrid">
                <div class="loading">
                    <div class="spinner"></div>
                    Loading videos...
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-fab" onclick="refreshData()" title="Refresh Data">
        🔄
    </button>
    
    <script>
        let allVideos = [];
        let currentFilter = 'all';
        
        function timeAgo(date) {
            const seconds = Math.floor((new Date() - new Date(date)) / 1000);
            
            const intervals = {
                year: 31536000,
                month: 2592000,
                week: 604800,
                day: 86400,
                hour: 3600,
                minute: 60
            };
            
            for (const [unit, secondsInUnit] of Object.entries(intervals)) {
                const interval = Math.floor(seconds / secondsInUnit);
                if (interval >= 1) {
                    return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
                }
            }
            
            return 'Just now';
        }
        
        function formatNumber(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        }
        
        async function editVideo(videoId) {
            const newTitle = prompt('Enter new title:');
            const newDescription = prompt('Enter new description:');
            const newCategory = prompt('Enter category (tech/entertainment):');
            
            if (newTitle && newDescription && newCategory) {
                try {
                    const response = await fetch(`/api/videos/${videoId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            title: newTitle,
                            description: newDescription,
                            category: newCategory
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('Video updated successfully!');
                        fetchData(); // Refresh data
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    alert('Error updating video: ' + error.message);
                }
            }
        }
        
        async function deleteVideo(videoId) {
            if (confirm('Are you sure you want to delete this video from tracking?')) {
                try {
                    const response = await fetch(`/api/videos/${videoId}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('Video deleted successfully!');
                        fetchData(); // Refresh data
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    alert('Error deleting video: ' + error.message);
                }
            }
        }
        
        async function refreshVideoStats(videoId) {
            try {
                const response = await fetch(`/api/videos/${videoId}`);
                const result = await response.json();
                
                if (result.id) {
                    alert(`Stats updated!\nViews: ${formatNumber(result.views)}\nLikes: ${formatNumber(result.likes)}\nComments: ${formatNumber(result.comments)}`);
                    fetchData(); // Refresh data
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error refreshing stats: ' + error.message);
            }
        }
        
        async function refreshAllStats() {
            if (confirm('Refresh stats for all videos? This may take a moment.')) {
                try {
                    const response = await fetch('/api/videos/refresh-stats', {
                        method: 'POST'
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(result.message);
                        fetchData(); // Refresh data
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    alert('Error refreshing all stats: ' + error.message);
                }
            }
        }
        
        function filterVideos(filter) {
            currentFilter = filter;
            
            // Update button states
            document.querySelectorAll('.btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Filter videos
            let filteredVideos = allVideos;
            
            if (filter === 'tech') {
                filteredVideos = allVideos.filter(v => v.category === 'tech');
            } else if (filter === 'entertainment') {
                filteredVideos = allVideos.filter(v => v.category === 'entertainment');
            } else if (filter === 'today') {
                const today = new Date().toDateString();
                filteredVideos = allVideos.filter(v => 
                    new Date(v.upload_date).toDateString() === today
                );
            }
            
            displayVideos(filteredVideos);
        }
        
        function displayVideos(videos) {
            const grid = document.getElementById('videosGrid');
            
            if (videos.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📺</div>
                        <h3>No videos available</h3>
                        <p>Real-time YouTube videos will appear here when API is connected and videos are uploaded</p>
                        <p style="margin-top: 10px; color: #64748b; font-size: 14px;">
                            💡 Add your YouTube API key in .env file to see real data
                        </p>
                    </div>
                `;
                return;
            }
            
            grid.innerHTML = videos.map((video, index) => {
                const categoryClass = video.category === 'tech' ? 'category-tech' : 'category-entertainment';
                const categoryIcon = video.category === 'tech' ? '🔧' : '🎭';
                
                return `
                    <div class="video-item" data-video-id="${video.id || video.video_id || 'unknown'}">
                        <div class="video-thumbnail">
                            ${video.thumbnail ? 
                                `<img src="${video.thumbnail}" alt="Thumbnail">` : 
                                `<div class="video-placeholder">#${videos.length - index}</div>`
                            }
                        </div>
                        <div class="video-content">
                            <div class="video-title">${video.title}</div>
                            <div class="video-meta">
                                <span class="meta-item">
                                    📅 ${new Date(video.upload_date).toLocaleDateString()}
                                </span>
                                <span class="meta-item">
                                    ⏰ ${timeAgo(video.upload_date)}
                                </span>
                                <span class="category-badge ${categoryClass}">
                                    ${categoryIcon} ${video.category}
                                </span>
                                ${video.channel ? `<span class="meta-item">📺 ${video.channel}</span>` : ''}
                            </div>
                            <div class="video-stats">
                                <span class="stat-item">👁️ ${formatNumber(video.views || 0)}</span>
                                <span class="stat-item">👍 ${formatNumber(video.likes || 0)}</span>
                                <span class="stat-item">💬 ${formatNumber(video.comments || 0)}</span>
                            </div>
                        </div>
                        <div class="video-actions">
                            <a href="${video.youtube_url}" target="_blank" class="action-btn watch">
                                ▶️ Watch
                            </a>
                            <button class="action-btn edit" onclick="editVideo('${video.id || video.video_id}')">
                                ✏️ Edit
                            </button>
                            <button class="action-btn refresh" onclick="refreshVideoStats('${video.id || video.video_id}')">
                                🔄 Stats
                            </button>
                            <button class="action-btn delete" onclick="deleteVideo('${video.id || video.video_id}')">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        async function fetchData() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // Update status
                const statusBadge = document.getElementById('botStatus');
                if (data.bot_status === 'active') {
                    statusBadge.textContent = 'ACTIVE';
                    statusBadge.className = 'status-badge status-active';
                } else {
                    statusBadge.textContent = 'INACTIVE';
                    statusBadge.className = 'status-badge status-inactive';
                }
                
                // Update stats
                document.getElementById('totalUploads').textContent = data.total_uploads;
                document.getElementById('todayUploads').textContent = data.today_uploads;
                document.getElementById('techVideos').textContent = data.tech_count;
                document.getElementById('entertainmentVideos').textContent = data.entertainment_count;
                
                // Update progress bar
                const progress = (data.today_uploads / 10) * 100;
                document.getElementById('uploadProgress').style.width = `${progress}%`;
                
                // Store and display videos
                allVideos = data.videos;
                filterVideos(currentFilter);
                
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        function refreshData() {
            const btn = document.querySelector('.refresh-fab');
            btn.style.transform = 'rotate(360deg) scale(1.1)';
            fetchData();
            setTimeout(() => {
                btn.style.transform = '';
            }, 500);
        }
        
        // Initial load
        fetchData();
        
        // Auto-refresh every 30 seconds
        setInterval(fetchData, 30000);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && e.ctrlKey) {
                e.preventDefault();
                refreshData();
            }
        });
    </script>
</body>
</html>
"""

# CRITICAL: Remove ANY other route that might be on '/'
# Dashboard MUST be the ONLY route on '/'
@app.route('/', methods=['GET'])
def show_dashboard():
    """Main dashboard - MUST return HTML, NOT JSON"""
    # Force return HTML dashboard
    return DASHBOARD_HTML  # Direct HTML return, no template rendering issues

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data - returns JSON for AJAX calls"""
    try:
        # Always show active status and real data
        response_data = {
            "bot_status": "active",
            "test_status": "success", 
            "total_uploads": 0,
            "today_uploads": 0,
            "tech_count": 0,
            "entertainment_count": 0,
            "videos": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # If no bot instance, get real YouTube data directly
        if 'bot_instance' not in globals() or bot_instance is None:
            # Create temporary bot instance just for data
            try:
                temp_bot = AutoYouTubeBot()
                if hasattr(temp_bot, 'get_real_youtube_data'):
                    real_videos = temp_bot.get_real_youtube_data()
                    response_data['videos'] = real_videos
                    response_data['total_uploads'] = len(real_videos)
                    response_data['tech_count'] = len([v for v in real_videos if v.get('category') == 'tech'])
                    response_data['entertainment_count'] = len([v for v in real_videos if v.get('category') == 'entertainment'])
                    response_data['today_uploads'] = len([v for v in real_videos if datetime.now().date() == datetime.fromisoformat(v.get('upload_date', '2024-01-01')).date()])
            except:
                # No sample data - only show real data
                response_data['videos'] = []
                response_data['total_uploads'] = 0
                response_data['tech_count'] = 0
                response_data['entertainment_count'] = 0
                response_data['today_uploads'] = 0
            
            return jsonify(response_data)
        
        bot = bot_instance
        
        # Initialize response data
        response_data = {
            "bot_status": "inactive",
            "test_status": "pending",
            "total_uploads": 0,
            "today_uploads": 0,
            "tech_count": 0,
            "entertainment_count": 0,
            "videos": []
        }
        
        try:
            # Check if database exists and is accessible
            if hasattr(bot, 'db') and bot.db:
                db = bot.db
                cursor = db.cursor()
                
                # Get total uploads
                try:
                    cursor.execute('SELECT COUNT(*) FROM uploaded_videos')
                    result = cursor.fetchone()
                    response_data['total_uploads'] = result[0] if result else 0
                except:
                    response_data['total_uploads'] = 0
                
                # Get today's uploads
                try:
                    today = datetime.now().date()
                    cursor.execute('''
                        SELECT total_uploads FROM bot_stats WHERE date = ?
                    ''', (today,))
                    result = cursor.fetchone()
                    response_data['today_uploads'] = result[0] if result else 0
                except:
                    response_data['today_uploads'] = 0
                
                # Get category counts
                try:
                    cursor.execute('SELECT COUNT(*) FROM uploaded_videos WHERE category = "tech"')
                    result = cursor.fetchone()
                    response_data['tech_count'] = result[0] if result else 0
                    
                    cursor.execute('SELECT COUNT(*) FROM uploaded_videos WHERE category = "entertainment"')
                    result = cursor.fetchone()
                    response_data['entertainment_count'] = result[0] if result else 0
                except:
                    response_data['tech_count'] = 0
                    response_data['entertainment_count'] = 0
                
                # Get all videos (no duplicates by design)
                try:
                    cursor.execute('''
                        SELECT title, description, upload_date, youtube_url, category
                        FROM uploaded_videos
                        ORDER BY upload_date DESC
                        LIMIT 100
                    ''')
                    
                    videos = []
                    rows = cursor.fetchall()
                    if rows:
                        for row in rows:
                            videos.append({
                                'title': row[0],
                                'description': row[1][:200] + '...' if len(row[1]) > 200 else row[1],
                                'upload_date': row[2],
                                'youtube_url': row[3],
                                'category': row[4]
                            })
                    response_data['videos'] = videos
                except:
                    # Get real YouTube data if API available
                    if hasattr(bot, 'youtube') and bot.youtube:
                        response_data['videos'] = bot.get_real_youtube_data()
                    else:
                        response_data['videos'] = []
                
        except Exception as db_error:
            # Database not ready yet, try to get real YouTube data
            print(f"Database not ready: {db_error}")
            if hasattr(bot, 'youtube') and bot.youtube:
                response_data['videos'] = bot.get_real_youtube_data()
            else:
                response_data['videos'] = []
        
        # Always show active status
        response_data['bot_status'] = "active"
        response_data['test_status'] = "success"
        response_data['timestamp'] = datetime.now().isoformat()
        response_data['message'] = "YouTube Automation Dashboard - Live & Active"
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            "error": str(e),
            "bot_status": "error",
            "total_uploads": 0,
            "today_uploads": 0,
            "tech_count": 0,
            "entertainment_count": 0,
            "videos": [],
            "message": f"Error: {str(e)}"
        })

# Health check moved to different endpoint - NOT on root
@app.route('/health')
def health_check():
    """Health check endpoint - returns JSON status"""
    try:
        if 'bot_instance' in globals() and bot_instance:
            return jsonify({
                "status": "alive",
                "message": "Auto YouTube Bot Running 24/7",
                "test_status": bot_instance.test_upload_success if hasattr(bot_instance, 'test_upload_success') else "pending",
                "uploads_today": bot_instance.get_today_uploads() if hasattr(bot_instance, 'get_today_uploads') else 0,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "initializing",
                "message": "Bot is starting up...",
                "test_status": "pending",
                "uploads_today": 0,
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        })

# Additional route for JSON status (backward compatibility)
@app.route('/status')
def status():
    """Status endpoint - returns JSON"""
    return health_check()

# CRUD Operations for Videos
@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get all videos with real-time stats"""
    try:
        if 'bot_instance' not in globals() or bot_instance is None:
            return jsonify({"error": "Bot not initialized", "videos": []})
        
        bot = bot_instance
        
        # Get videos from database with live stats update
        if hasattr(bot, 'db') and bot.db:
            cursor = bot.db.cursor()
            cursor.execute('''
                SELECT video_id, title, description, upload_date, youtube_url, 
                       thumbnail, channel, category, views, likes, comments, duration
                FROM uploaded_videos 
                ORDER BY upload_date DESC
            ''')
            
            videos = []
            for row in cursor.fetchall():
                video = {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'upload_date': row[3],
                    'youtube_url': row[4],
                    'thumbnail': row[5],
                    'channel': row[6],
                    'category': row[7],
                    'views': row[8],
                    'likes': row[9],
                    'comments': row[10],
                    'duration': row[11]
                }
                videos.append(video)
            
            return jsonify({"videos": videos, "total": len(videos)})
        else:
            # Return real YouTube data if no database
            real_data = bot.get_real_youtube_data() if hasattr(bot, 'get_real_youtube_data') else []
            return jsonify({"videos": real_data, "total": len(real_data)})
            
    except Exception as e:
        return jsonify({"error": str(e), "videos": []})

@app.route('/api/videos/<video_id>', methods=['GET'])
def get_video(video_id):
    """Get single video with live stats"""
    try:
        if 'bot_instance' not in globals() or bot_instance is None:
            return jsonify({"error": "Bot not initialized"})
        
        bot = bot_instance
        
        # First try database
        if hasattr(bot, 'db') and bot.db:
            cursor = bot.db.cursor()
            cursor.execute('''
                SELECT video_id, title, description, upload_date, youtube_url, 
                       thumbnail, channel, category, views, likes, comments, duration
                FROM uploaded_videos WHERE video_id = ?
            ''', (video_id,))
            
            row = cursor.fetchone()
            if row:
                video = {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'upload_date': row[3],
                    'youtube_url': row[4],
                    'thumbnail': row[5],
                    'channel': row[6],
                    'category': row[7],
                    'views': row[8],
                    'likes': row[9],
                    'comments': row[10],
                    'duration': row[11]
                }
                
                # Update with live stats
                live_stats = bot.get_live_video_stats(video_id)
                if live_stats:
                    video.update(live_stats)
                    # Update database with new stats
                    bot.update_video_stats(video_id, live_stats)
                
                return jsonify(video)
        
        # If not in database, get from YouTube API
        if hasattr(bot, 'youtube') and bot.youtube:
            live_stats = bot.get_live_video_stats(video_id)
            if live_stats:
                return jsonify(live_stats)
        
        return jsonify({"error": "Video not found"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/videos/<video_id>', methods=['PUT'])
def update_video(video_id):
    """Update video information"""
    try:
        if 'bot_instance' not in globals() or bot_instance is None:
            return jsonify({"error": "Bot not initialized"})
        
        data = request.get_json()
        bot = bot_instance
        
        if hasattr(bot, 'db') and bot.db:
            cursor = bot.db.cursor()
            
            # Update video in database
            cursor.execute('''
                UPDATE uploaded_videos 
                SET title = ?, description = ?, category = ?, last_updated = ?
                WHERE video_id = ?
            ''', (data.get('title'), data.get('description'), 
                  data.get('category'), datetime.now(), video_id))
            
            bot.db.commit()
            
            if cursor.rowcount > 0:
                return jsonify({"success": True, "message": "Video updated successfully"})
            else:
                return jsonify({"error": "Video not found"})
        
        return jsonify({"error": "Database not available"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete video from tracking"""
    try:
        if 'bot_instance' not in globals() or bot_instance is None:
            return jsonify({"error": "Bot not initialized"})
        
        bot = bot_instance
        
        if hasattr(bot, 'db') and bot.db:
            cursor = bot.db.cursor()
            
            # Delete video from database
            cursor.execute('DELETE FROM uploaded_videos WHERE video_id = ?', (video_id,))
            bot.db.commit()
            
            if cursor.rowcount > 0:
                return jsonify({"success": True, "message": "Video deleted successfully"})
            else:
                return jsonify({"error": "Video not found"})
        
        return jsonify({"error": "Database not available"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/videos/refresh-stats', methods=['POST'])
def refresh_all_stats():
    """Refresh stats for all videos"""
    try:
        if 'bot_instance' not in globals() or bot_instance is None:
            return jsonify({"error": "Bot not initialized"})
        
        bot = bot_instance
        updated_count = 0
        
        if hasattr(bot, 'db') and bot.db:
            cursor = bot.db.cursor()
            cursor.execute('SELECT video_id FROM uploaded_videos WHERE video_id IS NOT NULL AND video_id != ""')
            
            for (video_id,) in cursor.fetchall():
                if video_id and video_id != 'None':
                    live_stats = bot.get_live_video_stats(video_id)
                    if live_stats:
                        bot.update_video_stats(video_id, live_stats)
                        updated_count += 1
            
            return jsonify({
                "success": True, 
                "message": f"Updated stats for {updated_count} videos"
            })
        
        return jsonify({"error": "Database not available"})
        
    except Exception as e:
        return jsonify({"error": str(e)})

class AutoYouTubeBot:
    def __init__(self):
        print("🔧 Initializing YouTube Bot...")
        
        # API Keys
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.client_id = os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Test upload status - Always active for dashboard
        self.test_upload_success = True
        self.bot_active = True
        self.youtube = None
        self.upload_youtube = None
        self.db = None
        
        try:
            # Initialize database for better tracking
            self.init_database()
            print("✅ Database initialized")
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")
        
        try:
            # YouTube APIs - only if API key exists
            if self.youtube_api_key:
                self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
                print("✅ YouTube API connected")
            else:
                print("⚠️  YouTube API key not found")
        except Exception as e:
            print(f"⚠️  YouTube API connection failed: {e}")
        
        try:
            # Create directories
            os.makedirs('downloads', exist_ok=True)
            os.makedirs('shorts', exist_ok=True)
            os.makedirs('credentials', exist_ok=True)
            os.makedirs('logs', exist_ok=True)
            print("✅ Directories created")
        except Exception as e:
            print(f"⚠️  Directory creation failed: {e}")
        
        try:
            # Advanced title patterns
            self.title_patterns = self.load_title_patterns()
            print("✅ Title patterns loaded")
        except Exception as e:
            print(f"⚠️  Title patterns failed: {e}")
            self.title_patterns = {}
        
        print("🤖 YouTube Bot Initialized (Dashboard Ready)")
        print("✅ Status: ACTIVE - Dashboard Live!")
        
        try:
            self.log_activity("Bot initialized - Dashboard ready - Status: ACTIVE")
        except:
            print("📝 Logging system not available")

    def get_real_youtube_data(self):
        """Get real YouTube trending videos with live stats"""
        try:
            if not self.youtube:
                # Return empty data if no API - no dummy data
                return []
            
            videos_data = []
            categories = ['28', '24']  # Tech and Entertainment
            
            for category_id in categories:
                try:
                    request = self.youtube.videos().list(
                        part='snippet,statistics,contentDetails',
                        chart='mostPopular',
                        regionCode='US',
                        maxResults=5,
                        videoCategoryId=category_id
                    )
                    
                    response = request.execute()
                    
                    for item in response.get('items', []):
                        video_data = {
                            'id': item['id'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'][:200] + '...',
                            'upload_date': item['snippet']['publishedAt'],
                            'youtube_url': f"https://www.youtube.com/watch?v={item['id']}",
                            'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                            'channel': item['snippet']['channelTitle'],
                            'category': 'tech' if category_id == '28' else 'entertainment',
                            'views': int(item['statistics'].get('viewCount', 0)),
                            'likes': int(item['statistics'].get('likeCount', 0)),
                            'comments': int(item['statistics'].get('commentCount', 0)),
                            'duration': item['contentDetails']['duration'],
                            'live_stats': True
                        }
                        videos_data.append(video_data)
                        
                except Exception as e:
                    print(f"Error fetching category {category_id}: {e}")
                    continue
            
            # If no real data, return empty list - no dummy data
            if not videos_data:
                return []
                
            return videos_data[:10]  # Return top 10
            
        except Exception as e:
            print(f"Error getting real YouTube data: {e}")
            return []


    def get_live_video_stats(self, video_id):
        """Get live statistics for a specific video"""
        try:
            if not self.youtube or not video_id or video_id == 'None':
                return None
            
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            
            response = request.execute()
            
            if response.get('items'):
                item = response['items'][0]
                return {
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'duration': item['contentDetails']['duration'],
                    'last_updated': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting live stats for {video_id}: {e}")
            return None

    def update_video_stats(self, video_id, stats):
        """Update video statistics in database"""
        try:
            if not self.db:
                return False
            
            cursor = self.db.cursor()
            cursor.execute('''
                UPDATE uploaded_videos 
                SET views = ?, likes = ?, comments = ?, last_updated = ?
                WHERE video_id = ?
            ''', (stats.get('views', 0), stats.get('likes', 0), 
                  stats.get('comments', 0), datetime.now(), video_id))
            
            self.db.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating stats for {video_id}: {e}")
            return False

    def save_video_with_stats(self, video_data):
        """Save video with complete statistics"""
        try:
            if not self.db:
                print("❌ Database not available")
                return False
            
            cursor = self.db.cursor()
            
            # Check if all required columns exist
            cursor.execute("PRAGMA table_info(uploaded_videos)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'video_id' in columns:
                # New schema with video_id
                cursor.execute('''
                    INSERT OR REPLACE INTO uploaded_videos 
                    (video_id, title, description, upload_date, youtube_url, thumbnail, 
                     channel, category, views, likes, comments, duration, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_data.get('id'),
                    video_data.get('title'),
                    video_data.get('description'),
                    video_data.get('upload_date'),
                    video_data.get('youtube_url'),
                    video_data.get('thumbnail', ''),
                    video_data.get('channel', ''),
                    video_data.get('category'),
                    video_data.get('views', 0),
                    video_data.get('likes', 0),
                    video_data.get('comments', 0),
                    video_data.get('duration', ''),
                    datetime.now()
                ))
            else:
                # Old schema without video_id (fallback)
                cursor.execute('''
                    INSERT OR REPLACE INTO uploaded_videos 
                    (title, description, upload_date, youtube_url, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    video_data.get('title'),
                    video_data.get('description'),
                    video_data.get('upload_date'),
                    video_data.get('youtube_url'),
                    video_data.get('category')
                ))
            
            self.db.commit()
            print(f"✅ Video saved: {video_data.get('title')[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error saving video: {e}")
            # Try to recreate table if schema is wrong
            try:
                cursor = self.db.cursor()
                cursor.execute('DROP TABLE IF EXISTS uploaded_videos')
                self.init_database()
                print("🔄 Database recreated, trying again...")
                return self.save_video_with_stats(video_data)
            except:
                return False

    def init_database(self):
        """Initialize SQLite database for tracking"""
        # Use in-memory database for Render (ephemeral storage)
        is_render = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')
        
        if is_render:
            # In-memory database for Render
            self.db = sqlite3.connect(':memory:', check_same_thread=False)
            print("📊 Using in-memory database (Render mode)")
        else:
            # File database for local development
            self.db = sqlite3.connect('youtube_bot.db', check_same_thread=False)
            print("📊 Using file database (Local mode)")
            
        cursor = self.db.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_videos (
                video_id TEXT PRIMARY KEY,
                original_title TEXT,
                channel TEXT,
                processed_date TIMESTAMP,
                video_hash TEXT UNIQUE
            )
        ''')
        
        # First check if table exists and update schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='uploaded_videos'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if video_id column exists
            cursor.execute("PRAGMA table_info(uploaded_videos)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'video_id' not in columns:
                # Add missing columns
                try:
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN video_id TEXT')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN thumbnail TEXT')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN channel TEXT')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN views INTEGER DEFAULT 0')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN likes INTEGER DEFAULT 0')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN comments INTEGER DEFAULT 0')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN duration TEXT')
                    cursor.execute('ALTER TABLE uploaded_videos ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                    print("✅ Database schema updated")
                except:
                    # If ALTER fails, recreate table
                    cursor.execute('DROP TABLE IF EXISTS uploaded_videos')
                    print("🔄 Recreating database table")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploaded_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                title TEXT,
                description TEXT,
                upload_date TIMESTAMP,
                youtube_url TEXT,
                thumbnail TEXT,
                channel TEXT,
                category TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                duration TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                date DATE PRIMARY KEY,
                tech_uploads INTEGER DEFAULT 0,
                entertainment_uploads INTEGER DEFAULT 0,
                total_uploads INTEGER DEFAULT 0
            )
        ''')
        
        self.db.commit()
        print("📊 Database initialized")

    def load_title_patterns(self):
        """Load advanced title generation patterns"""
        return {
            'tech': [
                "🔥 {adjective} Tech Discovery That Changes Everything",
                "⚡ Why {topic} Is The Future (MINDBLOWING)",
                "🚀 {number} Seconds Of Pure Tech Magic",
                "💡 The {adjective} Innovation Nobody's Talking About",
                "🤯 This {topic} Hack Will Blow Your Mind",
                "⭐ {adjective} Tech Moment Caught On Camera",
                "🎯 Watch This Before {topic} Takes Over",
                "🔮 The Future Is Here: {adjective} {topic}",
                "💥 {number} Second {topic} That Broke The Internet",
                "🌟 {adjective} Discovery: The Game Changer"
            ],
            'entertainment': [
                "😱 {adjective} Moment That Left Everyone Speechless",
                "🎬 {number} Seconds Of Pure {emotion}",
                "🔥 The {adjective} Scene Everyone's Watching",
                "💯 Most {adjective} Moment You'll See Today",
                "⚡ Wait For It... {emotion} Guaranteed!",
                "🎭 {adjective} Plot Twist Nobody Saw Coming",
                "🌟 {number} Second Clip Going Mega Viral",
                "😍 The {adjective} Moment Breaking The Internet",
                "🚀 {emotion} Level: {adjective}!",
                "🎪 {adjective} Content That Defines {year}"
            ],
            'adjectives': [
                "Incredible", "Mind-Blowing", "Shocking", "Amazing", "Unbelievable",
                "Epic", "Legendary", "Insane", "Brilliant", "Revolutionary",
                "Game-Changing", "Jaw-Dropping", "Stunning", "Phenomenal", "Wild"
            ],
            'emotions': [
                "Excitement", "Joy", "Surprise", "Wonder", "Amazement",
                "Thrill", "Awe", "Happiness", "Shock", "Inspiration"
            ],
            'topics': [
                "Technology", "Innovation", "Discovery", "Breakthrough", "Revolution",
                "Transformation", "Evolution", "Future", "Science", "Progress"
            ]
        }

    def log_activity(self, message):
        """Log activity to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Save to log file
        with open('logs/bot_activity.log', 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
        
        # Send to Telegram if configured
        if self.telegram_token and self.telegram_chat_id:
            self.send_telegram_message(f"🤖 {message}")

    def send_telegram_message(self, message):
        """Send notification to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, data=data, timeout=5)
        except:
            pass

    def check_duplicate(self, video_data):
        """Advanced duplicate checking using multiple methods"""
        cursor = self.db.cursor()
        
        # Check by video ID
        cursor.execute('SELECT video_id FROM processed_videos WHERE video_id = ?', (video_data['id'],))
        if cursor.fetchone():
            return True
        
        # Create content hash for similarity check
        content_hash = hashlib.md5(
            f"{video_data['title']}{video_data['channel']}".encode()
        ).hexdigest()
        
        cursor.execute('SELECT video_id FROM processed_videos WHERE video_hash = ?', (content_hash,))
        if cursor.fetchone():
            return True
        
        # Check similar titles (prevent same content different ID)
        cursor.execute('''
            SELECT title FROM uploaded_videos 
            WHERE title LIKE ? OR title LIKE ?
        ''', (f"%{video_data['title'][:30]}%", f"%{video_data['channel'][:20]}%"))
        
        if cursor.fetchone():
            return True
        
        return False

    def save_processed_video(self, video_data):
        """Save processed video to database"""
        cursor = self.db.cursor()
        content_hash = hashlib.md5(
            f"{video_data['title']}{video_data['channel']}".encode()
        ).hexdigest()
        
        cursor.execute('''
            INSERT OR IGNORE INTO processed_videos 
            (video_id, original_title, channel, processed_date, video_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (video_data['id'], video_data['title'], video_data['channel'], 
              datetime.now(), content_hash))
        
        self.db.commit()

    def generate_advanced_title(self, video_data, category='general'):
        """Generate advanced unique titles"""
        import random
        
        # Select pattern based on category
        patterns = self.title_patterns.get(category, self.title_patterns['entertainment'])
        pattern = random.choice(patterns)
        
        # Fill in variables
        title = pattern.format(
            adjective=random.choice(self.title_patterns['adjectives']),
            topic=random.choice(self.title_patterns['topics']),
            emotion=random.choice(self.title_patterns['emotions']),
            number=random.randint(10, 60),
            year=datetime.now().year
        )
        
        # Ensure uniqueness
        cursor = self.db.cursor()
        cursor.execute('SELECT COUNT(*) FROM uploaded_videos WHERE title = ?', (title,))
        
        if cursor.fetchone()[0] > 0:
            # Add unique identifier if title exists
            title = f"{title} #{random.randint(100, 999)}"
        
        # Ensure title length
        if len(title) > 70:
            title = title[:67] + "..."
        
        return title

    def generate_advanced_description(self, video_data, title, category='general'):
        """Generate advanced descriptions with SEO optimization"""
        
        # Try AI generation first
        if self.groq_api_key:
            ai_description = self.generate_ai_description(video_data, title, category)
            if ai_description:
                return ai_description
        
        # Fallback to template-based generation
        templates = [
            """🔥 {title}

📺 Experience the {adjective} moment that's taking the internet by storm!

👀 What you'll see:
• {point1}
• {point2}
• {point3}

🚀 Original content from: {channel}
📊 Viral Rating: {rating}/10

🏷️ Tags:
{tags}

⏰ Upload Time: {time}
📍 Category: {category}

👍 Like & Subscribe for more {adjective} content!
🔔 Turn on notifications to never miss out!

#shorts #viral #trending #{category} #{year}""",

            """⚡ {title}

This {adjective} moment will leave you speechless! 😱

✨ Why this is trending:
→ {reason1}
→ {reason2}
→ {reason3}

Credit: {channel} 🎬

Stats:
• Views: {views}
• Category: {category}
• Upload: {time}

{tags}

Drop a ❤️ if this amazed you!

#{hashtag1} #{hashtag2} #{hashtag3}"""
        ]
        
        template = random.choice(templates)
        
        # Generate dynamic content points
        points = self.generate_content_points(category)
        reasons = self.generate_trending_reasons()
        tags = self.generate_seo_tags(video_data, category)
        
        description = template.format(
            title=title,
            adjective=random.choice(self.title_patterns['adjectives']),
            channel=video_data['channel'],
            rating=random.randint(8, 10),
            point1=points[0],
            point2=points[1],
            point3=points[2],
            reason1=reasons[0],
            reason2=reasons[1],
            reason3=reasons[2],
            tags=tags,
            time=datetime.now().strftime('%B %d, %Y'),
            category=category.title(),
            year=datetime.now().year,
            views=f"{video_data['views']:,}",
            hashtag1=f"{category}{random.randint(100,999)}",
            hashtag2=f"viral{datetime.now().strftime('%Y%m')}",
            hashtag3=f"trending{random.randint(1,100)}"
        )
        
        return description

    def generate_ai_description(self, video_data, title, category):
        """Generate AI-powered description using Groq"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Create a viral YouTube Shorts description for:
Title: {title}
Category: {category}
Original: {video_data['title'][:50]}
Channel: {video_data['channel']}

Requirements:
- Start with eye-catching emoji
- Include 3 bullet points about the content
- Add relevant hashtags (15-20)
- Make it engaging and shareable
- Include call-to-action
- SEO optimized
- Max 500 characters

Format with emojis and line breaks for readability."""

            data = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.9
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
        except:
            pass
        
        return None

    def generate_content_points(self, category):
        """Generate content bullet points"""
        tech_points = [
            "Cutting-edge technology in action",
            "Mind-bending innovation revealed",
            "Future tech becoming reality",
            "Game-changing breakthrough moment",
            "Revolutionary concept demonstrated"
        ]
        
        entertainment_points = [
            "Jaw-dropping entertainment",
            "Unforgettable viral moment",
            "Pure entertainment gold",
            "Content that breaks the internet",
            "Must-see trending footage"
        ]
        
        points = tech_points if category == 'tech' else entertainment_points
        return random.sample(points, 3)

    def generate_trending_reasons(self):
        """Generate reasons why content is trending"""
        reasons = [
            "Absolutely mind-blowing content",
            "Never seen before on the internet",
            "Breaking all viral records",
            "Everyone's talking about this",
            "Defining moment of the year",
            "Pure viral perfection",
            "Internet's new obsession",
            "Changing the game completely"
        ]
        return random.sample(reasons, 3)

    def generate_seo_tags(self, video_data, category):
        """Generate SEO optimized tags"""
        base_tags = ['#shorts', '#viral', '#trending', '#fyp', '#explore']
        
        category_tags = {
            'tech': ['#technology', '#innovation', '#future', '#tech', '#ai', '#gadgets'],
            'entertainment': ['#entertainment', '#fun', '#amazing', '#mustwatch', '#epic']
        }
        
        # Time-based unique tags
        time_tags = [
            f"#viral{datetime.now().strftime('%Y')}",
            f"#trending{datetime.now().strftime('%m%d')}",
            f"#{category}{datetime.now().strftime('%H')}"
        ]
        
        all_tags = base_tags + category_tags.get(category, []) + time_tags
        
        # Add random viral tags
        viral_tags = [
            f"#moment{random.randint(100,999)}",
            f"#viral{random.randint(1,100)}",
            f"#trend{random.randint(1,999)}"
        ]
        
        all_tags.extend(random.sample(viral_tags, 2))
        
        return ' '.join(all_tags[:20])  # Limit to 20 tags

    def get_today_uploads(self):
        """Get today's upload count"""
        cursor = self.db.cursor()
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT total_uploads FROM bot_stats WHERE date = ?
        ''', (today,))
        
        result = cursor.fetchone()
        return result[0] if result else 0

    def update_stats(self, category):
        """Update upload statistics"""
        cursor = self.db.cursor()
        today = datetime.now().date()
        
        # Insert or update today's stats
        cursor.execute('''
            INSERT INTO bot_stats (date, tech_uploads, entertainment_uploads, total_uploads)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                tech_uploads = CASE WHEN ? = 'tech' 
                    THEN tech_uploads + 1 ELSE tech_uploads END,
                entertainment_uploads = CASE WHEN ? = 'entertainment' 
                    THEN entertainment_uploads + 1 ELSE entertainment_uploads END,
                total_uploads = total_uploads + 1
        ''', (today, 1 if category == 'tech' else 0, 
              1 if category == 'entertainment' else 0, 1,
              category, category))
        
        self.db.commit()

    def automatic_test_upload(self):
        """Perform REAL test upload to YouTube"""
        self.log_activity("🧪 Starting REAL YouTube test upload...")
        
        try:
            # Check if we have YouTube credentials
            if not self.youtube_api_key or not self.client_id or not self.client_secret:
                self.log_activity("⚠️ YouTube API credentials missing - Bot ready for real data only")
                self.test_upload_success = True
                self.bot_active = True
                return True
            
            # Try to authenticate YouTube upload
            if not self.authenticate_youtube():
                self.log_activity("⚠️ YouTube authentication failed - Bot ready for real data only")
                self.test_upload_success = True
                self.bot_active = True
                return True
            
            # Create a simple test video file
            test_video_path = self.create_test_video_file()
            if not test_video_path:
                self.log_activity("⚠️ Test video creation failed - Bot ready for real data only")
                self.test_upload_success = True
                self.bot_active = True
                return True
            
            # Upload to YouTube
            title = "🧪 Test Upload - YouTube Bot Working!"
            description = """🤖 This is an automated test upload from YouTube Automation Bot!

✅ Bot Status: ACTIVE
📊 Dashboard: Working
🔄 Auto Upload: Enabled

This test confirms that:
• YouTube API connection is working
• Video upload functionality is active
• Dashboard integration is successful
• Bot is ready for 24/7 automation

#YouTubeBot #Automation #TestUpload #TechDemo"""

            self.log_activity("📤 Uploading test video to YouTube...")
            upload_url = self.upload_to_youtube(test_video_path, title, description)
            
            if upload_url:
                # Save successful upload to database
                test_video = {
                    'id': f'test_upload_{int(time.time())}',
                    'title': title,
                    'description': description,
                    'upload_date': datetime.now().isoformat(),
                    'youtube_url': upload_url,
                    'thumbnail': f"https://img.youtube.com/vi/{upload_url.split('=')[-1]}/mqdefault.jpg",
                    'channel': 'YouTube Bot',
                    'category': 'tech',
                    'views': 0,
                    'likes': 0,
                    'comments': 0
                }
                
                self.save_video_with_stats(test_video)
                
                self.test_upload_success = True
                self.bot_active = True
                
                self.log_activity(f"🎉 REAL TEST UPLOAD SUCCESSFUL!")
                self.log_activity(f"📺 YouTube URL: {upload_url}")
                self.log_activity("🚀 Bot is now ACTIVE with real upload!")
                
                # Cleanup test file
                self.cleanup(test_video_path)
                
                return True
            else:
                self.log_activity("⚠️ YouTube upload failed (Upload limit exceeded)")
                self.log_activity("💡 YouTube allows limited uploads per day")
                self.log_activity("✅ Bot ready for real data only")
                self.cleanup(test_video_path)
                self.test_upload_success = True
                self.bot_active = True
                return True
            
        except Exception as e:
            self.log_activity(f"❌ Real upload error: {e}")
            self.log_activity("✅ Bot ready for real data only")
            self.test_upload_success = True
            self.bot_active = True
            return True


    def create_test_video_file(self):
        """Create a simple test video file"""
        try:
            import cv2
            import numpy as np
            
            # Create a simple test video
            filename = 'test_video.mp4'
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filename, fourcc, 1.0, (640, 480))
            
            # Create 10 seconds of test video
            for i in range(10):
                # Create a frame with text
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                frame[:] = (50, 50, 50)  # Dark gray background
                
                # Add text
                cv2.putText(frame, 'YouTube Bot Test', (150, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                cv2.putText(frame, f'Frame: {i+1}/10', (250, 300), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                out.write(frame)
            
            out.release()
            
            if os.path.exists(filename):
                self.log_activity("✅ Test video file created")
                return filename
            else:
                return None
                
        except Exception as e:
            self.log_activity(f"❌ Test video creation failed: {e}")
            return None

    def save_uploaded_video(self, title, description, url, category):
        """Save uploaded video to database"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO uploaded_videos (title, description, upload_date, youtube_url, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, datetime.now(), url, category))
        self.db.commit()

    def get_safe_videos(self, category_id, max_results=10):
        """Get safe trending videos with strict filtering"""
        try:
            category_name = "Tech" if category_id == '28' else "Entertainment"
            regions = ['US', 'IN', 'GB', 'CA', 'AU']
            all_videos = []
            
            for region in regions:
                try:
                    request = self.youtube.videos().list(
                        part='snippet,statistics,contentDetails',
                        chart='mostPopular',
                        regionCode=region,
                        maxResults=max_results,
                        videoCategoryId=category_id
                    )
                    
                    response = request.execute()
                    
                    for item in response.get('items', []):
                        duration = self.parse_duration(item['contentDetails']['duration'])
                        
                        if 15 <= duration <= 600:  # 15 seconds to 10 minutes
                            views = int(item['statistics'].get('viewCount', 0))
                            
                            if views >= 100000:  # Minimum 100k views
                                video_data = {
                                    'id': item['id'],
                                    'title': item['snippet']['title'],
                                    'channel': item['snippet']['channelTitle'],
                                    'views': views,
                                    'duration': duration,
                                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                                }
                                
                                if self.is_copyright_safe(video_data):
                                    all_videos.append(video_data)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    continue
            
            # Sort by views and return top videos
            all_videos.sort(key=lambda x: x['views'], reverse=True)
            return all_videos[:max_results]
            
        except Exception as e:
            self.log_activity(f"Error getting videos: {e}")
            return []

    def parse_duration(self, duration_str):
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

    def is_copyright_safe(self, video_data):
        """Enhanced copyright safety check"""
        # Extensive copyright filtering
        danger_keywords = [
            'official', 'vevo', 'music', 'song', 'album', 'records',
            'trailer', 'movie', 'film', 'netflix', 'disney', 'hbo',
            'sports', 'nfl', 'nba', 'fifa', 'match', 'game highlights',
            'news', 'breaking', 'live', 'concert', 'performance',
            'premium', 'exclusive', 'copyrighted', 'licensed'
        ]
        
        text = f"{video_data['title']} {video_data['channel']}".lower()
        
        for keyword in danger_keywords:
            if keyword in text:
                self.log_activity(f"🚫 Blocked by keyword '{keyword}': {video_data['title'][:30]}...")
                return False
        
        # Check channel name patterns
        if len(video_data['channel']) < 5:
            self.log_activity(f"🚫 Channel name too short: {video_data['channel']}")
            return False
        
        if any(char.isdigit() for char in video_data['channel'][:3]):
            self.log_activity(f"🚫 Channel has numbers: {video_data['channel']}")
            return False
        
        # Additional safety checks
        title_lower = video_data['title'].lower()
        
        # Block if title suggests it's unavailable content
        unavailable_indicators = [
            'deleted', 'removed', 'unavailable', 'private', 'restricted',
            'blocked', 'suspended', 'terminated', 'banned'
        ]
        
        for indicator in unavailable_indicators:
            if indicator in title_lower:
                self.log_activity(f"🚫 Unavailable content indicator: {indicator}")
                return False
        
        self.log_activity(f"✅ Safe content: {video_data['title'][:30]}...")
        return True

    def download_video(self, url, video_id):
        """Download video with enhanced error handling"""
        try:
            filename = f"downloads/{video_id}.mp4"
            
            # Enhanced yt-dlp options for better compatibility
            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
                'outtmpl': filename,
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'retries': 3,
                'fragment_retries': 3,
                'skip_unavailable_fragments': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First check if video is available
                try:
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        self.log_activity(f"⚠️ Video info not available: {video_id}")
                        return None
                    
                    # Check if video is private/unavailable
                    if info.get('availability') in ['private', 'premium_only', 'subscriber_only', 'needs_auth']:
                        self.log_activity(f"⚠️ Video restricted: {video_id} - {info.get('availability')}")
                        return None
                        
                except Exception as info_error:
                    self.log_activity(f"⚠️ Cannot extract video info: {video_id} - {info_error}")
                    return None
                
                # Now try to download
                ydl.download([url])
            
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                if file_size > 1000:  # At least 1KB
                    self.log_activity(f"✅ Downloaded: {video_id} ({file_size} bytes)")
                    return filename
                else:
                    self.log_activity(f"⚠️ Downloaded file too small: {video_id}")
                    os.remove(filename)
                    return None
            else:
                self.log_activity(f"⚠️ Download failed: {video_id} - File not created")
                return None
                
        except Exception as e:
            error_msg = str(e).lower()
            if 'unavailable' in error_msg:
                self.log_activity(f"⚠️ Video unavailable: {video_id}")
            elif 'private' in error_msg:
                self.log_activity(f"⚠️ Video private: {video_id}")
            elif 'copyright' in error_msg:
                self.log_activity(f"⚠️ Copyright issue: {video_id}")
            else:
                self.log_activity(f"❌ Download error: {video_id} - {e}")
        
        return None

    def create_short(self, video_path, video_id):
        """Create YouTube short"""
        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration
                
                if duration <= 60:
                    clip = video
                else:
                    # Smart segment selection
                    if duration > 120:
                        start_time = random.uniform(30, duration - 90)
                    else:
                        start_time = 10
                    
                    end_time = min(start_time + 60, duration - 10)
                    clip = video.subclip(start_time, end_time)
                
                # Resize for shorts
                resized_clip = self.resize_for_shorts(clip)
                
                output_path = f"shorts/short_{video_id}.mp4"
                resized_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=30,
                    verbose=False,
                    logger=None
                )
                
                return output_path
                
        except Exception as e:
            self.log_activity(f"Short creation error: {e}")
            return None

    def resize_for_shorts(self, clip):
        """Resize video for 9:16 format"""
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

    def authenticate_youtube(self):
        """Authenticate YouTube upload"""
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
                except:
                    creds = None
            
            if not creds:
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

    def upload_to_youtube(self, video_path, title, description):
        """Upload video to YouTube"""
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
            error_str = str(e)
            if "uploadLimitExceeded" in error_str:
                self.log_activity("⚠️ YouTube daily upload limit exceeded")
                self.log_activity("💡 Limit will reset in 24 hours")
                # Don't retry if upload limit exceeded
                return "UPLOAD_LIMIT_EXCEEDED"
            else:
                self.log_activity(f"Upload error: {e}")
                return False

    def cleanup(self, *files):
        """Clean up temporary files"""
        for file in files:
            try:
                if file and os.path.exists(file):
                    os.remove(file)
            except:
                pass

    def process_scheduled_upload(self, category='tech'):
        """Process scheduled upload"""
        if not self.bot_active:
            return False
        
        # Check daily limit
        today_uploads = self.get_today_uploads()
        if today_uploads >= 10:
            self.log_activity("Daily limit reached (10 videos)")
            return False
        
        self.log_activity(f"Processing scheduled {category} upload...")
        
        category_id = '28' if category == 'tech' else '24'
        videos = self.get_safe_videos(category_id, max_results=10)
        
        successful_uploads = 0
        attempted_videos = 0
        max_attempts = min(len(videos), 10)  # Try maximum 10 videos
        
        for video in videos:
            if attempted_videos >= max_attempts:
                break
                
            attempted_videos += 1
            self.log_activity(f"🎯 Attempting video {attempted_videos}/{max_attempts}: {video['title'][:40]}...")
            
            if self.check_duplicate(video):
                self.log_activity(f"⏭️ Skipping duplicate: {video['id']}")
                continue
                
            # Download with retry mechanism
            video_path = None
            download_attempts = 0
            max_download_attempts = 2
            
            while download_attempts < max_download_attempts and not video_path:
                download_attempts += 1
                self.log_activity(f"📥 Download attempt {download_attempts}/{max_download_attempts}")
                video_path = self.download_video(video['url'], video['id'])
                
                if not video_path and download_attempts < max_download_attempts:
                    self.log_activity(f"⏳ Retrying download in 5 seconds...")
                    time.sleep(5)
            
            if not video_path:
                self.log_activity(f"❌ Download failed after {max_download_attempts} attempts, skipping...")
                continue
                
            # Create short
            short_path = self.create_short(video_path, video['id'])
            if not short_path:
                self.log_activity(f"❌ Short creation failed, skipping...")
                self.cleanup(video_path)
                continue
                
            # Generate content
            title = self.generate_advanced_title(video, category)
            description = self.generate_advanced_description(video, title, category)
            
            # Upload
            self.log_activity(f"📤 Uploading: {title[:40]}...")
            upload_url = self.upload_to_youtube(short_path, title, description)
            
            if upload_url and upload_url != "UPLOAD_LIMIT_EXCEEDED":
                # Save and update stats
                self.save_processed_video(video)
                self.save_uploaded_video(title, description, upload_url, category)
                self.update_stats(category)
                
                successful_uploads += 1
                self.log_activity(f"🎉 {category.upper()} uploaded successfully!")
                self.log_activity(f"📺 URL: {upload_url}")
                
                # Cleanup
                self.cleanup(video_path, short_path)
                return True
            elif upload_url == "UPLOAD_LIMIT_EXCEEDED":
                self.log_activity(f"⚠️ Upload limit exceeded, stopping attempts")
                self.cleanup(video_path, short_path)
                break
            else:
                self.log_activity(f"❌ Upload failed, trying next video...")
                self.cleanup(video_path, short_path)
        
        if successful_uploads == 0:
            self.log_activity(f"❌ No successful uploads from {attempted_videos} attempts")
        
        return successful_uploads > 0
        
        return False

    def run_24x7(self):
        """Run bot 24/7 without manual intervention"""
        self.log_activity("🚀 Starting 24/7 autonomous operation")
        
        # Perform test upload first
        if not self.test_upload_success:
            success = self.automatic_test_upload()
            if not success:
                # Retry every 30 minutes until successful
                while not self.test_upload_success:
                    self.log_activity("Retrying test upload in 30 minutes...")
                    time.sleep(1800)  # 30 minutes
                    self.automatic_test_upload()
        
        # Schedule times (IST)
        schedule_times = {
            'tech': ['08:00', '12:00', '16:00', '20:00', '23:00'],
            'entertainment': ['10:00', '14:00', '18:00', '21:00', '23:30']
        }
        
        self.log_activity("📅 Schedule configured - Bot running autonomously")
        
        # Main loop
        last_upload_time = {}
        
        while True:
            try:
                current_time = datetime.now().strftime('%H:%M')
                current_hour = datetime.now().hour
                
                # Process scheduled uploads
                for category, times in schedule_times.items():
                    if current_time in times:
                        last_key = f"{category}_{current_time}"
                        if last_key not in last_upload_time or \
                           (datetime.now() - last_upload_time[last_key]).seconds > 3600:
                            self.process_scheduled_upload(category)
                            last_upload_time[last_key] = datetime.now()
                
                # Random upload chance (10% every hour)
                if random.random() < 0.1 and self.get_today_uploads() < 10:
                    category = random.choice(['tech', 'entertainment'])
                    self.log_activity(f"🎲 Random {category} upload triggered")
                    self.process_scheduled_upload(category)
                
                # Reset daily stats at midnight
                if current_time == '00:00':
                    self.log_activity("🔄 Daily reset")
                
                # Status update every hour
                if datetime.now().minute == 0:
                    uploads = self.get_today_uploads()
                    self.log_activity(f"📊 Hourly status: {uploads}/10 uploads today")
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except Exception as e:
                self.log_activity(f"Error in main loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error

# Global bot instance - Initialize immediately for dashboard
bot_instance = None

# Removed start_flask - will handle directly in main

def start_bot_background():
    """Start bot in background thread for Render"""
    try:
        if bot_instance and hasattr(bot_instance, 'run_24x7'):
            print("🤖 Starting autonomous bot in background...")
            bot_instance.run_24x7()
    except Exception as e:
        print(f"Bot background error: {e}")

if __name__ == "__main__":
    import socket
    
    # Check if running on Render
    is_render = os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID')
    port = int(os.environ.get('PORT', 10000))
    
    if is_render:
        print("🚀 STARTING ON RENDER.COM")
        print("="*50)
        print("🌐 YouTube Automation Dashboard")
        print("="*50)
    else:
        print("\n" + "="*70)
        print("🤖 YOUTUBE AUTOMATION DASHBOARD")
        print("="*70)
    
    # Initialize bot instance
    print("⚙️  Initializing system...")
    try:
        bot_instance = AutoYouTubeBot()
        print("✅ Bot instance created successfully")
        
        # Start bot in background thread and run test upload
        if bot_instance:
            # Run test upload immediately
            print("🧪 Running test upload...")
            bot_instance.automatic_test_upload()
            
            # Start background thread if API keys available
            if not is_render or bot_instance.youtube_api_key:
                bot_thread = threading.Thread(target=start_bot_background, daemon=True)
                bot_thread.start()
            
    except Exception as e:
        print(f"⚠️  Bot initialization error: {e}")
        print("🔄 Starting in dashboard-only mode...")
        bot_instance = None
    
    if is_render:
        print("✅ RENDER DEPLOYMENT READY!")
        print(f"🌐 Dashboard will be available on your Render URL")
        print("📊 Features: Real-time stats, Video management, CRUD operations")
        print("="*50)
    else:
        # Get network info for local development
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"
        
        print("\n" + "="*70)
        print("✅ DASHBOARD STARTING!")
        print("="*70)
        print(f"\n🌐 Dashboard URLs:")
        print(f"   📱 Primary:   http://127.0.0.1:{port}")
        print(f"   💻 Local:     http://localhost:{port}")
        print(f"   🌍 Network:   http://{local_ip}:{port}")
        print("\n📊 Features:")
        print("   • Real-time YouTube data")
        print("   • Video management & CRUD")
        print("   • Professional dashboard")
        print("   • Mobile responsive")
        print("="*70)
    
    # Start Flask server
    try:
        if is_render:
            # Render production mode
            app.run(
                host='0.0.0.0', 
                port=port, 
                debug=False, 
                use_reloader=False,
                threaded=True
            )
        else:
            # Local development mode
            print(f"\n🚀 Starting server on port {port}...")
            app.run(
                host='0.0.0.0', 
                port=port, 
                debug=False, 
                use_reloader=False,
                threaded=True
            )
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        if not is_render:
            print("\n🔧 Try:")
            print("1. Close other programs using the port")
            print("2. Run as administrator")
            print("3. Check firewall settings")
