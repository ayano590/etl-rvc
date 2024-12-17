import os
import sys
from dotenv import load_dotenv

now_dir = os.getcwd()
sys.path.append(now_dir)
load_dotenv()

from pydub import AudioSegment
import numpy as np
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
    frequencies = np.fft.rfftfreq(len(audio_data), 1 / sample_rate)

    # Take the magnitude of the FFT result
    magnitude = np.abs(fft_result)

    # Convert amplitude to decibels
    magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Avoid log(0) by adding a small value

    # Step 4: Create a logarithmic frequency grid
    log_freqs = np.logspace(np.log10(frequencies[1]), np.log10(frequencies[-1]), num=500)

    # Step 5: Interpolate the FFT data onto the logarithmic frequency grid
    interp_magnitude_db = interp1d(frequencies, magnitude_db, kind="linear", bounds_error=False, fill_value="extrapolate")
    log_magnitude_db = interp_magnitude_db(log_freqs)

    # Step 6: Normalize magnitude to ensure average between 0-2 kHz is 30 dB
    # Select the first 392 points (indices 0 to 391) which correspond to the 0-2 kHz range in the log frequency grid
    idx_0_2kHz = np.arange(0, 392)  # Indices from 0 to 391

    # Calculate the average magnitude in dB between 0 and 2 kHz
    avg_0_2kHz = np.mean(log_magnitude_db[idx_0_2kHz])

    # Calculate the scaling factor to achieve an average of 30 dB in the 0-2 kHz range
    scaling_factor = 30 - avg_0_2kHz

    # Apply scaling factor to all magnitude values
    log_magnitude_db += scaling_factor

    return np.column_stack((log_freqs, log_magnitude_db))
