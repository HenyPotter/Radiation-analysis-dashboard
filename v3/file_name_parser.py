import os
import json

class FilenameParser:
    def __init__(self, folder='imported-data'):
        self.folder = folder

    def parse_filename(self, filename):
        base = filename[:-4] if filename.endswith('.csv') else filename
        parts = base.split('_')

        if len(parts) < 10:
            raise ValueError(f"Název souboru '{filename}' nemá očekávaný formát (má {len(parts)} částí).")

        particle_type = parts[0]
        instrument = parts[1]
        model = parts[2]
        version_1 = parts[3]
        version_2 = parts[4]
        unit = parts[5]
        code = parts[6]
        detector_type = parts[7]
        material = parts[8]
        spectrum = parts[9]

        return {
            "file_name": filename,
            "particle_type": particle_type,
            "instrument": instrument,
            "model": model,
            "version_1": version_1,
            "version_2": version_2,
            "unit": unit,
            "code": code,
            "detector_type": detector_type,
            "material": material,
            "spectrum": spectrum
        }

    def process_all_files(self):
        for filename in os.listdir(self.folder):
            if filename.endswith('.csv'):
                try:
                    parsed = self.parse_filename(filename)
                    json_filename = filename.replace('.csv', '.json')
                    output_path = os.path.join(self.folder, json_filename)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed, f, indent=4)
                    print(f"Zpracováno: {filename} -> {json_filename}")
                except Exception as e:
                    print(f"Chyba u souboru '{filename}': {e}")

def main():
    parser = FilenameParser()
    parser.process_all_files()

if __name__ == "__main__":
    main()
