import yt_dlp
import subprocess
import os
import sys

def download_youtube_video_1080p(url, download_path="."):
    downloaded_file = None  # this will store the full path to the downloaded file
    
    ydl_opts = {
        # More flexible format selection - try 1080p first, then fallback to best available
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': '/Users/user/Git/yt_download/cookies.txt', 
        'cookies-from-browser': 'chrome',  # Use cookies directly from your browser session
    }
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            print(f"Downloaded 1080p video from: {url}")
            
        except Exception as e:
            print(f"An error occurred: {e}")

def get_codec(file_path, stream_type):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", f"{stream_type}:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=nw=1:nk=1",
                file_path
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
    if not os.path.isfile(file_path):
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
        print("❌ Not Plex-friendly - run re-encode function")
        return False


def get_mp4_files(folder="."):
    return [
        os.path.abspath(f)
        for f in os.listdir(folder)
        if f.endswith(".mp4") and os.path.isfile(os.path.join(folder, f))
    ]

def reencode_to_plex_friendly(input_path, output_path):
    print(f"⚙️ Re-encoding '{input_path}' to Plex-friendly format...")
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", input_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-movflags", "+faststart",
                "-preset", "slow",  # can use "fast" for quicker encodes
                output_path
            ],
            check=True
        )
        print(f"✅ Re-encoded and saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Re-encoding failed: {e}")


def trim_video(input_file: str, output_file: str, cut_seconds: int) -> bool:
    """
    Trim `cut_seconds` from the end of an MP4 file without re-encoding.

    Requires `ffmpeg` and `ffprobe` installed (macOS: `brew install ffmpeg`).

    :param input_file: Path to source MP4 file
    :param output_file: Path to output trimmed MP4 file
    :param cut_seconds: Number of seconds to cut from the end
    :return: True if success, False if error
    """
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found.")
        return False

    # Get video duration using ffprobe
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
    except Exception as e:
        print("❌ Error reading file duration:", e)
        return False

    new_duration = max(0, duration - cut_seconds)

    # Run ffmpeg to trim down video
    cmd = [
        "ffmpeg",
        "-y",              # overwrite if exists
        "-i", input_file,  # input file
        "-t", str(new_duration),  # set new duration
        "-c", "copy",      # copy codec (no re-encode)
        output_file
    ]

    print("▶️ Running:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Trimmed video written to: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg failed:", e)
        return False



video_url, trim_seconds = "https://www.youtube.com/watch?v=e85suzRafVQ", 0



download_youtube_video_1080p(video_url)
mp4_files = get_mp4_files()
[is_plex_friendly(mp4) for mp4 in mp4_files]


# Need only one video file to enable trim
if trim_seconds == 0 or len(mp4_files) > 1:
    print("Trimming skipped !")
    sys.exit(1)

# Cut last 10 seconds
success = trim_video(mp4_files[0], "output_trimmed.mp4", trim_seconds)

if success:
    print("✅ Video successfully trimmed.")
else:
    print("Trimming failed.")
