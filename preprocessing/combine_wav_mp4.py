import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from moviepy import VideoFileClip, AudioFileClip

def merge_av(wav_file, mp4_file, output_file):
    # Load the video file
    video = VideoFileClip(mp4_file)

    # Load the new audio file
    new_audio = AudioFileClip(wav_file)

    # Remove the original audio from the video
    video_without_audio = video.without_audio()

    # Add the new audio to the video
    final_video = video_without_audio.set_audio(new_audio)

    # Write the output to a file
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac")
