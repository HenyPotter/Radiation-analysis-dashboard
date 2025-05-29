import os
import json
import re


def add_prefix_to_file_map(file_map_path, prefix='generated-data'):
    """
    Projde file_map.json a ke každé cestě přidá prefix, pokud tam ještě není.
    """
    with open(file_map_path, 'r', encoding='utf-8') as f:
        file_map = json.load(f)

    # Ověříme, jestli už není prefix všude přidán
    all_prefixed = all(
        all(fp.startswith(prefix + '/') for fp in lst)
        for lst in file_map.values()
    )
    if all_prefixed:
        print(f"Prefix '{prefix}/' už je v {file_map_path}, neprovádím změny.")
        return

    updated_map = {}
    for container, file_list in file_map.items():
        new_file_list = []
        for filepath in file_list:
            if not filepath.startswith(prefix + '/'):
                new_fp = os.path.join(prefix, filepath).replace(os.sep, '/')
            else:
                new_fp = filepath
            new_file_list.append(new_fp)
        updated_map[container] = new_file_list

    with open(file_map_path, 'w', encoding='utf-8') as f:
        json.dump(updated_map, f, indent=4, ensure_ascii=False)

    print(f"Updated {file_map_path} with prefix '{prefix}/'")


class CsvPropertiesCollector:
    """
    Načte file_map.json (už s prefixem) a pro každý CSV soubor extrahuje
    vlastnosti z hlavičky. Výsledkem je properties.json.
    """
    def __init__(self,
                 root_folder='generated-data',
                 file_map_path='file_map.json',
                 output_file='properties.json'):
        self.root_folder = root_folder
        self.file_map_path = file_map_path
        self.output_file = output_file

        # pattern pro klíče/hodnoty v hlavičce CSV
        self.key_value_pattern = re.compile(r"'([^']+)',\s*-?\d+,\s*'([^']*)'")
        # pattern pro extrakci názvu physical_volume z container_name
        self.physical_volume_pattern = re.compile(r'v6-(.*?)-DETECTOR', re.IGNORECASE)

    def parse_csv_headers(self, filepath):
        props = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    m = self.key_value_pattern.search(line)
                    if m:
                        key, val = m.group(1), m.group(2)
                        props[key] = val
        except Exception as e:
            print(f"ERROR reading {filepath}: {e}")
        return props

    def collect_properties(self):
        # Načteme už upravený file_map.json
        with open(self.file_map_path, 'r', encoding='utf-8') as fm:
            file_map = json.load(fm)

        all_props = []

        for container_name, relpaths in file_map.items():
            # extrahujeme physical_volume
            m = self.physical_volume_pattern.search(container_name)
            physical_vol = m.group(1).strip() if m else "N/A"

            for rel_csv in relpaths:
                full_csv = rel_csv.replace('/', os.sep)
                csv_props = self.parse_csv_headers(full_csv)

                folder = os.path.dirname(rel_csv).replace('/', '__')
                fname = os.path.splitext(os.path.basename(rel_csv))[0]
                plot_path = (
                    f"output_plots/{folder}/{fname}.png"
                    if folder else
                    f"output_plots/{fname}.png"
                )

                # Zajistíme základní pole a doplníme chybějící hodnoty jako 'N/A'
                entry = {
                    "container_file": container_name,
                    "physical_volume": physical_vol,
                    "folder": folder,
                    "file_name": fname,
                    "file_path": rel_csv,
                    "plot_title": plot_path,
                    "HIST_TITLE": csv_props.get("HIST_TITLE", "N/A"),
                }

                # Přidej další vlastnosti z CSV (bez přepsání těch, co už jsou)
                for key, val in csv_props.items():
                    if key not in entry:
                        entry[key] = val

                all_props.append(entry)

        # uložíme výsledek
        with open(self.output_file, 'w', encoding='utf-8') as out:
            json.dump(all_props, out, indent=4, ensure_ascii=False)

        print(f"\nDone — collected {len(all_props)} CSVs → {self.output_file}")


# Použití (například):
if __name__ == "__main__":
    file_map_path = 'file_map.json'

    # Krok 1: Přidání prefixu
    add_prefix_to_file_map(file_map_path)

    # Krok 2: Sbírání vlastností
    collector = CsvPropertiesCollector(file_map_path=file_map_path)
    collector.collect_properties()
