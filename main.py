import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import random
import os
from moviepy import VideoFileClip, AudioFileClip

# 1. Configuration
CHART_TITLE = "SP500 vs Leverage"  # Edit your title here
LOWER_LIMIT = 0  # Edit your lower limit here

csv_file = "data.csv"
tickers = ['SP500', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x', '10x']
FPS = 60 
DURATION_SECONDS = 45  
TOTAL_FRAMES = FPS * DURATION_SECONDS
PAUSE_SECONDS = 0
PAUSE_FRAMES = FPS * PAUSE_SECONDS
INITIAL_INVESTMENT = 100000
START_YEAR, END_YEAR = 0000, 2025
output_name = "output.mp4"

COLORS = [
    '#00ffcc', '#ff0077', '#ffff00', '#0077ff', '#ff8800', 
    '#cc00ff', '#ffffff', '#00ff00', '#ff0000', '#00ffff'
]
audio_path = os.path.join("songs", f"song{random.randint(1, 100):03}.mp3")

# 2. Data Cleaning
data = pd.read_csv(csv_file)
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year

for col in tickers:
    if data[col].dtype == 'object':
        data[col] = data[col].str.replace('%', '').astype(float)

data = data[(data['Year'] >= START_YEAR) & (data['Year'] <= END_YEAR)]
data = data.dropna(subset=tickers).reset_index(drop=True)

# Math & Date Interpolation
compounded = (1 + data[tickers] / 100).cumprod()
raw_values = pd.concat([pd.DataFrame([[1.0]*len(tickers)], columns=tickers), compounded], ignore_index=True) * INITIAL_INVESTMENT

# FIX: Force bankrupt tickers to stay at LOWER_LIMIT once they hit it
for col in tickers:
    hit_mask = raw_values[col] <= LOWER_LIMIT
    if hit_mask.any():
        first_hit_idx = hit_mask.idxmax()
        raw_values.loc[first_hit_idx:, col] = LOWER_LIMIT

raw_dates = [data['Date'].iloc[0] - pd.DateOffset(months=1)] + data['Date'].tolist()
raw_date_nums = mdates.date2num(raw_dates)

x_old = np.linspace(0, len(raw_values) - 1, len(raw_values))
x_new = np.linspace(0, len(raw_values) - 1, TOTAL_FRAMES)

value_data = pd.DataFrame({col: np.interp(x_new, x_old, raw_values[col]) for col in tickers})
dates_interp = np.interp(x_new, x_old, raw_date_nums)

# 3. Plot Setup
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(9, 16), dpi=120)
plt.subplots_adjust(left=0.18, right=0.9, top=0.85, bottom=0.15) 

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#444444')
ax.spines['bottom'].set_color('#444444')

lines = [ax.plot([], [], label=t, color=COLORS[i % len(COLORS)], lw=5)[0] for i, t in enumerate(tickers)]
line_labels = [ax.text(0, 0, f" {t}", color=COLORS[i % len(COLORS)], 
                       fontsize=18, fontweight='bold', va='center') for i, t in enumerate(tickers)]

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(fontsize=18, color='#888888')

def currency(x, pos=None):
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    return f'${x*1e-3:.0f}K' if x >= 1e3 else f'${x:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency))
ax.tick_params(axis='both', labelsize=18, colors='#888888')
ax.set_title(CHART_TITLE, fontsize=40, pad=50, fontweight='bold')

# Lower Limit Line
ax.axhline(y=LOWER_LIMIT, color='red', linestyle='--', alpha=0.5, lw=3)
ax.text(dates_interp[0], LOWER_LIMIT + 2000, f" BANKRUPTCY = {currency(LOWER_LIMIT)}", color='red', 
        fontsize=20, fontweight='bold', alpha=0.7, va='bottom')

def init():
    ax.set_xlim(dates_interp[0], dates_interp[1])
    ax.set_ylim(INITIAL_INVESTMENT * 0.9, INITIAL_INVESTMENT * 1.1)
    return *lines, *line_labels  

# 4. Rendering Setup
# Find the first frame where ANY ticker hits the limit
hit_frames = value_data[(value_data[tickers] <= LOWER_LIMIT).any(axis=1)].index
first_hit_frame = hit_frames[0] if len(hit_frames) > 0 else None

# Animation will be longer by the duration of the pause
ANIMATION_FRAMES = TOTAL_FRAMES + PAUSE_FRAMES if first_hit_frame is not None else TOTAL_FRAMES

pbar = tqdm(total=ANIMATION_FRAMES, desc="Rendering")

def update(frame):
    pbar.update(1)
    
    # Pause Logic: If we've hit the bankruptcy line, freeze frame for PAUSE_FRAMES
    if first_hit_frame is not None:
        if frame < first_hit_frame:
            current_idx = frame
        elif frame < first_hit_frame + PAUSE_FRAMES:
            current_idx = first_hit_frame
        else:
            current_idx = frame - PAUSE_FRAMES
    else:
        current_idx = frame
        
    current_idx = min(max(1, current_idx), TOTAL_FRAMES - 1)
    current_slice = value_data.iloc[:current_idx+1]
    
    for i, ticker in enumerate(tickers):
        lines[i].set_data(dates_interp[:current_idx+1], current_slice[ticker])
        current_x = dates_interp[current_idx]
        current_y = current_slice[ticker].iloc[-1]
        line_labels[i].set_position((current_x, current_y + 200))
    
    ax.set_xlim(dates_interp[0], dates_interp[current_idx] + 150)
    current_min = current_slice.min().min()
    current_max = current_slice.max().max()
    
    plot_min = min(current_min * 0.95, LOWER_LIMIT - 5000)
    ax.set_ylim(plot_min, current_max * 1.1)

    return *lines, *line_labels  

ani = FuncAnimation(fig, update, frames=ANIMATION_FRAMES, init_func=init, blit=False)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge
video_clip = VideoFileClip("temp_silent.mp4")
final_video = video_clip.with_audio(AudioFileClip(audio_path).subclipped(0, video_clip.duration))
final_video.write_videofile(output_name, codec="libx264", threads=8, fps=FPS)

video_clip.close()
if os.path.exists("temp_silent.mp4"):
    os.remove("temp_silent.mp4")
