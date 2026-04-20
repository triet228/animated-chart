# Animated Stock Chart Generator

A Python project that creates an animated video chart racing stock data, complete with background music. 

## Project Structure

* `main.py`: The main script. Run this to generate the final `output.mp4` video.
* `generate_data.py`: A helper script used to generate the stock data.
* `data.csv`: Contains the generated stock data used for the animation.
* `songs/`: A directory containing free, public-domain background songs. `main.py` picks one randomly for the video.
* `LICENSE`: Contains the copyleft license for this project.

## Requirements

Ensure you have the necessary Python libraries installed before running the scripts:

```bash
pip install pandas numpy matplotlib moviepy tqdm
```

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/triet228/animated-chart.git
cd animated-chart
```

## Usage

1. **Generate the stock data** (if you haven't already):
   ```bash
   python generate_data.py
   ```

2. **Render the animated video**:
   ```bash
   python main.py
   ```

The script will render the frames, merge the audio, and output a finished video named `output.mp4` in your current directory.

## Other Branches

Different branches in this repository feature unique variations of the animated chart. You can switch between branches to generate different styles of racing videos.

| Branch Name | Description |
| :--- | :--- |
| `main` | The default animated chart racing up to the end of the provided data. |
| `millionaire` | Races the stocks until one reaches $1M. |
| `leverage` | Races the stocks until one reaches $0. |
| `retirement` | Retirement focus animated chart. |


## License

This project is open-source and distributed under a Copyleft License. See the `LICENSE` file for more details.
