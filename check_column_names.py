"""Check all column names and patterns in the parquet file."""

import pandas as pd
import re

# Load the parquet file
vcc_file = r"F:\OneDrive - Aimsun SLU\2218 - AD Mobility- Provision of Hybrid Model Enhancements\Task 3 - Model Maintenance and Automation\02_Data\02_InputData\vcc_data.parquet"
df = pd.read_parquet(vcc_file)

print("="*80)
print("ALL COLUMN NAMES IN PARQUET FILE")
print("="*80)

# Group columns by type
metadata_cols = []
flow_cols = []
cls_cols = []
other_cols = []

for col in sorted(df.columns):
    if col in ['Sensor_ID', 'Bound', 'Db_Date', 'start_time', 'end_time']:
        metadata_cols.append(col)
    elif col.startswith('cls_'):
        cls_cols.append(col)
    elif col.startswith('Lane') or col in ['Direction', 'Total']:
        flow_cols.append(col)
    elif col.startswith('occ_') or col.startswith('hdw_') or col.startswith('spd_'):
        other_cols.append(col)
    elif col.startswith('total_'):
        cls_cols.append(col)
    else:
        other_cols.append(col)

print(f"\nMetadata columns ({len(metadata_cols)}):")
for col in metadata_cols:
    print(f"  {col}")

print(f"\nFlow columns ({len(flow_cols)}):")
for col in flow_cols:
    print(f"  {col}")

print(f"\nClassification columns ({len(cls_cols)}):")
for col in cls_cols:
    print(f"  {col}")

# Analyze the pattern of cls columns
print(f"\n" + "="*80)
print("ANALYZING CLASSIFICATION COLUMN PATTERNS")
print("="*80)

# Extract unique suffixes from cls columns
suffixes = set()
for col in cls_cols:
    if col.startswith('cls_Lane'):
        # Extract the part after lane number
        match = re.search(r'cls_Lane\d+(?:_Fast)?_(.*)', col)
        if match:
            suffixes.add(match.group(1))
    elif col.startswith('cls_Direction_'):
        suffix = col.replace('cls_Direction_', '')
        suffixes.add(suffix)
    elif col.startswith('total_cls_'):
        suffix = col.replace('total_cls_', '')
        suffixes.add(suffix)

print(f"\nUnique class suffixes found: {sorted(suffixes)}")

# Check if there are any columns with dots instead of underscores
print(f"\n" + "="*80)
print("CHECKING FOR ALTERNATE NAMING PATTERNS")
print("="*80)

# Check for columns with dots
dot_cols = [col for col in df.columns if '.' in col]
if dot_cols:
    print(f"\nColumns with dots ({len(dot_cols)}):")
    for col in dot_cols:
        print(f"  {col}")
else:
    print(f"\nNo columns with dots found")

# Check for columns with different number formats
print(f"\n" + "="*80)
print("CHECKING LENGTH CLASS NAMING VARIATIONS")
print("="*80)

# Look for all possible representations of 0-3.5 range
variations_0_3_5 = [col for col in df.columns if any(x in col.lower() for x in ['0_3_5', '0-3.5', '0.3.5', '035', '0_35'])]
print(f"\nPossible 0-3.5m columns ({len(variations_0_3_5)}):")
for col in sorted(variations_0_3_5):
    print(f"  {col}")

# Check the actual data type and sample values
print(f"\n" + "="*80)
print("SAMPLE DATA FROM CLASSIFICATION COLUMNS")
print("="*80)

sensor_id = "SHZ_1_L71_IB"
df_sensor = df[df['Sensor_ID'] == sensor_id]

if len(df_sensor) > 0:
    sample_row = df_sensor.iloc[0]

    print(f"\nSample row from {sensor_id}:")
    print(f"Date: {sample_row['Db_Date']}, Time: {sample_row['start_time']}")

    # Show Lane 3 classification (the one with high 0_3_5 percentage)
    print(f"\nLane 3 classification columns:")
    lane3_cls_cols = sorted([col for col in df_sensor.columns if col.startswith('cls_Lane3')])
    for col in lane3_cls_cols:
        val = sample_row[col]
        print(f"  {col:40} = {val:>6} (type: {type(val).__name__})")

    # Check if column names might be swapped or mislabeled
    print(f"\n" + "="*80)
    print("CHECKING FOR POTENTIAL COLUMN MISLABELING")
    print("="*80)

    # Compare multiple rows to see if pattern is consistent
    print(f"\nComparing first 5 rows for Lane 3:")
    print(f"{'Row':<5} {'0_3_5':>8} {'3_5_6':>8} {'6_8':>8} {'8_10':>8} {'10_12':>8} {'12_Inf':>8} {'Total':>8}")
    print("-"*70)

    for idx, row in df_sensor.head(5).iterrows():
        v_0_3_5 = pd.to_numeric(row['cls_Lane3_0_3_5'], errors='coerce')
        v_3_5_6 = pd.to_numeric(row['cls_Lane3_3_5_6'], errors='coerce')
        v_6_8 = pd.to_numeric(row['cls_Lane3_6_8'], errors='coerce')
        v_8_10 = pd.to_numeric(row['cls_Lane3_8_10'], errors='coerce')
        v_10_12 = pd.to_numeric(row['cls_Lane3_10_12'], errors='coerce')
        v_12_inf = pd.to_numeric(row['cls_Lane3_12_Infinity'], errors='coerce')
        lane3_flow = pd.to_numeric(row['Lane3'], errors='coerce')

        total_cls = v_0_3_5 + v_3_5_6 + v_6_8 + v_8_10 + v_10_12 + v_12_inf

        print(f"{idx:<5} {v_0_3_5:>8.0f} {v_3_5_6:>8.0f} {v_6_8:>8.0f} {v_8_10:>8.0f} {v_10_12:>8.0f} {v_12_inf:>8.0f} {total_cls:>8.0f}")

    print(f"\nObservation: If 0_3_5 is consistently very high compared to 3_5_6,")
    print(f"this suggests either:")
    print(f"1. The data is correct (unusual traffic pattern)")
    print(f"2. Column labels are swapped (0_3_5 actually contains different data)")
    print(f"3. Sensor is miscalibrated (classifying 3.5-6m vehicles as 0-3.5m)")
