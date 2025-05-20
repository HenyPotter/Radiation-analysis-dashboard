from gras_splitter import GrasBlockSplitter
from histogram_plotter import HistogramPlotter, scan_files  # Přidán import scan_files

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

if __name__ == "__main__":
    main()
