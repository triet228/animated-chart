import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import random
import os
from moviepy import VideoFileClip, AudioFileClip

# 1. Configuration
csv_file = "data.csv" 
tickers = ['VOO', 'ONEQ'] 
FPS = 60 
DURATION_SECONDS = 15  # How long you want the video to be
TOTAL_FRAMES = FPS * DURATION_SECONDS

# Random song selection
song_num = random.randint(1, 100)
audio_path = os.path.join("songs", f"song{song_num:03}.mp3")

# 2. Data Cleaning & Interpolation
data = pd.read_csv(csv_file).dropna().reset_index(drop=True)
for col in tickers:
    if data[col].dtype == 'object':
        data[col] = data[col].str.replace('%', '').astype(float)

# Cumulative Math
compounded = (1 + data[tickers] / 100).cumprod()
start_val = pd.DataFrame([[1.0] * len(tickers)], columns=tickers)
raw_pct = (pd.concat([start_val, compounded], ignore_index=True) - 1) * 100
raw_years = [data['Year'].iloc[0] - 1] + data['Year'].tolist()

# INTERPOLATION: Stretch data to fill the duration
x_old = np.linspace(0, len(raw_pct) - 1, len(raw_pct))
x_new = np.linspace(0, len(raw_pct) - 1, TOTAL_FRAMES)

pct_data = pd.DataFrame({
    col: np.interp(x_new, x_old, raw_pct[col]) for col in tickers
})
years_interp = np.interp(x_new, x_old, raw_years)

# 3. Setup Plot
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 16), dpi=120)
plt.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.15)

line1, = ax.plot([], [], label=tickers[0], color='#00ffcc', lw=5, zorder=3)
line2, = ax.plot([], [], label=tickers[1], color='#ff0077', lw=5, zorder=3)
ax.legend(loc='upper center', fontsize=22, frameon=False, ncol=2)

year_text = ax.text(0.5, 0.92, '', transform=ax.transAxes, ha='center', 
                    fontsize=32, fontweight='bold', color='#FFD700')
winner_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha='center', 
                      fontsize=50, fontweight='bold', color='white', alpha=0)

def init():
    ax.set_xlim(0, TOTAL_FRAMES)
    ax.set_ylim(pct_data.min().min() - 10, pct_data.max().max() + 20)
    return line1, line2, year_text

# 4. Rendering
pbar = tqdm(total=TOTAL_FRAMES, desc="Rendering 60FPS Video")

def update(frame):
    pbar.update(1)
    line1.set_data(range(frame), pct_data[tickers[0]][:frame])
    line2.set_data(range(frame), pct_data[tickers[1]][:frame])
    year_text.set_text(f"YEAR: {int(years_interp[frame])}")
    
    # Final Frame: Show the Winner
    if frame == TOTAL_FRAMES - 1:
        winner = tickers[0] if pct_data[tickers[0]].iloc[-1] > pct_data[tickers[1]].iloc[-1] else tickers[1]
        winner_text.set_text(f"{winner} WINS!")
        winner_text.set_alpha(1)
        
    return line1, line2, year_text, winner_text

ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES, init_func=init, blit=True)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge
print("Finalizing Video...")
video_clip = VideoFileClip("temp_silent.mp4")
audio_clip = AudioFileClip(audio_path).subclipped(0, video_clip.duration)
final_video = video_clip.with_audio(audio_clip)
final_video.write_videofile("shorts_output.mp4", codec="libx264", audio_codec="aac", threads=8, fps=FPS)

# 6. Cleanup
video_clip.close()
audio_clip.close()
if os.path.exists("temp_silent.mp4"): os.remove("temp_silent.mp4")
