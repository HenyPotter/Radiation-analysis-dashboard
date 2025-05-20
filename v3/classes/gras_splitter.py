# gras_splitter.py

import os
import re
import glob
import shutil

class GrasBlockSplitter:
    def __init__(self, input_dir="imported-data", output_dir="generated-data"):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def list_csv_files(self):
        return sorted(glob.glob(f"{self.input_dir}/*.csv"))

    def show_menu(self, files):
        print("Found the following CSV files:\n")
        for idx, file in enumerate(files, start=1):
            print(f"  {idx}) {os.path.basename(file)}")
        print("\033[1m\nEnter the numbers of the files to process (e.g. 1,2,4) or 'a' for all:\033[0m")
        return input("Your choice: ").strip()

    def get_selected_files(self, files, choice):
        if choice.lower() == 'a':
            return files
        indices = []
        for i in choice.split(","):
            try:
                index = int(i.strip()) - 1
                if 0 <= index < len(files):
                    indices.append(index)
            except ValueError:
                continue
        return [files[i] for i in indices]

    def process_file(self, file_path):
        filename = os.path.basename(file_path)
        parts = filename.split("_")
        base_folder_name = "_".join(parts[:2]) if len(parts) >= 2 else "output"
        output_dir = os.path.join(self.output_dir, base_folder_name)
        os.makedirs(output_dir, exist_ok=True)

        print(f"\nProcessing '{filename}' → '{output_dir}'")

        with open(file_path, "r", encoding="utf-8") as f:
            blocks = f.read().split("'End of Block'")

        for i, block in enumerate(blocks, start=1):
            block = block.strip()
            if not block or block == "'End of File'":
                continue

            title_match = re.search(r"'GRAS_DATA_TITLE'\s*,\s*-1\s*,\s*'([^']+)'", block)
            if title_match:
                title = title_match.group(1).replace(" ", "_").replace("/", "_")
            else:
                title = f"block_{i}"

            output_path = os.path.join(output_dir, f"{title.lower()}.csv")
            with open(output_path, "w", encoding="utf-8") as out:
                out.write(block)

        print(f"Done: {len(blocks)} blocks processed.")

    def run(self):
        self.clear_screen()
        print("GRAS Block Splitter")
        print("========================\n")

        csv_files = self.list_csv_files()
        if not csv_files:
            print(f"No CSV files found in '{self.input_dir}' directory.")
            return

        user_choice = self.show_menu(csv_files)
        selected_files = self.get_selected_files(csv_files, user_choice)

        if not selected_files:
            print("No valid files selected. Exiting.")
            return

        shutil.rmtree(self.output_dir, ignore_errors=True)
        os.makedirs(self.output_dir, exist_ok=True)

        for file_path in selected_files:
            self.process_file(file_path)

        print("\nAll selected files processed successfully.")
