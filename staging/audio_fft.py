import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def fft_analysis(audio_file, audio_format):
    # Step 1: Load audio file
    audio = AudioSegment.from_file(audio_file, format=audio_format)

    # Step 2: Convert file to raw audio data and handle stereo audio
    raw_data = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate

    # If stereo, convert to mono by averaging channels
    if raw_data.ndim == 2:
        raw_data = raw_data.mean(axis=1)

    # Normalize the audio data
    audio_data = raw_data / np.max(np.abs(raw_data))

    # Step 3: Compute the FFT
    fft_result = np.fft.rfft(audio_data)
    frequencies = np.fft.rfftfreq(len(fft_result), 1 / sample_rate)

    # Take the magnitude of the FFT result
    magnitude = np.abs(fft_result)

    # Convert amplitude to decibels
    magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Avoid log(0) by adding a small value

    # Step 4: Create a logarithmic frequency grid
    log_freqs = np.logspace(np.log10(frequencies[1]), np.log10(frequencies[-1]), num=500)

    # Step 5: Interpolate the FFT data onto the logarithmic frequency grid
    interp_magnitude_db = interp1d(frequencies, magnitude_db, kind="linear", bounds_error=False, fill_value="extrapolate")
    log_magnitude_db = interp_magnitude_db(log_freqs)

    # # Step 6: Plot the frequency spectrum
    # plt.figure(figsize=(12, 6))
    # plt.semilogx(log_freqs, log_magnitude_db)
    # plt.title("Frequency Spectrum (Logarithmic Frequency and Amplitude)")
    # plt.xlabel("Frequency (Hz)")
    # plt.ylabel("Amplitude (dB)")
    # plt.grid(which="both", linestyle="--", linewidth=0.5)
    # plt.show()

    return np.column_stack((log_freqs, log_magnitude_db))
