import re

filename = "solar_proton_TPS_BDS-CISHAB-MDL-0002-ELV214_v007-ELV214_v6-NA1-FP011-FP10telo001-DETECTOR_MATDEF_Silicon_PV_Spectrum1.csv"
pattern = r"v6-(.*?)-DETECTOR"

print("Filename for regex:", filename)
match = re.search(pattern, filename)
if match:
    print("Extracted physical_volume:", match.group(1))
else:
    print("No match found")
