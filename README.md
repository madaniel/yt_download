# YouTube Downloader Web Interface 🎬

A modern, Docker-based web application for downloading and trimming YouTube videos with ease.

![Interface Screenshot](https://img.shields.io/badge/Status-Ready-success?style=for-the-badge) ![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker) ![Python](https://img.shields.io/badge/Python-3.10-green?style=for-the-badge&logo=python)

## ✨ Features

- 🎨 **Modern Web Interface** - Beautiful, responsive UI with gradient design
- 📹 **Quality Selection** - Choose from 360p, 720p, 1080p, 4K, or Best Available
- ✂️ **Video Trimming** - Trim videos with start/end time (supports HH:MM:SS or seconds)
- 💾 **Direct Downloads** - Files download directly to your browser's download folder
- 🐳 **Docker Ready** - Fully containerized, runs standalone
- 🗑️ **Auto Cleanup** - Temporary files automatically deleted
- 🔒 **Age-Restricted Support** - Includes cookies for restricted videos

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Installation & Running

```bash
# Clone or navigate to the project directory
cd yt_download

# Build and start the service
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker logs yt-downloader
```

The web interface will be available at: **http://localhost:5000**

### Stopping the Service

```bash
# Stop the service
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📖 Usage

1. **Open** http://localhost:5000 in your browser
2. **Paste** a YouTube URL
3. **Select** desired video quality
4. **Optional:** Set start/end times to trim the video
   - Format: `HH:MM:SS`, `MM:SS`, or seconds
   - Example: `0:30` or `30` for 30 seconds
5. **Click** "Download Video"
6. Video will download to your browser's download folder

## 🎯 Examples

### Basic Download
- URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- Quality: `1080p`
- Result: Full video in 1080p

### Trimmed Download
- URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- Quality: `720p`
- Start: `0:10` (10 seconds)
- End: `2:30` (2 minutes 30 seconds)
- Result: 2 minute 20 second clip in 720p

## 🏗️ Architecture

```
Browser → Flask Web Server → yt-dlp → Video Download
                ↓
          Trim (ffmpeg)
                ↓
        Stream to Browser → Cleanup
```

## 📦 Project Structure

```
yt_download/
├── web_app.py           # Flask web server with embedded UI
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker image definition
├── requirements.txt     # Python dependencies
├── cookies.txt         # Cookies for age-restricted videos
├── download.py         # Original CLI wrapper
└── run_orig.py         # Original download script
```

## 🔧 Configuration

### Port Change
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Use port 8080 instead of 5000
```

### Quality Options
Available in the web interface:
- 360p (640×360)
- 720p (1280×720)
- 1080p (1920×1080) - Default
- 4K (3840×2160)
- Best Available

## 🛠️ Development

### Manual Testing
```bash
# Health check
curl http://localhost:5000/health

# Download test (returns JSON)
curl "http://localhost:5000/api/download?url=YOUTUBE_URL&quality=720p"
```

### Rebuilding
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
docker logs yt-downloader

# Check if port is in use
sudo lsof -i :5000
```

### Download fails
- Verify the YouTube URL is valid
- Try a different quality setting
- Check Docker logs for detailed errors
- Some videos may be geo-restricted or require authentication

### Trimming doesn't work
- Ensure times are in correct format (HH:MM:SS or seconds)
- End time must be greater than start time
- Times must be within video duration

## 📝 API Endpoints

### `GET /`
Returns the web interface HTML

### `GET /api/download`
Downloads and optionally trims a YouTube video

**Parameters:**
- `url` (required): YouTube video URL
- `quality` (optional): Video quality (360p, 720p, 1080p, 4k, best)
- `start_time` (optional): Start time in HH:MM:SS or seconds
- `end_time` (optional): End time in HH:MM:SS or seconds

**Response:** Video file as attachment

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "YouTube Downloader"
}
```

## 🔒 Security Notes

- Files are automatically deleted after download
- No data is stored permanently in the container
- Cookies file is used for age-restricted video access only
- All processing happens locally in Docker

## 📄 License

This project uses:
- **yt-dlp** - YouTube video downloader
- **FFmpeg** - Video processing
- **Flask** - Web framework

## 🙏 Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Flask](https://flask.palletsprojects.com/) - Python web framework

## 📞 Support

If you encounter issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review Docker logs: `docker logs yt-downloader`
3. Verify system requirements are met
4. Try rebuilding the container

---

**Made with ❤️ and Docker**
