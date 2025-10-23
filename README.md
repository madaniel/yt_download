# YouTube Downloader

A user-friendly YouTube video downloader with optional trimming functionality.

## Quick Start

### Using the Python wrapper script (recommended - OS agnostic):

```bash
# Download a video
python3 download.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Download and trim 15 seconds from the end
python3 download.py "https://www.youtube.com/watch?v=VIDEO_ID" --trim 15

# Download to a specific directory
python3 download.py "https://www.youtube.com/watch?v=VIDEO_ID" --download-path ~/Downloads
```

## Features

- 🎬 Downloads YouTube videos in high quality (up to 4K)
- ✂️ Optional trimming from the end of videos
- 🔍 Checks video compatibility with Plex
- 📁 Customizable download directory
- 🚀 Simple Python wrapper script (no venv activation needed, OS agnostic)

## Requirements

- Python 3.10+
- Virtual environment with required packages
- ffmpeg (for trimming functionality)

## Installation

1. Clone this repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (On Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`

## Usage Examples

```bash
# Basic download
python3 download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download and trim 30 seconds
python3 download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -t 30

# Download to specific folder
python3 download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -d ~/Videos

# Combine options
python3 download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -t 10 -d ~/Downloads
```

## Command Line Options

- `url` (required): YouTube video URL
- `--trim, -t`: Number of seconds to trim from the end (default: 0)
- `--download-path, -d`: Directory to save videos (default: current directory)
