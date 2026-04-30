# Animated Stock Chart Generator

A Python project that creates an financial animated chart. 

Youtube playlist: https://www.youtube.com/playlist?list=PLhtWoD9f53K85YdW4S_VDj_1OeaxnEyJb

https://github.com/user-attachments/assets/7ec80d3f-a488-4e7b-b3f3-ccc8a6491e71



https://github.com/user-attachments/assets/6be1235f-ae65-4b2d-a978-847ecd796d43




## Project Structure

* `README.md`: README file
* `LICENSE`: Contains the copyleft license for this project.
* `songs/`: A directory containing free, public-domain background songs. `src/main.py` picks one randomly for the video.
* `src/main.py`: The main script. Run this to generate the final `src/output.mp4` video.
* `src/generate_data.py`: A helper script used to generate the data.
* `src/README.md`: copy of README file

  Temp files:
* `src/data.csv`: Contains the generated stock data used for the animation.
* `src/output.mp4`: Output video after running `src/main.py`.


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

1. **Generate the data** (if you are interested in seeing `src/data.csv`):
   ```bash
   python src/generate_data.py
   ```

2. **Render the animated video**:
   ```bash
   python src/main.py
   ```

The script will render the frames, merge the audio, and output a finished video at `src/output.mp4`.

## Other Branches

Different branches in this repository feature unique variations of the animated chart. You can switch between branches to generate different styles of racing videos.

| Branch Name | Description |
| :--- | :--- |
| `main` | The default branch with on going development. |
| `millionaire` | Races the stocks until one reaches $1M. |
| `leverage` | Races the stocks until one reaches $0. |
| `retirement` | Compare withdraw rate. |
| `contribution` | Invest monthly in stocks. |

Example use of branch
```bash
git checkout retirement
python src/main.py
```

## License

This project is open-source and distributed under a Copyleft License. See the `LICENSE` file for more details.
