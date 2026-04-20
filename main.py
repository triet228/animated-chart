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
tickers = ['$500'] 
FPS = 60 
DURATION_SECONDS = 15  
PAUSE_SECONDS = 0  # ADDED: 3 second pause
TOTAL_FRAMES = FPS * DURATION_SECONDS
PAUSE_FRAMES = FPS * PAUSE_SECONDS
INITIAL_INVESTMENT = 1
START_YEAR, END_YEAR = 0, 2025
output_name = "output.mp4"

COLORS = ['#00ffcc', '#ff0077', '#ffcc00'] 
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

start_row = pd.DataFrame([[INITIAL_INVESTMENT]*len(tickers)], columns=tickers)
raw_values = pd.concat([start_row, data[tickers]], ignore_index=True)

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

# MOVED: Investing Years Counter to Middle Top
years_text = ax.text(0.5, 0.92, '', transform=ax.transAxes, ha='center', 
                     fontsize=40, fontweight='bold', color='#ffffff', alpha=0.8)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(fontsize=18, color='#888888')

def currency(x, pos=None):
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    return f'${x*1e-3:.0f}K' if x >= 1e3 else f'${x:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency))
ax.tick_params(axis='both', labelsize=18, colors='#888888')
ax.set_title("INVEST $500 A MONTH", fontsize=40, pad=60, fontweight='bold')

ax.axhline(y=1000000, color='white', linestyle='--', alpha=0.3, lw=3)
ax.text(dates_interp[0], 1000000 + 20000, "$1M", color='white', 
        fontsize=20, fontweight='bold', alpha=0.5, va='bottom')

winner_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha='center', 
                      fontsize=45, fontweight='bold', color='white', alpha=0)

def init():
    ax.set_xlim(dates_interp[0], dates_interp[1])
    ax.set_ylim(INITIAL_INVESTMENT * 0.9, INITIAL_INVESTMENT * 1.1)
    years_text.set_text('')
    return *lines, *line_labels, winner_text, years_text  

# 4. Rendering
winning_frames = value_data[(value_data[tickers] >= 1000000).any(axis=1)].index
winning_frame = winning_frames[0] if len(winning_frames) > 0 else TOTAL_FRAMES - 1

# Updated total for tqdm to include pause
pbar = tqdm(total=TOTAL_FRAMES + PAUSE_FRAMES, desc="Rendering")

def update(frame):
    pbar.update(1)
    # Freeze the data at winning_frame, but the animation continues to run
    current_idx = min(max(1, frame), winning_frame)
    current_slice = value_data.iloc[:current_idx+1]
    
    current_date = mdates.num2date(dates_interp[current_idx])
    elapsed_years = current_date.year - data['Date'].iloc[0].year
    years_text.set_text(f"YEAR {max(0, elapsed_years)}")
    
    current_max = current_slice.max().max()
    label_offset = current_max * 0.02
    
    for i, ticker in enumerate(tickers):
        lines[i].set_data(dates_interp[:current_idx+1], current_slice[ticker])
        current_x = dates_interp[current_idx]
        current_y = current_slice[ticker].iloc[-1]
        line_labels[i].set_position((current_x, current_y + label_offset))
    
    ax.set_xlim(dates_interp[0], dates_interp[current_idx] + 200)
    current_min = current_slice.min().min()
    ax.set_ylim(current_min * 0.95, current_max * 1.15)

    if current_idx == winning_frame:
        winner_text.set_text(f"{elapsed_years} YEARS\nTO REACH $1M!")
        winner_text.set_alpha(1)
        
    return *lines, *line_labels, winner_text, years_text  

# Added PAUSE_FRAMES to the animation length
ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES + PAUSE_FRAMES, init_func=init, blit=False)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge
if os.path.exists(audio_path):
    video_clip = VideoFileClip("temp_silent.mp4")
    # Subclipped to duration ensures the music fits the new longer video
    final_video = video_clip.with_audio(AudioFileClip(audio_path).subclipped(0, video_clip.duration))
    final_video.write_videofile(output_name, codec="libx264", threads=8, fps=FPS)
    video_clip.close()
    os.remove("temp_silent.mp4")
else:
    os.rename("temp_silent.mp4", output_name)
