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
tickers = ['SP500', 'NASDAQ'] # Exclusively SP500 and NASDAQ
FPS = 60 
DURATION_SECONDS = 15  
TOTAL_FRAMES = FPS * DURATION_SECONDS
INITIAL_INVESTMENT = 10000
START_YEAR, END_YEAR = 2000, 2024
output_name = "output.mp4"

COLORS = ['#00ffcc', '#ff0077'] # Neon Cyan and Neon Pink
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

lines = [ax.plot([], [], label=t, color=COLORS[i % len(COLORS)], lw=5)[0] for i, t in enumerate(tickers)]
ax.legend(loc='upper center', fontsize=22, frameon=False, ncol=1, borderpad=2)

# Sparse X-Axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(5)) 
plt.xticks(fontsize=18, color='#888888')

def currency(x, pos=None):
    if x >= 1e6: return f'${x*1e-6:.1f}M'
    return f'${x*1e-3:.0f}K' if x >= 1e3 else f'${x:.0f}'

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency))
ax.tick_params(axis='y', labelsize=18, colors='#888888')
ax.set_title("SP500 VS NASDAQ", fontsize=40, pad=50, fontweight='bold')

winner_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha='center', 
                      fontsize=45, fontweight='bold', color='white', alpha=0)

def init():
    ax.set_xlim(min(dates_interp), max(dates_interp))
    ax.set_ylim(value_data.min().min() * 0.9, value_data.max().max() * 1.1)
    return *lines, winner_text

# 4. Rendering
pbar = tqdm(total=TOTAL_FRAMES, desc=f"Rendering {tickers[0]} vs {tickers[1]}")
def update(frame):
    pbar.update(1)
    for i, ticker in enumerate(tickers):
        lines[i].set_data(dates_interp[:frame], value_data[ticker][:frame])
    
    if frame == TOTAL_FRAMES - 1:
        final_scores = {t: value_data[t].iloc[-1] for t in tickers}
        win = max(final_scores, key=final_scores.get)
        winner_text.set_text(f"{win} WINS!\n{currency(final_scores[win])}")
        winner_text.set_alpha(1)
    return *lines, winner_text

ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES, init_func=init, blit=True)
ani.save('temp_silent.mp4', writer='ffmpeg', fps=FPS, bitrate=5000)
pbar.close()

# 5. Audio Merge
video_clip = VideoFileClip("temp_silent.mp4")
final_video = video_clip.with_audio(AudioFileClip(audio_path).subclipped(0, video_clip.duration))
final_video.write_videofile(output_name, codec="libx264", threads=8, fps=FPS)

# Cleanup
video_clip.close()
if os.path.exists("temp_silent.mp4"):
    os.remove("temp_silent.mp4")

print(f"\nBattle complete! Saved as {output_name}")
