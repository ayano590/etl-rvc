import numpy as np
import pyaudio as pa
import struct
import matplotlib.pyplot as plt
from pprint import pprint

p = pa.PyAudio()

CHUNK = 8192
FORMAT = pa.paInt16
CHANNELS = 8
RATE = 44100

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    input_device_index=9,
    frames_per_buffer=CHUNK
)

fig, (ax1,ax2) = plt.subplots(2)
x_fft = np.linspace(0, RATE, CHUNK)
x = np.arange(0, 2 * CHUNK, 2)
line, = ax1.plot(x, np.random.rand(CHUNK),'r')
line_fft, = ax2.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax1.set_ylim(-2000,2000)
ax1.ser_xlim = (0, CHUNK)
ax2.set_xlim(20, RATE/2)
ax2.set_ylim(0,0.05)
fig.show()

while 1:
    data = stream.read(CHUNK)
    dataInt = struct.unpack(str(CHUNK * CHANNELS) + 'h', data)
    channel_data = dataInt[::CHANNELS]
    line.set_ydata(channel_data)
    line_fft.set_ydata(np.abs(np.fft.fft(channel_data))*2/(11000*CHUNK))
    fig.canvas.draw()
    fig.canvas.flush_events()