import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from moviepy import VideoFileClip

def extract(input_video, output_audio):
    # Load the video file
    video = VideoFileClip(input_video)

    # Extract audio
    audio = video.audio

    # Save audio to file
    audio.write_audiofile(output_audio)
