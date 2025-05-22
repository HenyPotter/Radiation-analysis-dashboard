import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from io import StringIO

ROOT_DIR = 'generated-data'
OUTPUT_ROOT = 'plots'


def scan_files(root=ROOT_DIR):
    matched_files = []
    for subdir, dirs, files in os.walk(root):
        for file in files:
            if file.endswith('.csv'):
                filepath = os.path.join(subdir, file)
                with open(filepath, 'r') as f:
                    for line in f:
                        if "'GRAS_DATA_TYPE',   -1,'HIST_1D'" in line:
                            matched_files.append(filepath)
                            break
    return matched_files


def extract_data(csv_file):
    metadata = {}
    data_lines = []

    with open(csv_file, 'r') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("'"):
                content = stripped.lstrip("'").strip()
                if content.startswith('X_AXIS_SCALE'):
                    metadata['x_axis_scale'] = content.split(',')[2].strip().strip("'\"")
                elif content.startswith('X_AXIS_UNITS'):
                    metadata['x_axis_units'] = content.split(',')[2].strip().strip("'\"")
                elif content.startswith('Y_AXIS_UNITS'):
                    metadata['y_axis_units'] = content.split(',')[2].strip().strip("'\"")
                elif content.startswith('X_AXIS_LABEL'):
                    metadata['x_axis_label'] = content.split(',')[2].strip().strip("'\"")
                elif content.startswith('Y_AXIS_LABEL'):
                    metadata['y_axis_label'] = content.split(',')[2].strip().strip("'\"")
                elif content.startswith('HIST_TITLE'):
                    metadata['title'] = content.split(',')[2].strip().strip("'\"")
            if re.match(r'^\s*[\d\.\+\-]', line):
                data_lines.append(line)

    xlabel = metadata.get('x_axis_label', 'x')
    ylabel = metadata.get('y_axis_label', 'y')
    title = metadata.get('title', '')
    xunits = metadata.get('x_axis_units', '')
    yunits = metadata.get('y_axis_units', '')
    xscale = metadata.get('x_axis_scale', 'linear')

    if xunits:
        xlabel += f" [{xunits}]"
    if yunits:
        ylabel += f" [{yunits}]"

    column_names = ['lower', 'upper', 'mean', 'value', 'error', 'entries']
    data_str = ''.join(data_lines)
    df = pd.read_csv(StringIO(data_str), header=None, names=column_names).astype(float)

    bin_lower = df['lower'].values
    bin_upper = df['upper'].values
    bin_center = (bin_lower + bin_upper) / 2
    dose = df['value'].values
    dose_error = df['error'].values

    return {
        'bin_lower': bin_lower,
        'bin_upper': bin_upper,
        'bin_center': bin_center,
        'dose': dose,
        'dose_error': dose_error,
        'xlabel': xlabel,
        'ylabel': ylabel,
        'title': title,
        'xscale': xscale,
        'file_name': os.path.basename(csv_file),
        'csv_path': csv_file
    }


class HistogramPlotter:
    def __init__(self, files, root_dir=ROOT_DIR, output_root=OUTPUT_ROOT):
        self.files = files
        self.root_dir = root_dir
        self.output_root = output_root

    def plot_all(self):
        for file in tqdm(self.files, desc="Generating plots", unit="file"):
            try:
                data = extract_data(file)
            except Exception as e:
                tqdm.write(f"❌ Failed to process {file}: {e}")
                continue

            # Determine relative subfolder and create matching output folder
            rel_path = os.path.relpath(os.path.dirname(file), self.root_dir)
            output_dir = os.path.join(self.output_root, rel_path)
            os.makedirs(output_dir, exist_ok=True)

            fig, ax = plt.subplots(figsize=(12, 5))

            ax.bar(data['bin_lower'], data['dose'],
                   width=(data['bin_upper'] - data['bin_lower']),
                   align='edge',
                   edgecolor='black',
                   alpha=0.6,
                   label='Dose per bin')

            if np.any(data['dose_error'] > 0):
                ax.errorbar(data['bin_center'], data['dose'],
                            yerr=data['dose_error'],
                            fmt='o',
                            ecolor='firebrick',
                            elinewidth=2,
                            capsize=5,
                            capthick=2,
                            markersize=6,
                            label='Error')

            ax.set_xscale(data['xscale'])
            ax.set_xlabel(data['xlabel'])
            ax.set_ylabel(data['ylabel'])
            ax.set_title(f"{data['title']}\n{rel_path.replace('_', ' ').capitalize()} - ({data['file_name']})")
            ax.set_xlim(data['bin_lower'].min(), data['bin_upper'].max())
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            ax.legend()

            fig.tight_layout()

            # Save with same filename but .png
            file_stem = data['file_name'].replace('.csv', '.png')
            output_path = os.path.join(output_dir, file_stem)
            fig.savefig(output_path, dpi=300)
            plt.close(fig)


if __name__ == '__main__':
    files = scan_files()
    plotter = HistogramPlotter(files)
    plotter.plot_all()