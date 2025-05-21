import os
import json

class FilenameParser:
    def __init__(self, folder='imported-data'):
        self.folder = folder
        # Create folder if it doesn't exist
        if not os.path.exists(self.folder):
            print(f"Folder '{self.folder}' does not exist. Creating it now...")
            os.makedirs(self.folder)

    def parse_filename(self, filename):
        base = filename[:-4] if filename.endswith('.csv') else filename
        parts = base.split('_')

        if len(parts) < 10:
            raise ValueError(f"Název souboru '{filename}' nemá očekávaný formát (má {len(parts)} částí).")

        return {
            "file_name": filename,
            "particle_type": parts[0],
            "instrument": parts[1],
            "model": parts[2],
            "thing_1": parts[3],
            "thing_2": parts[4],
            "thing_3": parts[5],
            "material": parts[7],
            "spectrum": parts[9]
        }

    def process_all_files(self):
        print(f"Looking for CSV files in folder: '{self.folder}'")
        all_parsed = []

        for filename in os.listdir(self.folder):
            if filename.endswith('.csv'):
                print(f"Processing file: {filename}")
                try:
                    parsed = self.parse_filename(filename)
                    all_parsed.append(parsed)
                except Exception as e:
                    print(f"Error processing '{filename}': {e}")

        if all_parsed:
            output_path = os.path.join('generated-data', 'properties.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_parsed, f, indent=4, ensure_ascii=False)
            print(f"\nCreated combined JSON file with {len(all_parsed)} entries: {output_path}")
        else:
            print("No valid CSV files processed, no JSON file created.")

def main():
    parser = FilenameParser()
    parser.process_all_files()

if __name__ == "__main__":
    main()
    
