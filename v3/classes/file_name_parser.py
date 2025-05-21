import os
import json
import re

class CsvPropertiesCollector:
    def __init__(self, root_folder='generated-data', output_file='properties.json'):
        self.root_folder = root_folder
        self.output_file = output_file
        self.key_value_pattern = re.compile(r"'([^']+)',\s*-?\d+,\s*'([^']*)'")

    def parse_csv_headers(self, filepath):
        properties = {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    match = self.key_value_pattern.search(line)
                    if match:
                        key, value = match.group(1), match.group(2)
                        properties[key] = value
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        return properties

    def collect_properties(self):
        all_properties = []

        for dirpath, dirnames, filenames in os.walk(self.root_folder):
            for filename in filenames:
                if filename.endswith('.csv'):
                    full_path = os.path.join(dirpath, filename)
                    
                    relative_folder = os.path.relpath(dirpath, self.root_folder)
                    if relative_folder == '.':
                        relative_folder = ''

                    file_name_without_ext = filename[:-4]

                    csv_props = self.parse_csv_headers(full_path)

                    # Ukládat jen pokud v csv_props je HIST_TITLE
                    if "HIST_TITLE" in csv_props:
                        properties = {
                            "folder": relative_folder,
                            "file_name": file_name_without_ext,
                            "plot_title": "output_plots/" + relative_folder + "_" + file_name_without_ext + ".png",
                        }
                        properties.update(csv_props)
                        all_properties.append(properties)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(all_properties, f, indent=4, ensure_ascii=False)

        print(f"Collected properties for {len(all_properties)} CSV files with 'HIST_TITLE'.")
        print(f"Saved to '{self.output_file}'")
