"""
video_extractor.py
Utility to download videos/shorts from TikTok, YouTube, Instagram Reels, etc.
using `uvx yt-dlp` and extract audio/keyframes with `ffmpeg` for visual inspection.
"""

import subprocess
import os
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

def download_media(video_url: str, output_dir: str, prefix: str = "video") -> dict:
    """
    Downloads both video (.mp4) and audio (.mp3) using uvx yt-dlp.
    """
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"{prefix}.mp4")
    audio_path = os.path.join(output_dir, f"{prefix}_audio.mp3")

    # 1. Download video
    print(f"Downloading video from {video_url} ...")
    cmd_video = ["uvx", "yt-dlp", "-f", "b", "-o", video_path, video_url]
    subprocess.run(cmd_video, check=True)

    # 2. Extract audio
    print(f"Extracting audio to {audio_path} ...")
    cmd_audio = ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "libmp3lame", audio_path]
    subprocess.run(cmd_audio, check=True)

    return {
        "video": video_path,
        "audio": audio_path
    }

def extract_frames(video_path: str, frames_dir: str, fps: float = 1.0) -> list[str]:
    """
    Extracts frames at specified rate (e.g. fps=1 for 1 frame per second).
    """
    os.makedirs(frames_dir, exist_ok=True)
    pattern = os.path.join(frames_dir, "frame_%04d.jpg")
    print(f"Extracting frames at {fps} fps to {frames_dir} ...")
    cmd = ["ffmpeg", "-y", "-i", video_path, "-vf", f"fps={fps}", pattern]
    subprocess.run(cmd, check=True)

    frames = sorted(glob.glob(os.path.join(frames_dir, "frame_*.jpg")))
    print(f"Extracted {len(frames)} frames.")
    return frames

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_extractor.py <video_url> [output_dir]")
        sys.exit(1)
    
    url = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "downloaded_video")
    
    media = download_media(url, out_dir)
    frames_dir = os.path.join(out_dir, "frames")
    extract_frames(media["video"], frames_dir, fps=1.0)
    print("Extraction complete!")
