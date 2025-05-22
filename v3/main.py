import os
import time
from tqdm import tqdm

from classes.gras_splitter import GrasBlockSplitter
from classes.histogram_plotter import HistogramPlotter, scan_files
from classes.file_name_parser import CsvPropertiesCollector


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    # 1) Split GRAS CSVs into blocks
    print("🔧 Splitting GRAS CSV files...")
        # initialize GRAS block splitter (uses default configuration)
    splitter = GrasBlockSplitter()
    splitter.run()
    time.sleep(0.5)
    clear_screen()

    # 2) Scan for HIST_1D CSV files
    print("🔍 Scanning for matching CSV files...")
    files = scan_files(root='generated-data')
    if not files:
        print("❌ No matching files found with 'GRAS_DATA_TYPE',   -1,'HIST_1D'.")
        return
    print(f"✅ Found {len(files)} matching file(s).")
    time.sleep(0.5)
    clear_screen()

    # 3) Generate histograms
    print("📊 Generating and saving histogram plots...")
    plotter = HistogramPlotter(
        files,
        root_dir='generated-data',
        output_root='output_plots'
    )
    plotter.plot_all()
    time.sleep(0.5)
    clear_screen()

    # 4) Collect CSV header properties
    print("📝 Extracting CSV header properties and saving to JSON...")
    collector = CsvPropertiesCollector(
        root_folder='generated-data',
        output_file='properties.json'
    )
    collector.collect_properties()
    time.sleep(0.5)
    clear_screen()

    print("✅ All tasks completed successfully.")


if __name__ == '__main__':
    main()
