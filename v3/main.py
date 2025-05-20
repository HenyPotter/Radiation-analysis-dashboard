import os
import re
import glob

output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

for filepath in glob.glob(os.path.join(output_dir, "*.csv")):
    os.remove(filepath)

data_file = "solar_proton_TPS_BDS-CISHAB-MDL-0002-ELV214_v007-ELV214_v6-NA1-FP011-FP10telo001-DETECTOR_MATDEF_Silicon_PV_Spectrum1.csv"
with open(data_file) as f:
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

    with open(os.path.join(output_dir, f"{title}.csv"), "w") as out:
        out.write(block)
