import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

import numpy as np
from pydub import AudioSegment

def fft_analysis(audio_file, audio_format):

    max_rows = 1000

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
    frequencies = np.fft.rfftfreq(len(audio_data), 1 / sample_rate)

    # Take the magnitude of the FFT result
    magnitude = np.abs(fft_result)

    # Convert amplitude to decibels
    magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Avoid log(0) by adding a small value

    # Step 4: Determine the total number of frequency bins
    total_frequencies = len(frequencies)

    # Step 5: Calculate the index corresponding to 2 kHz
    idx_2kHz = int(2000 / (sample_rate / len(audio_data)))  # Index corresponding to 2 kHz

    # Step 6: Normalize magnitude to ensure average between 0-2 kHz is 30 dB
    idx_0_2kHz = np.arange(0, min(idx_2kHz, total_frequencies))  # Indices from 0 to idx_2kHz
    selected_frequencies = frequencies[idx_0_2kHz]
    selected_magnitude_db = magnitude_db[idx_0_2kHz]

    # Calculate the step size needed to return at most `max_rows` points
    desired_step = max(1, selected_frequencies // max_rows)

    # Select every `desired_step`-th frequency and magnitude to limit the number of rows
    downsampled_frequencies = selected_frequencies[::desired_step]
    downsampled_magnitude_db = selected_magnitude_db[::desired_step]

    # Calculate the average magnitude in dB between 0 and 2 kHz
    avg_0_2kHz = np.mean(downsampled_magnitude_db)

    # Calculate the scaling factor to achieve an average of 30 dB in the 0-2 kHz range
    scaling_factor = 30 - avg_0_2kHz

    # Apply scaling factor to all magnitude values
    downsampled_magnitude_db += scaling_factor

    return np.column_stack((downsampled_frequencies, downsampled_magnitude_db))
