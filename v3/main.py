import re
import glob

data_file = "solar_proton_TPS_BDS-CISHAB-MDL-0002-ELV214_v007-ELV214_v6-NA1-FP011-FP10telo001-DETECTOR_MATDEF_Silicon_PV_Spectrum1.csv"
with open(data_file) as f:
    blocks = f.read().split("'End of Block'")

for i, block in enumerate(blocks):
    block = block.strip()
    if not block:
        continue


    title_match = re.search(r"'GRAS_DATA_TITLE'\s*,\s*-1\s*,\s*'([^']+)'", block)
    if title_match:
        title = title_match.group(1).replace(" ", "_").replace("/", "_")
    else:
        title = f"block_{i+1}"

    with open(f"data/{title}.csv", "w") as out:
        os.remove(f"data.csv")
        out.write(block)