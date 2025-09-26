import subprocess
import os
import sys

def cut_from_end(input_file, output_file, cut_seconds):
    """
    Trim `cut_seconds` from the end of an MP4 file without re-encoding.
    Works on macOS (requires ffmpeg installed).
    
    :param input_file: Path to source MP4 file
    :param output_file: Path to output trimmed MP4 file
    :param cut_seconds: Number of seconds to cut from the end
    """
    # Get video duration in seconds
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if result.returncode != 0:
        print("Error reading input file duration:", result.stderr)
        return
    
    duration = float(result.stdout.strip())
    new_duration = max(0, duration - cut_seconds)
    
    # Run ffmpeg to trim without re-encoding
    cmd = [
        "ffmpeg",
        "-y",              # overwrite output if exists
        "-i", input_file,  # input file
        "-t", str(new_duration),  # new duration
        "-c", "copy",      # no re-encoding
        output_file
    ]
    
    print("Running:", " ".join(cmd))
    subprocess.run(cmd)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python trim_end.py input.mp4 output.mp4 seconds_to_cut")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    cut_seconds = int(sys.argv[3])

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    cut_from_end(input_file, output_file, cut_seconds)