import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

import numpy as np
from preprocessing import audio_fft, combine_wav_mp4, extract_wav
from configs.config import lv_orig_dir, lv_conv_dir, tw_orig_mp4_dir, tw_orig_wav_dir

def lv_fft():
    # perform FFT on LV tracks
    # store dir paths in list
    lv_list = [lv_orig_dir, lv_conv_dir]

    for dir in lv_list:
        # set directory path
        lv_dir_audio = dir + "\\audio"
        lv_dir_fft = dir + "\\fft"

        # create directory for FFT files
        os.makedirs(lv_dir_fft, exist_ok=True)

        # access audio files and save FFT
        for name in os.listdir(lv_dir_audio):
            audio_format = name.split(".")[-1]
            output_name = name.replace(audio_format, "txt")
            # perform FFT and save it in specified directory
            fft_file = audio_fft.fft_analysis(lv_dir_audio + "\\" + name, audio_format)
            np.savetxt(lv_dir_fft + "\\" + output_name, fft_file)

def tw_orig_wav():
    # extract audio from original twitch clips and perform FFT
    # set directory path
    tw_orig_dir_audio = tw_orig_wav_dir + "\\audio"
    tw_orig_dir_fft = tw_orig_wav_dir + "\\fft"

    # create directory for FFT files
    os.makedirs(tw_orig_dir_fft, exist_ok=True)

    # access video files
    for name in os.listdir(tw_orig_mp4_dir):
        # change output file extension to .wav
        file_format = name.split(".")[-1]
        output_name = name.replace(file_format, "wav")
        # extract audio and save it in specified directory
        extract_wav.extract(tw_orig_mp4_dir + "\\" + name, tw_orig_dir_audio + "\\" + output_name)

    # access audio files
    for name in os.listdir(tw_orig_dir_audio):
        audio_format = name.split(".")[-1]
        output_name = name.replace(audio_format, "txt")
        # perform FFT and save it in specified directory
        fft_file = audio_fft.fft_analysis(tw_orig_dir_audio + "\\" + name, audio_format)
        np.savetxt(tw_orig_dir_fft + "\\" + output_name, fft_file)

def combine():
    # merge original mp4 with converted wav from tw clips
    pass

def main():
    pass


if __name__ == "__main__":
    main()
