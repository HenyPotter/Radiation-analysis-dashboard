from classes.gras_splitter import GrasBlockSplitter
from classes.histogram_plotter import HistogramPlotter, scan_files  # Přidán import scan_files
from classes.file_name_parser import FilenameParser
import os
import json

def main():
    # Spusť část pro rozdělení CSV souborů
    splitter = GrasBlockSplitter()
    splitter.run()

    # Poté načti histogramové soubory a vykresli je
    print("\nScanning for matching CSV files...")
    files = scan_files()
    if not files:
        print("No matching files found with 'GRAS_DATA_TYPE',   -1,'HIST_1D'.")
        return

    pager = HistogramPlotter(files, per_page=2)
    pager.plot_page()

    # Nakonec spusť parser názvů CSV souborů a ulož vše do jednoho JSON
    print("\nParsing filenames and creating single JSON file...")
    parser = FilenameParser()
    parser.process_all_files()

if __name__ == "__main__":
    main()
    