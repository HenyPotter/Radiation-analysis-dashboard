from classes.gras_splitter import GrasBlockSplitter
from classes.histogram_plotter import HistogramPlotter, scan_files
from classes.file_name_parser import CsvPropertiesCollector
import os
import json
import re

def main():
    print("Splitting GRAS CSV files...")
    splitter = GrasBlockSplitter()
    splitter.run()

    print("\nScanning for matching CSV files...")
    files = scan_files()
    if not files:
        print("No matching files found with 'GRAS_DATA_TYPE',   -1,'HIST_1D'.")
        return
    print(f"Found {len(files)} file(s).")

    print("Generating and saving histogram plots...")
    plotter = HistogramPlotter(files, output_dir='output_plots')
    plotter.plot_all()

    print("\nExtracting CSV header properties and saving to JSON...")
    collector = CsvPropertiesCollector(root_folder='generated-data', output_file='properties.json')
    collector.collect_properties()

    print("\nDone.")

if __name__ == "__main__":
    main()
