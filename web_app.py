#!/usr/bin/env python3
"""
YouTube Downloader Web Interface
Flask web application for downloading and trimming YouTube videos
"""

from flask import Flask, request, send_file, jsonify, Response
import yt_dlp
import subprocess
import os
import sys
from pathlib import Path
import tempfile
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
DOWNLOAD_PATH = Path("/downloads")
DOWNLOAD_PATH.mkdir(exist_ok=True)

# Quality format mappings for yt-dlp
QUALITY_FORMATS = {
    '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]',
    '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]',
    '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]',
    '4k': 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]',
    'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
}

def parse_time(time_str):
    """Convert time string (HH:MM:SS or seconds) to seconds"""
    if not time_str:
        return None
    
    time_str = str(time_str).strip()
    if ':' in time_str:
        # Format: HH:MM:SS or MM:SS
        parts = time_str.split(':')
        parts = [int(p) for p in parts]
        if len(parts) == 3:  # HH:MM:SS
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:  # MM:SS
            return parts[0] * 60 + parts[1]
    else:
        # Just seconds
        return float(time_str)

def download_youtube_video(url, quality='1080p', download_path=DOWNLOAD_PATH):
    """Download YouTube video with specified quality"""
    download_path = Path(download_path)
    download_path.mkdir(exist_ok=True)
    
    format_string = QUALITY_FORMATS.get(quality, QUALITY_FORMATS['1080p'])
    
    ydl_opts = {
        'format': format_string,
        'outtmpl': str(download_path / '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }
    
    # Add cookies file if it exists
    cookies_file = Path('/app/cookies.txt')
    if cookies_file.exists():
        ydl_opts['cookiefile'] = str(cookies_file)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Get the actual downloaded file path
        requested_downloads = info.get('requested_downloads') or []
        if requested_downloads and requested_downloads[0].get('filepath'):
            filepath = requested_downloads[0]['filepath']
        else:
            filepath = ydl.prepare_filename(info)
        
        return Path(filepath)

def get_video_duration(file_path):
    """Get video duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None

def get_codec(file_path, stream_type):
    """Get codec for video or audio stream"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", f"{stream_type}:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=nw=1:nk=1",
                str(file_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error reading {stream_type} codec: {e.stderr}")
        return None

def is_plex_friendly(file_path):
    """Check if video has Plex-friendly codecs (h264 video, aac audio)"""
    if not Path(file_path).exists():
        print("❌ File does not exist.")
        return False

    vcodec = get_codec(file_path, 'v')
    acodec = get_codec(file_path, 'a')

    print(f"Video codec: {vcodec}")
    print(f"Audio codec: {acodec}")

    if vcodec == "h264" and acodec == "aac":
        print("✅ Plex-friendly")
        return True
    else:
        print(f"❌ Not Plex-friendly (video: {vcodec}, audio: {acodec})")
        return False

def reencode_to_plex_friendly(input_path, output_path):
    """Re-encode video to Plex-friendly format (h264/aac)"""
    print(f"⚙️ Re-encoding '{input_path}' to Plex-friendly format...")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-movflags", "+faststart",
                "-preset", "fast",  # Use 'fast' for quicker encodes
                str(output_path)
            ],
            check=True,
            capture_output=True
        )
        print(f"✅ Re-encoded and saved to: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Re-encoding failed: {e}")
        print(f"stderr: {e.stderr.decode()}")
        return False

def trim_video(input_file, output_file, start_time=None, end_time=None):
    """
    Trim video using ffmpeg
    
    Args:
        input_file: Path to input video
        output_file: Path to output video
        start_time: Start time in seconds (None = from beginning)
        end_time: End time in seconds (None = to end)
    
    Returns:
        True if successful, False otherwise
    """
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    # Build ffmpeg command
    cmd = ["ffmpeg", "-y", "-i", str(input_file)]
    
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    
    if end_time is not None:
        if start_time is not None:
            # Duration = end - start
            duration = end_time - start_time
            cmd.extend(["-t", str(duration)])
        else:
            # Just use end time as duration
            cmd.extend(["-t", str(end_time)])
    
    cmd.extend(["-c", "copy", str(output_file)])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Trimmed video saved to: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed: {e}")
        print(f"stderr: {e.stderr.decode()}")
        return False

@app.route('/')
def index():
    """Serve the main HTML page"""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Downloader</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            backdrop-filter: blur(10px);
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        input[type="text"],
        input[type="number"],
        select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s ease;
            background: white;
        }
        
        input[type="text"]:focus,
        input[type="number"]:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .time-inputs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }
        
        .btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active:not(:disabled) {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status {
            text-align: center;
            margin-top: 15px;
            padding: 12px;
            border-radius: 8px;
            font-weight: 500;
            display: none;
        }
        
        .status.active {
            display: block;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .hint {
            font-size: 0.8em;
            color: #999;
            margin-top: 5px;
        }
        
        .optional-badge {
            display: inline-block;
            background: #ffeaa7;
            color: #d63031;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7em;
            margin-left: 5px;
            font-weight: 600;
        }
        
        .checkbox-label {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #333;
        }
        
        .checkbox-label input[type="checkbox"] {
            width: auto;
            margin-right: 10px;
            cursor: pointer;
            width: 18px;
            height: 18px;
            accent-color: #667eea;
        }
        
        .checkbox-label span {
            flex: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 YouTube Downloader</h1>
        <p class="subtitle">Download and trim YouTube videos with ease</p>
        
        <form id="downloadForm">
            <div class="form-group">
                <label for="url">YouTube URL</label>
                <input 
                    type="text" 
                    id="url" 
                    name="url" 
                    placeholder="https://www.youtube.com/watch?v=..." 
                    required
                >
            </div>
            
            <div class="form-group">
                <label for="quality">Video Quality</label>
                <select id="quality" name="quality">
                    <option value="360p">360p</option>
                    <option value="720p">720p</option>
                    <option value="1080p" selected>1080p (Full HD)</option>
                    <option value="4k">4K (2160p)</option>
                    <option value="best">Best Available</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>
                    Trim Video 
                    <span class="optional-badge">OPTIONAL</span>
                </label>
                <div class="time-inputs">
                    <div>
                        <input 
                            type="text" 
                            id="start_time" 
                            name="start_time" 
                            placeholder="Start (e.g., 0:30 or 30)"
                        >
                        <p class="hint">Format: HH:MM:SS, MM:SS, or seconds</p>
                    </div>
                    <div>
                        <input 
                            type="text" 
                            id="end_time" 
                            name="end_time" 
                            placeholder="End (e.g., 2:30 or 150)"
                        >
                        <p class="hint">Leave empty for full video</p>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="checkbox-label">
                    <input 
                        type="checkbox" 
                        id="plex_compatible" 
                        name="plex_compatible"
                        checked
                    >
                    <span>Ensure Plex Compatibility (h264/aac)</span>
                </label>
                <p class="hint">Automatically re-encode if needed for Plex playback</p>
            </div>
            
            <button type="submit" class="btn" id="downloadBtn">
                Download Video
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p id="loadingText">Processing your request...</p>
        </div>
        
        <div class="status" id="status"></div>
    </div>
    
    <script>
        const form = document.getElementById('downloadForm');
        const loadingDiv = document.getElementById('loading');
        const statusDiv = document.getElementById('status');
        const downloadBtn = document.getElementById('downloadBtn');
        const loadingText = document.getElementById('loadingText');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Get form data
            const url = document.getElementById('url').value;
            const quality = document.getElementById('quality').value;
            const startTime = document.getElementById('start_time').value;
            const endTime = document.getElementById('end_time').value;
            const plexCompatible = document.getElementById('plex_compatible').checked;
            
            // Reset status
            statusDiv.className = 'status';
            statusDiv.textContent = '';
            
            // Show loading
            loadingDiv.classList.add('active');
            downloadBtn.disabled = true;
            loadingText.textContent = 'Downloading video...';
            
            // Build query params
            const params = new URLSearchParams({
                url: url,
                quality: quality,
                plex_compatible: plexCompatible ? '1' : '0'
            });
            
            if (startTime) params.append('start_time', startTime);
            if (endTime) params.append('end_time', endTime);
            
            try {
                const response = await fetch(`/api/download?${params}`);
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Download failed');
                }
                
                // Update loading text
                loadingText.textContent = 'Preparing download...';
                
                // Get filename from header
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'video.mp4';
                if (contentDisposition) {
                    const matches = /filename[^;=\\n]*=((['"]).*?\\2|[^;\\n]*)/.exec(contentDisposition);
                    if (matches && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }
                
                // Download the file
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
                // Show success
                statusDiv.className = 'status success active';
                statusDiv.textContent = '✅ Download complete! Check your downloads folder.';
                
            } catch (error) {
                statusDiv.className = 'status error active';
                statusDiv.textContent = `❌ Error: ${error.message}`;
            } finally {
                loadingDiv.classList.remove('active');
                downloadBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
    """
    return html

@app.route('/api/download')
def download():
    """Download endpoint - handles video download and trimming"""
    try:
        # Get parameters
        url = request.args.get('url')
        quality = request.args.get('quality', '1080p')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        plex_compatible = request.args.get('plex_compatible', '1') == '1'
        
        if not url:
            return jsonify({'error': 'Missing URL parameter'}), 400
        
        # Parse times
        start_time = parse_time(start_time_str) if start_time_str else None
        end_time = parse_time(end_time_str) if end_time_str else None
        
        print(f"Download request: URL={url}, Quality={quality}, Start={start_time}, End={end_time}, Plex={plex_compatible}")
        
        # Download video
        print("Downloading video...")
        video_file = download_youtube_video(url, quality, DOWNLOAD_PATH)
        
        if not video_file.exists():
            return jsonify({'error': 'Download failed'}), 500
        
        # Determine output file
        output_file = video_file
        
        # Trim if needed
        if start_time is not None or end_time is not None:
            print(f"Trimming video: start={start_time}, end={end_time}")
            trimmed_file = video_file.parent / f"{video_file.stem}_trimmed{video_file.suffix}"
            
            if trim_video(video_file, trimmed_file, start_time, end_time):
                # Use trimmed file and delete original
                video_file.unlink()
                output_file = trimmed_file
            else:
                return jsonify({'error': 'Trimming failed'}), 500
        
        # Check Plex compatibility if requested
        if plex_compatible:
            print("Checking Plex compatibility...")
            if not is_plex_friendly(output_file):
                print("Re-encoding to Plex-friendly format...")
                plex_file = output_file.parent / f"{output_file.stem}_plex{output_file.suffix}"
                
                if reencode_to_plex_friendly(output_file, plex_file):
                    # Use re-encoded file and delete original
                    output_file.unlink()
                    output_file = plex_file
                else:
                    return jsonify({'error': 'Plex re-encoding failed'}), 500
            else:
                print("Video is already Plex-friendly!")
        
        print(f"Sending file: {output_file}")
        
        # Send file to client
        def cleanup_file():
            """Cleanup file after sending"""
            try:
                time.sleep(1)  # Give time for download to complete
                if output_file.exists():
                    output_file.unlink()
                    print(f"Cleaned up: {output_file}")
            except Exception as e:
                print(f"Cleanup error: {e}")
        
        response = send_file(
            output_file,
            as_attachment=True,
            download_name=output_file.name,
            mimetype='video/mp4'
        )
        
        # Schedule cleanup (note: this won't work perfectly with send_file)
        # We'll do a simpler approach - cleanup in background
        import threading
        threading.Timer(2.0, cleanup_file).start()
        
        return response
        
    except Exception as e:
        print(f"Error in download endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'YouTube Downloader'})

if __name__ == "__main__":
    print("🚀 Starting YouTube Downloader Web Server...")
    print(f"📁 Download directory: {DOWNLOAD_PATH}")
    app.run(debug=False, host="0.0.0.0", port=5000)
