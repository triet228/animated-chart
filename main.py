import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import random
import os
from moviepy.editor import VideoFileClip, AudioFileClip

# 1. Configuration
tickers = ['AAPL', 'MSFT']
FPS = 30
# Select a random song from song001.mp3 to song100.mp3
random_audio = f"song{random.randint(1, 100):03}.mp3"

# 2. Data Download
print(f"Downloading data and preparing {random_audio}...")
data = yf.download(tickers, period='5d', interval='1m')['Close'].dropna()

# 3. Setup 9:16 Vertical Plot
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 16), dpi=120)
plt.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)

ax.set_title("STOCK BATTLE", fontsize=40, pad=40, fontweight='bold')
line1, = ax.plot([], [], label=tickers[0], color='#00ffcc', lw=4)
line2, = ax.plot([], [], label=tickers[1], color='#ff0077', lw=4)
ax.legend(loc='upper center', fontsize=20, frameon=False, ncol=2)

def init():
    ax.set_xlim(0, len(data))
    ax.set_ylim(data.min().min() * 0.99, data.max().max() * 1.01)
    return line1, line2

# 4. Animation & Progress Bar
pbar = tqdm(total=len(data), desc="Rendering Video")

def update(frame):
    pbar.update(1)
    line1.set_data(range(frame), data[tickers[0]][:frame])
    line2.set_data(range(frame), data[tickers[1]][:frame])
    return line1, line2

ani = FuncAnimation(fig, update, frames=len(data), init_func=init, blit=True)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS)
pbar.close()

# 5. Add Music with MoviePy
print("Merging audio...")
video_clip = VideoFileClip("temp_silent.mp4")
audio_clip = AudioFileClip(random_audio).subclip(0, video_clip.duration)

final_video = video_clip.set_audio(audio_clip)
final_video.write_videofile("shorts.mp4", codec="libx264", audio_codec="aac")

# Cleanup
video_clip.close()
audio_clip.close()
os.remove("temp_silent.mp4")

print("\nDone! 'shorts.mp4' is ready for YouTube.")
