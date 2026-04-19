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
DURATION_SECONDS = 15  
TOTAL_FRAMES = FPS * DURATION_SECONDS
INITIAL_INVESTMENT = 10000

# Set specific years or None
START_YEAR = 2000  
END_YEAR = 2024    

# Random song selection
song_num = random.randint(1, 100)
audio_path = os.path.join("songs", f"song{song_num:03}.mp3")

# 2. Data Cleaning & Range Filtering
data = pd.read_csv(csv_file)

for col in tickers:
    if data[col].dtype == 'object':
        data[col] = data[col].str.replace('%', '').astype(float)

if START_YEAR:
    data = data[data['Year'] >= START_YEAR]
if END_YEAR:
    data = data[data['Year'] <= END_YEAR]

data = data.dropna(subset=tickers).reset_index(drop=True)

if data.empty:
    print("Error: No data for the specified years.")
    exit()

# Portfolio Math
compounded = (1 + data[tickers] / 100).cumprod()
start_row = pd.DataFrame([[1.0] * len(tickers)], columns=tickers)
raw_values = pd.concat([start_row, compounded], ignore_index=True) * INITIAL_INVESTMENT
raw_years = [data['Year'].iloc[0] - 1] + data['Year'].tolist()

# Interpolation
x_old = np.linspace(0, len(raw_values) - 1, len(raw_values))
x_new = np.linspace(0, len(raw_values) - 1, TOTAL_FRAMES)
value_data = pd.DataFrame({col: np.interp(x_new, x_old, raw_values[col]) for col in tickers})
years_interp = np.interp(x_new, x_old, raw_years)

# 3. Setup Plot
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 16), dpi=120)
plt.subplots_adjust(left=0.18, right=0.9, top=0.85, bottom=0.15) 

line1, = ax.plot([], [], label=tickers[0], color='#00ffcc', lw=5)
line2, = ax.plot([], [], label=tickers[1], color='#ff0077', lw=5)
ax.legend(loc='upper center', fontsize=22, frameon=False, ncol=2)

def currency(x, pos=None):
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    return f'${x*1e-3:.0f}K' if x >= 1e3 else f'${x:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency))
year_text = ax.text(0.5, 0.92, '', transform=ax.transAxes, ha='center', fontsize=32, fontweight='bold', color='#FFD700')
winner_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha='center', fontsize=45, fontweight='bold', color='white', alpha=0)

# FIXED: Dynamic Y-axis limits
def init():
    ax.set_xlim(min(raw_years), max(raw_years))
    
    # Dynamically find the absolute bottom and top
    ymin = value_data.min().min()
    ymax = value_data.max().max()
    
    # Apply a 10% buffer so lines don't touch the edges
    ax.set_ylim(ymin * 0.9, ymax * 1.1)
    return line1, line2, year_text

# 4. Rendering
pbar = tqdm(total=TOTAL_FRAMES, desc="Rendering Video")
def update(frame):
    pbar.update(1)
    line1.set_data(years_interp[:frame], value_data[tickers[0]][:frame])
    line2.set_data(years_interp[:frame], value_data[tickers[1]][:frame])
    year_text.set_text(f"YEAR: {int(years_interp[frame])}")
    
    if frame == TOTAL_FRAMES - 1:
        win = tickers[0] if value_data[tickers[0]].iloc[-1] > value_data[tickers[1]].iloc[-1] else tickers[1]
        winner_text.set_text(f"{win} WINS!\n{currency(value_data[win].iloc[-1])}")
        winner_text.set_alpha(1)
    return line1, line2, year_text, winner_text

ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES, init_func=init, blit=True)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge
video_clip = VideoFileClip("temp_silent.mp4")
final_video = video_clip.with_audio(AudioFileClip(audio_path).subclipped(0, video_clip.duration))
final_video.write_videofile("fixed_battle_output.mp4", codec="libx264", threads=8, fps=FPS)
os.remove("temp_silent.mp4")
