from classes.gras_splitter import GrasBlockSplitter
from classes.histogram_plotter import HistogramPlotter, scan_files
from classes.file_name_parser import FilenameParser
import os

def main():
    # Step 1: Split GRAS CSV files
    print("Splitting GRAS CSV files...")
    splitter = GrasBlockSplitter()
    splitter.run()

    # Step 2: Scan for matching histogram files
    print("\nScanning for matching CSV files...")
    files = scan_files()
    if not files:
        print("No matching files found with 'GRAS_DATA_TYPE',   -1,'HIST_1D'.")
        return
    print(f"Found {len(files)} file(s).")

    # Step 3: Generate and save plots
    print("Generating and saving histogram plots...")
    plotter = HistogramPlotter(files, output_dir='output_plots')
    plotter.plot_all()

    # Step 4: Parse filenames and save metadata to JSON
    print("\nParsing filenames and creating single JSON file...")
    parser = FilenameParser()
    parser.process_all_files()

    print("\nDone.")

if __name__ == "__main__":
    main()
