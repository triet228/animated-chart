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
csv_file = "data.csv"
tickers = ['SP500', 'Inflation'] 
FPS = 60 
DURATION_SECONDS = 30  
TOTAL_FRAMES = FPS * DURATION_SECONDS
INITIAL_INVESTMENT = 10000
START_YEAR, END_YEAR = 0, 2025
output_name = "output.mp4"

COLORS = ['#00ffcc', '#ff0077', '#ffff00', '#0077ff', '#ff8800', '#cc00ff', '#ffffff']
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

# REMOVE BORDERS
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#444444')
ax.spines['bottom'].set_color('#444444')

lines = [ax.plot([], [], label=t, color=COLORS[i % len(COLORS)], lw=5)[0] for i, t in enumerate(tickers)]

# ADDED: Moving labels instead of a static legend
line_labels = [ax.text(0, 0, f" {t}", color=COLORS[i % len(COLORS)], 
                       fontsize=12, fontweight='bold', va='center') for i, t in enumerate(tickers)]

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(fontsize=18, color='#888888')

def currency(x, pos=None):
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    return f'${x*1e-3:.0f}K' if x >= 1e3 else f'${x:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency))
ax.tick_params(axis='both', labelsize=12, colors='#888888')
ax.set_title("SP500 VS INFLATION", fontsize=40, pad=50, fontweight='bold')

winner_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha='center', 
                      fontsize=45, fontweight='bold', color='white', alpha=0)

def init():
    ax.set_xlim(dates_interp[0], dates_interp[1])
    ax.set_ylim(INITIAL_INVESTMENT * 0.9, INITIAL_INVESTMENT * 1.1)
    return *lines, *line_labels, winner_text  # UPDATED

# 4. Rendering
pbar = tqdm(total=TOTAL_FRAMES, desc="Rendering")
def update(frame):
    pbar.update(1)
    current_idx = max(1, frame)
    current_slice = value_data.iloc[:current_idx+1]
    
    for i, ticker in enumerate(tickers):
        lines[i].set_data(dates_interp[:current_idx+1], current_slice[ticker])
        # UPDATED: Move the label to the current end of the line
        current_x = dates_interp[current_idx]
        current_y = current_slice[ticker].iloc[-1]
        line_labels[i].set_position((current_x - 80, current_y + 1000))
    
    # UPDATED: Increased padding so text doesn't cut off
    ax.set_xlim(dates_interp[0], dates_interp[current_idx] + 150)
    current_min = current_slice.min().min()
    current_max = current_slice.max().max()
    ax.set_ylim(current_min * 0.95, current_max * 1.1)

    if frame == TOTAL_FRAMES - 1:
        final_scores = {t: value_data[t].iloc[-1] for t in tickers}
        win = max(final_scores, key=final_scores.get)
        winner_text.set_text(f"{win} WINS!\n{currency(final_scores[win])}")
        winner_text.set_alpha(1)
        
    return *lines, *line_labels, winner_text  # UPDATED

ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES, init_func=init, blit=False)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge
video_clip = VideoFileClip("temp_silent.mp4")
final_video = video_clip.with_audio(AudioFileClip(audio_path).subclipped(0, video_clip.duration))
final_video.write_videofile(output_name, codec="libx264", threads=8, fps=FPS)

video_clip.close()
if os.path.exists("temp_silent.mp4"):
    os.remove("temp_silent.mp4")
