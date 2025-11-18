"""Debug script to test PCU column detection logic."""

import pandas as pd
import re

# Load the parquet file
vcc_file = r"F:\OneDrive - Aimsun SLU\2218 - AD Mobility- Provision of Hybrid Model Enhancements\Task 3 - Model Maintenance and Automation\02_Data\02_InputData\vcc_data.parquet"
df = pd.read_parquet(vcc_file)

# Filter for a specific sensor (one mentioned in the config)
sensor_id = "SHZ_1_L71_IB"
df_sensor = df[df['Sensor_ID'] == sensor_id].copy()

print(f"Sensor: {sensor_id}")
print(f"Total rows: {len(df_sensor)}")
print("\n" + "="*80)

# Get all cls_ columns for this sensor
cls_cols = [c for c in df_sensor.columns if c.startswith('cls_Lane')]
print(f"\nAll cls_Lane columns ({len(cls_cols)}):")
for col in sorted(cls_cols):
    print(f"  {col}")

# Extract unique lane numbers using regex
lane_cols = [col for col in df_sensor.columns if col.startswith('cls_Lane')]
lane_numbers = sorted(set([
    int(re.search(r'cls_Lane(\d+)', col).group(1))
    for col in lane_cols
    if re.search(r'cls_Lane(\d+)', col)
]))

print(f"\n" + "="*80)
print(f"Detected lane numbers: {lane_numbers}")

# PCU values from config
pcu_values = {
    "0_3_5": 0.5,
    "3_5_6": 1.0,
    "6_8": 1.5,
    "8_10": 2.0,
    "10_12": 2.5,
    "12_Infinity": 3.0
}

print(f"\n" + "="*80)
print("Testing column detection for each lane:")
print("="*80)

# Test current logic for each lane
for lane in lane_numbers:
    print(f"\nLane {lane}:")
    class_cols = {}

    for class_name in pcu_values.keys():
        # Current logic from pcu_converter.py
        col_fast = f'cls_Lane{lane}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane}_{class_name}'

        if col_fast in df_sensor.columns:
            class_cols[class_name] = col_fast
            print(f"  [OK] {class_name:12} -> {col_fast} (FOUND via _Fast)")
        elif col_regular in df_sensor.columns:
            class_cols[class_name] = col_regular
            print(f"  [OK] {class_name:12} -> {col_regular} (FOUND via regular)")
        else:
            print(f"  [XX] {class_name:12} -> NOT FOUND (tried {col_fast} and {col_regular})")

    print(f"  Total found: {len(class_cols)}/{len(pcu_values)}")

# Now test with actual data - get a sample row
print(f"\n" + "="*80)
print("Sample data values for first row:")
print("="*80)

sample_row = df_sensor.iloc[0]
for lane in lane_numbers:
    print(f"\nLane {lane}:")
    for class_name in pcu_values.keys():
        col_fast = f'cls_Lane{lane}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane}_{class_name}'

        if col_fast in df_sensor.columns:
            val = sample_row[col_fast]
            print(f"  {class_name:12} = {val:>6} (from {col_fast})")
        elif col_regular in df_sensor.columns:
            val = sample_row[col_regular]
            print(f"  {class_name:12} = {val:>6} (from {col_regular})")

# Test if there's double counting happening
print(f"\n" + "="*80)
print("Checking for double-counting issue:")
print("="*80)

for lane in lane_numbers:
    print(f"\nLane {lane}:")

    # Check if both versions of the column exist
    for class_name in pcu_values.keys():
        col_fast = f'cls_Lane{lane}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane}_{class_name}'

        has_fast = col_fast in df_sensor.columns
        has_regular = col_regular in df_sensor.columns

        if has_fast and has_regular:
            print(f"  [WARNING] {class_name:12} - BOTH columns exist!")
            print(f"      {col_fast}: {sample_row[col_fast]}")
            print(f"      {col_regular}: {sample_row[col_regular]}")
        elif has_fast:
            print(f"  [OK] {class_name:12} - Only _Fast version exists")
        elif has_regular:
            print(f"  [OK] {class_name:12} - Only regular version exists")
        else:
            print(f"  [XX] {class_name:12} - Neither version exists")
