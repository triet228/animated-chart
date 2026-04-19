import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import random
import os
from moviepy import VideoFileClip, AudioFileClip

# 1. Configuration
csv_file = "data.csv" 
tickers = ['VOO', 'ONEQ'] # Ensure these columns exist in data.csv
FPS = 60 

# Random song selection
song_num = random.randint(1, 100)
audio_path = os.path.join("songs", f"song{song_num:03}.mp3")

# 2. Data Cleaning & Cumulative Math
data = pd.read_csv(csv_file).dropna().reset_index(drop=True)

for col in tickers:
    if data[col].dtype == 'object':
        data[col] = data[col].str.replace('%', '').astype(float)

# Calculate Cumulative Growth: (1 + r/100).cumprod()
compounded = (1 + data[tickers] / 100).cumprod()
start_val = pd.DataFrame([[1.0] * len(tickers)], columns=tickers)
pct_data = (pd.concat([start_val, compounded], ignore_index=True) - 1) * 100
years = [data['Year'].iloc[0] - 1] + data['Year'].tolist()

# 3. Setup 9:16 Plot
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 16), dpi=120)
plt.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)

ax.set_title("THE ULTIMATE BATTLE", fontsize=35, pad=60, fontweight='bold')
line1, = ax.plot([], [], label=tickers[0], color='#00ffcc', lw=5)
line2, = ax.plot([], [], label=tickers[1], color='#ff0077', lw=5)
ax.legend(loc='upper center', fontsize=22, frameon=False, ncol=2)

year_text = ax.text(0.5, 0.92, '', transform=ax.transAxes, 
                    ha='center', fontsize=32, fontweight='bold', color='#FFD700')

def init():
    ax.set_xlim(0, len(pct_data))
    ax.set_ylim(pct_data.min().min() - 10, pct_data.max().max() + 10)
    return line1, line2, year_text

# 4. 60 FPS Rendering
pbar = tqdm(total=len(pct_data), desc="Rendering 60FPS Video")

def update(frame):
    pbar.update(1)
    line1.set_data(range(frame), pct_data[tickers[0]][:frame])
    line2.set_data(range(frame), pct_data[tickers[1]][:frame])
    year_text.set_text(f"YEAR: {int(years[frame])}")
    return line1, line2, year_text

ani = FuncAnimation(fig, update, frames=len(pct_data), init_func=init, blit=True)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge (MoviePy 2.0)
print("Finalizing Audio...")
video_clip = VideoFileClip("temp_silent.mp4")
audio_clip = AudioFileClip(audio_path).subclipped(0, video_clip.duration)
final_video = video_clip.with_audio(audio_clip)

final_video.write_videofile("shorts_output.mp4", codec="libx264", audio_codec="aac", threads=8, fps=FPS)

# 6. Cleanup
video_clip.close()
audio_clip.close()
if os.path.exists("temp_silent.mp4"): os.remove("temp_silent.mp4")

print(f"\nDone! Smooth 60FPS video saved using {audio_path}")
