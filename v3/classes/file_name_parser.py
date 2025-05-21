import os
import json
import re
import sys

class CsvPropertiesCollector:
    def __init__(self,
                 root_folder='generated-data',
                 file_map_path='file_map.json',
                 output_file='properties.json'):
        self.root_folder = root_folder
        self.file_map_path = file_map_path
        self.output_file = output_file

        # regex for CSV‐header key/value
        self.key_value_pattern = re.compile(r"'([^']+)',\s*-?\d+,\s*'([^']*)'")
        # regex to pull out physical_volume from the *container* filename:
        self.physical_volume_pattern = re.compile(r'v6-(.*?)-DETECTOR', re.IGNORECASE)

    def parse_csv_headers(self, filepath):
        props = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    m = self.key_value_pattern.search(line)
                    if m:
                        k, v = m.group(1), m.group(2)
                        props[k] = v
        except Exception as e:
            print(f"ERROR reading {filepath}: {e}")
        return props

    def collect_properties(self):
        # load the big map
        with open(self.file_map_path, 'r', encoding='utf-8') as fm:
            file_map = json.load(fm)

        all_properties = []

        # for each container (the long name with v6-...-DETECTOR)
        for container_name, child_relpaths in file_map.items():
            # 1) extract physical_volume from the container_name
            m = self.physical_volume_pattern.search(container_name)
            physical_volume = m.group(1).strip() if m else None

            # 2) loop over each child CSV path
            for rel_csv in child_relpaths:
                # Print parsing line, stay on same line for update

                full_csv = os.path.join(self.root_folder, rel_csv)

                csv_props = self.parse_csv_headers(full_csv)
                keys = list(csv_props.keys())

                # only keep if HIST_TITLE present
                if "HIST_TITLE" in csv_props:
                    folder = os.path.dirname(rel_csv)
                    fname = os.path.splitext(os.path.basename(rel_csv))[0]
                    plot = f"output_plots/{folder}_{fname}.png" if folder else f"output_plots/{fname}.png"

                    props = {
                        "container_file": container_name,
                        "physical_volume": physical_volume,
                        "folder": folder,
                        "file_name": fname,
                        "plot_title": plot,
                    }
                    props.update(csv_props)
                    all_properties.append(props)


        # dump results
        with open(self.output_file, 'w', encoding='utf-8') as out:
            json.dump(all_properties, out, indent=4, ensure_ascii=False)

        print(f"\nDone — collected {len(all_properties)} CSVs with HIST_TITLE → {self.output_file}")

if __name__ == "__main__":
    collector = CsvPropertiesCollector(
        root_folder='generated-data',
        file_map_path='file_map.json',
        output_file='properties.json'
    )
    collector.collect_properties()
