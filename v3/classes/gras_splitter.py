import os
import re
import glob
import shutil
import json

class GrasBlockSplitter:
    def __init__(self, input_dir="imported-data", output_dir="generated-data"):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def list_csv_files(self):
        return sorted(glob.glob(f"{self.input_dir}/*.csv"))

    def show_menu(self, files):
        print("\033[1;36mFound the following CSV files:\033[0m\n")
        for idx, file in enumerate(files, start=1):
            print(f"  \033[93m{idx:2})\033[0m {os.path.basename(file)}")
        print("\n\033[1;32mEnter the numbers of the files to process (e.g. 1,2,4) or 'a' for all:\033[0m")
        return input("➤ Your choice: ").strip()

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

        print(f"\n\033[1;34m▶ Processing:\033[0m {filename}")
        print(f"   \033[1;33m→ Output Directory:\033[0m {output_dir}")

        with open(file_path, "r", encoding="utf-8") as f:
            blocks = f.read().split("'End of Block'")

        saved = 0
        for i, block in enumerate(blocks, start=1):
            block = block.strip()
            if not block or block == "'End of File'":
                continue

            title_match = re.search(r"'GRAS_DATA_TITLE'\s*,\s*-1\s*,\s*'([^']+)'", block)
            title = title_match.group(1).replace(" ", "_").replace("/", "_") if title_match else f"block_{i}"
            output_path = os.path.join(output_dir, f"{title.lower()}.csv")

            with open(output_path, "w", encoding="utf-8") as out:
                out.write(block)
            saved += 1

        print(f"   \033[1;32m✓ {saved} blocks saved.\033[0m")

    def generate_file_map(self, selected_files):
        file_map = {}

        for file_path in selected_files:
            filename = os.path.basename(file_path)
            parts = filename.split("_")
            base_folder_name = "_".join(parts[:2]) if len(parts) >= 2 else "output"
            output_dir = os.path.join(self.output_dir, base_folder_name)

            new_files = sorted([
                os.path.join(base_folder_name, f)
                for f in os.listdir(output_dir)
                if f.endswith(".csv")
            ])

            file_map[filename] = new_files

        with open("file_map.json", "w", encoding="utf-8") as f:
            json.dump(file_map, f, indent=4)

        print("\n\033[1;36m✔ File map saved to 'file_map.json'.\033[0m\n")

    def run(self):
        self.clear_screen()
        print("\033[1;35mGRAS Block Splitter\033[0m")

        csv_files = self.list_csv_files()
        if not csv_files:
            print(f"\033[1;31mNo CSV files found in '{self.input_dir}' directory.\033[0m")
            return

        user_choice = self.show_menu(csv_files)
        selected_files = self.get_selected_files(csv_files, user_choice)

        if not selected_files:
            print("\n\033[1;31m No valid files selected. Exiting.\033[0m")
            return

        shutil.rmtree(self.output_dir, ignore_errors=True)
        os.makedirs(self.output_dir, exist_ok=True)

        print("\n\033[1;36mProcessing selected files...\033[0m")
        for file_path in selected_files:
            self.process_file(file_path)

        self.generate_file_map(selected_files)

        print("\n\033[1;32m✔ All selected files processed successfully.\033[0m\n")
