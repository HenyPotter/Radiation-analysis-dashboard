import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def scan_files(root='generated-data'):
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

    with open(csv_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith("'"):
                break
            line_content = line.lstrip("'").strip()
            if line_content.startswith('X_AXIS_SCALE'):
                metadata['x_axis_scale'] = line_content.split(',')[2].strip().strip("'\"")
            elif line_content.startswith('X_AXIS_UNITS'):
                metadata['x_axis_units'] = line_content.split(',')[2].strip().strip("'\"")
            elif line_content.startswith('Y_AXIS_UNITS'):
                metadata['y_axis_units'] = line_content.split(',')[2].strip().strip("'\"")
            elif line_content.startswith('X_AXIS_LABEL'):
                metadata['x_axis_label'] = line_content.split(',')[2].strip().strip("'\"")
            elif line_content.startswith('Y_AXIS_LABEL'):
                metadata['y_axis_label'] = line_content.split(',')[2].strip().strip("'\"")
            elif line_content.startswith('HIST_TITLE'):
                metadata['title'] = line_content.split(',')[2].strip().strip("'\"")

    xlabel = metadata.get('x_axis_label', 'Not found')
    ylabel = metadata.get('y_axis_label', 'Not found')
    title = metadata.get('title', 'Not found')
    xunits = metadata.get('x_axis_units', '')
    yunits = metadata.get('y_axis_units', '')
    xscale = metadata.get('x_axis_scale', 'linear')

    if xunits:
        xlabel += f" [{xunits}]"
    if yunits:
        ylabel += f" [{yunits}]"

    column_names = ['lower', 'upper', 'mean', 'value', 'error', 'entries']
    df = pd.read_csv(csv_file, comment="'", header=None, names=column_names).astype(float)

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
        'folder_name': os.path.basename(os.path.dirname(csv_file))
    }

class HistogramPlotter:
    def __init__(self, files, per_page=3):
        self.files = files
        self.per_page = per_page
        self.page = 0
        self.num_pages = (len(files) + per_page - 1) // per_page
        self.fig = None
        self.axes = None

    def plot_page(self):
        start = self.page * self.per_page
        end = min(start + self.per_page, len(self.files))
        batch = self.files[start:end]

        if self.fig:
            plt.close(self.fig)

        rows = self.per_page
        self.fig, self.axes = plt.subplots(rows, 1, figsize=(12, 5 * rows))
        if rows == 1:
            self.axes = [self.axes]

        for ax in self.axes:
            ax.clear()

        for i, file in enumerate(batch):
            data = extract_data(file)
            ax = self.axes[i]

            ax.bar(data['bin_lower'], data['dose'],
                   width=(data['bin_upper'] - data['bin_lower']),
                   align='edge',
                   edgecolor='black',
                   alpha=0.6,
                   color='steelblue',
                   label='Dose per bin')

            if np.any(data['dose_error'] > 0):
                ax.errorbar(data['bin_center'], data['dose'],
                            yerr=data['dose_error'],
                            fmt='o',
                            color='darkred',
                            ecolor='firebrick',
                            elinewidth=2,
                            capsize=5,
                            capthick=2,
                            markersize=6,
                            label='Error')

            ax.set_xscale(data['xscale'])
            ax.set_xlabel(data['xlabel'])
            ax.set_ylabel(data['ylabel'])
            ax.set_title(
                f"{data['title']}\n{data['folder_name'].replace('_', ' ').capitalize()} - ({data['file_name']})"
            )

            ax.set_xlim(data['bin_lower'].min(), data['bin_upper'].max())
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            ax.legend()

        for i in range(len(batch), self.per_page):
            self.axes[i].set_visible(False)

        self.fig.suptitle(f"Page {self.page + 1} / {self.num_pages}", fontsize=16)
        self.fig.tight_layout(rect=[0, 0, 1, 0.96])

        try:
            mng = plt.get_current_fig_manager()
            mng.window.state('zoomed')
        except Exception:
            mng.full_screen_toggle()

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        plt.show()

    def on_key(self, event):
        if event.key == 'right' or event.key == ' ':
            if self.page < self.num_pages - 1:
                self.page += 1
                self.plot_page()
        elif event.key == 'left':
            if self.page > 0:
                self.page -= 1
                self.plot_page()
        elif event.key == 'escape':
            plt.close(self.fig)
