import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt

def fft_analysis(audio_file, audio_format):
    # Step 1: Load MP3 file
    audio = AudioSegment.from_file(audio_file, format=audio_format)

    # Step 2: Convert to raw audio data
    # Get raw audio data as a NumPy array
    raw_data = np.array(audio.get_array_of_samples())

    # Get the sample rate
    sample_rate = audio.frame_rate

    # Step 3: Compute the FFT
    # Apply FFT to the raw audio data
    fft_result = np.fft.fft(raw_data)
    frequencies = np.fft.fftfreq(len(fft_result), 1 / sample_rate)

    # Take the magnitude of the FFT result
    magnitude = np.abs(fft_result)

    # Step 4: Plot the frequency spectrum
    plt.figure(figsize=(12, 6))
    plt.plot(frequencies[:len(frequencies) // 2], magnitude[:len(magnitude) // 2])
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.grid()
    plt.show()
