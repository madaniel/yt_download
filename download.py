#!/usr/bin/env python3
"""
YouTube Downloader Wrapper Script
Simple wrapper that runs run_orig.py from the virtual environment
"""

import os
import sys
import subprocess
from pathlib import Path

def get_venv_python_path():
    """Get the path to the Python executable in the virtual environment"""
    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / "venv"
    
    if sys.platform.startswith('win'):
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    return python_exe

def main():
    """Main wrapper function"""
    print("🚀 Starting YouTube Downloader...")
    
    # Check if virtual environment exists
    python_exe = get_venv_python_path()
    
    if not python_exe.exists():
        print("❌ Virtual environment not found!")
        print(f"Expected Python executable at: {python_exe}")
        print("\n📋 To set up the environment, run these commands:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        print("\nThen run this script again.")
        sys.exit(1)
    
    # Get the path to the main script
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "run_orig.py"
    
    if not main_script.exists():
        print(f"❌ Main script not found at: {main_script}")
        sys.exit(1)
    
    print("🎬 Running YouTube downloader...")
    
    # Prepare the command
    cmd = [str(python_exe), str(main_script)] + sys.argv[1:]
    
    try:
        # Run the main script with all arguments passed through
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"❌ Script execution failed with exit code: {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n⏹️ Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()