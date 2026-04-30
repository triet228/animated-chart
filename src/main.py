# src/main.py

import sys
import subprocess
import os
import random
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
from moviepy import VideoFileClip, AudioFileClip

import generate_data

# ==========================================
# 1. GLOBAL CONFIGURATION
# ==========================================
FPS = 60
DURATION_SECONDS = 2
PAUSE_SECONDS = 3
INITIAL_INVESTMENT = 10000
START_YEAR, END_YEAR = 0, 2025

# Path management
src_dir = Path(__file__).parent
project_root = src_dir.parent
csv_file = src_dir / "data.csv"
output_name = str(src_dir / "output.mp4")
temp_video_path = str(src_dir / 'temp_silent.mp4')

# Visual Styling
PALETTE = [
    '#00E5FF', '#76FF03', '#FFD600', '#FF1744', '#D500F9',
    '#1DE9B6', '#FF9100', '#F50057', '#2979FF', '#C6FF00'
]

# ==========================================
# 2. DATA PREPARATION
# ==========================================
def load_and_clean_data():
    if not csv_file.exists():
        print("data.csv not found. Fetching data...")
        df = generate_data.get_portfolio_data()
        df.to_csv(csv_file, index=False)
    else:
        df = pd.read_csv(csv_file)

    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    
    tickers = [col for col in df.columns if col not in ['Date', 'Year']]
    
    for col in tickers:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('%', '').replace('', np.nan).astype(float)
            
    df = df[(df['Year'] >= START_YEAR) & (df['Year'] <= END_YEAR)]
    return df.dropna(subset=tickers).reset_index(drop=True), tickers

data, tickers = load_and_clean_data()
COLORS = random.sample(PALETTE, len(tickers))

# ==========================================
# 3. MATHEMATICAL INTERPOLATION
# ==========================================
compounded = (1 + data[tickers] / 100).cumprod()
raw_values = pd.concat([
    pd.DataFrame([[1.0]*len(tickers)], columns=tickers), 
    compounded
], ignore_index=True) * INITIAL_INVESTMENT

raw_dates = [data['Date'].iloc[0] - pd.DateOffset(months=1)] + data['Date'].tolist()
raw_date_nums = mdates.date2num(raw_dates)

ANIMATION_FRAMES = FPS * DURATION_SECONDS
TOTAL_FRAMES = ANIMATION_FRAMES + (FPS * PAUSE_SECONDS)

x_old = np.linspace(0, len(raw_values) - 1, len(raw_values))
x_new = np.linspace(0, len(raw_values) - 1, ANIMATION_FRAMES)

value_data = pd.DataFrame({col: np.interp(x_new, x_old, raw_values[col]) for col in tickers})
dates_interp = np.interp(x_new, x_old, raw_date_nums)

# ==========================================
# 4. PLOT & ANIMATION SETUP
# ==========================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 16), dpi=120)
plt.subplots_adjust(left=0.18, right=0.75, top=0.85, bottom=0.15)

# Axis Styling
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#444444')
ax.spines['bottom'].set_color('#444444')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

def currency_fmt(x, pos=None):
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    return f'${x*1e-3:.0f}K' if x >= 1e3 else f'${x:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency_fmt))
ax.tick_params(axis='both', labelsize=12, colors='#888888')
ax.set_title(" VS ".join(tickers).upper(), fontsize=40, pad=50, fontweight='bold')

# Graphical Elements
lines = [ax.plot([], [], label=t, color=COLORS[i], lw=5)[0] for i, t in enumerate(tickers)]
line_labels = [ax.text(0, 0, f" {t}", color=COLORS[i], fontsize=12, 
                       fontweight='bold', va='center') for i, t in enumerate(tickers)]
winner_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha='center', 
                      fontsize=45, fontweight='bold', color='white', alpha=0)

# ==========================================
# 5. RENDERING ENGINE
# ==========================================
def init():
    ax.set_xlim(dates_interp[0], dates_interp[1])
    ax.set_ylim(INITIAL_INVESTMENT * 0.9, INITIAL_INVESTMENT * 1.1)
    return *lines, *line_labels, winner_text

pbar = tqdm(total=TOTAL_FRAMES, desc="Rendering")

def update(frame):
    pbar.update(1)
    idx = max(1, min(frame, ANIMATION_FRAMES - 1))
    current_slice = value_data.iloc[:idx+1]

    for i, ticker in enumerate(tickers):
        lines[i].set_data(dates_interp[:idx+1], current_slice[ticker])
        current_x, current_y = dates_interp[idx], current_slice[ticker].iloc[-1]
        line_labels[i].set_position((current_x, current_y + 1000))
    
    ax.set_xlim(dates_interp[0], dates_interp[idx] + 150)
    ax.set_ylim(current_slice.min().min() * 0.95, current_slice.max().max() * 1.1)
    return *lines, *line_labels, winner_text

# Save silent video
ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES, init_func=init, blit=False)
ani.save(temp_video_path, writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# ==========================================
# 6. AUDIO MERGE & EXPORT
# ==========================================
songs_dir = project_root / "songs"
available_songs = list(songs_dir.glob("*.mp3"))
if not available_songs:
    raise FileNotFoundError(f"No .mp3 files in {songs_dir}")

video_clip = VideoFileClip(temp_video_path)
audio_clip = AudioFileClip(str(random.choice(available_songs))).subclipped(2, 2 + video_clip.duration)

final_video = video_clip.with_audio(audio_clip)
final_video.write_videofile(output_name, codec="libx264", threads=8, fps=FPS)

video_clip.close()
audio_clip.close()
final_video.close()

if os.path.exists(temp_video_path):
    os.remove(temp_video_path)

# ==========================================
# 7. FINAL LAUNCH
# ==========================================
print("Opening video...")
if sys.platform == "win32":
    os.startfile(output_name)
elif sys.platform == "darwin":
    subprocess.call(["open", output_name])
else:
    subprocess.call(["xdg-open", output_name])
