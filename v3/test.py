import pandas as pd

df = pd.read_csv('generated-data/solar_proton/total_dose_vs_primary_kinetic_energy.csv', comment="'")
print(df.columns.tolist())
print(df.head())