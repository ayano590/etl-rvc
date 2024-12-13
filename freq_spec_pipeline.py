import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

import numpy as np
from staging import audio_fft, combine_wav_mp4


lv_orig_dir = os.getenv("lv_orig_dir")
lv_conv_dir = os.getenv("lv_conv_dir")
tw_orig_wav_dir = os.getenv("tw_orig_wav_dir")
tw_orig_mp4_dir = os.getenv("tw_orig_mp4_dir")
tw_conv_wav_dir = os.getenv("tw_conv_wav_dir")
tw_conv_mp4_dir = os.getenv("tw_conv_mp4_dir")

def lv_fft():
    # perform FFT on LV tracks
    # store dir paths in list
    lv_list = [lv_orig_dir, lv_conv_dir]

    for dir in lv_list:
        # set directory path
        lv_dir_audio = dir + "/audio"
        lv_dir_fft = dir + "/fft"

        # create directory for FFT files
        os.makedirs(lv_dir_fft, exist_ok=True)

        # access audio files and save FFT
        for name in os.listdir(lv_dir_audio):
            audio_format = name.split(".")[-1]
            output_name = name.replace(audio_format, "txt")

            if not os.path.isfile(lv_dir_fft + "/" + output_name):
                # perform FFT and save it in specified directory
                fft_file = audio_fft.fft_analysis(lv_dir_audio + "/" + name, audio_format)
                np.savetxt(lv_dir_fft + "/" + output_name, fft_file)

def tw_fft():
    # perform FFT on TW clips
    tw_list = [tw_orig_wav_dir, tw_conv_wav_dir]

    for dir in tw_list:
        # set directory path
        tw_dir_audio = dir + "/audio"
        tw_dir_fft = dir + "/fft"

        # create directory for FFT files
        os.makedirs(tw_dir_fft, exist_ok=True)

        # access audio files and save FFT
        for name in os.listdir(tw_dir_audio):
            audio_format = name.split(".")[-1]
            output_name = name.replace(audio_format, "txt")

            if not os.path.isfile(tw_dir_fft + "/" + output_name):
                # perform FFT and save it in specified directory
                fft_file = audio_fft.fft_analysis(tw_dir_audio + "/" + name, audio_format)
                np.savetxt(tw_dir_fft + "/" + output_name, fft_file)

def combine():
    # merge original mp4 with converted wav from tw clips
    # iterate over original tw mp4 files
    for name in os.listdir(tw_orig_mp4_dir):
        [title, file_format] = name.split(".")

        # iterate over converted tw wav files
        for audio_name in os.listdir(tw_conv_wav_dir + "/audio"):
            # check if the title matches
            audio_title = audio_name.split(".")[0]

            if audio_title.startswith(title):
                if not os.path.isfile(tw_conv_mp4_dir + "/" + audio_title + "." + file_format):
                    combine_wav_mp4.merge_av(
                        tw_conv_wav_dir + "/audio/" + audio_name,
                        tw_orig_mp4_dir + "/" + name,
                        tw_conv_mp4_dir + "/" + audio_title + "." + file_format)

def main():
    lv_fft()
    tw_fft()
    combine()


if __name__ == "__main__":
    main()
