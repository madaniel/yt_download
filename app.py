from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
from pathlib import Path

app = Flask(__name__)
DOWNLOAD_PATH = "./downloads"

def download_youtube_video_file(url, hd=False, download_path=DOWNLOAD_PATH):
    download_path = Path(download_path)
    if hd:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height=1080]+bestaudio[ext=m4a]/best[ext=mp4][height=1080]',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }
    else:
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        # yt-dlp provides info dict with 'title' and 'ext'
        filename = f"{result['title']}.{result['ext']}"
        filepath = download_path / filename
        return str(filepath.resolve())

@app.route('/', methods=['GET'])
def index():
    return jsonify(
        {"message": "Welcome to YT Downloader Service!",
         "syntax": "/download?url=https://www.youtube.com/watch?v=XXXXXXX"}
    )

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    hd = request.args.get('hd', '0') == '1'
    if not url:
        return jsonify(success=False, error="Missing URL"), 400

    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    # try:
    #     filepath = download_youtube_video_file(url, hd=hd)
    # except Exception as e:
    #     return jsonify(success=False, error=str(e)), 500
    
    # response = jsonify({"m": filepath})
        
    # response = send_file(
    #     filepath,
    #     as_attachment=True,
    #     download_name=os.path.basename(filepath),
    #     mimetype='video/mp4'
    # )

    # Optionally, delete file after use
    # @response.call_on_close
    # def cleanup():
    #     try:
    #         os.remove(filepath)
    #     except Exception:
    #         pass

    return response

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
