from classes.gras_splitter import GrasBlockSplitter
from classes.histogram_plotter import HistogramPlotter, scan_files
from classes.file_name_parser import CsvPropertiesCollector
from tqdm import tqdm
import os
import json
import re

def main():
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
        
    print("🔧 Splitting GRAS CSV files...")
    splitter = GrasBlockSplitter()
    splitter.run()
    clear_screen()
    print("\n🔍 Scanning for matching CSV files...")
    
    files = scan_files()
    if not files:
        print("❌ No matching files found with 'GRAS_DATA_TYPE',   -1,'HIST_1D'.")
        return
    print(f"✅ Found {len(files)} matching file(s).")
    clear_screen()
    
    print("\n📊 Generating and saving histogram plots...")
    plotter = HistogramPlotter(files, output_dir='output_plots')
    for _ in tqdm([None], desc="Processing files"):
        plotter.plot_all()
        
    clear_screen()
    print("\n📝 Extracting CSV header properties and saving to JSON...")
    collector = CsvPropertiesCollector(root_folder='generated-data', output_file='properties.json')
    collector.collect_properties()

    clear_screen()
    print("\n✅ All tasks completed successfully.")

if __name__ == "__main__":
    main()
