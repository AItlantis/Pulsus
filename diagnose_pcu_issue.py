"""Diagnose PCU calculation issue - check for double counting."""

import pandas as pd
import numpy as np
import re

# Load the parquet file
vcc_file = r"F:\OneDrive - Aimsun SLU\2218 - AD Mobility- Provision of Hybrid Model Enhancements\Task 3 - Model Maintenance and Automation\02_Data\02_InputData\vcc_data.parquet"
df = pd.read_parquet(vcc_file)

# Filter for a specific sensor
sensor_id = "SHZ_1_L71_IB"
df_sensor = df[df['Sensor_ID'] == sensor_id].copy()

print(f"Sensor: {sensor_id}")
print(f"Total rows: {len(df_sensor)}")
print("\n" + "="*80)
print("DIAGNOSTIC: Check for double-counting or incorrect column selection")
print("="*80)

# Get a sample row
sample_row = df_sensor.iloc[0]

print(f"\nSample row date: {sample_row['Db_Date']}")
print(f"Sample row time: {sample_row['start_time']} to {sample_row['end_time']}")

# Show flow values for lanes
print(f"\n" + "-"*80)
print("FLOW VALUES (vehicles per 15-min interval):")
print("-"*80)
lane_flow_cols = [c for c in df_sensor.columns if c.startswith('Lane') and not c.startswith('cls_')]
for col in sorted(lane_flow_cols)[:10]:
    val = sample_row[col]
    print(f"  {col:20} = {val}")

# Show class distribution for each lane
print(f"\n" + "-"*80)
print("CLASS DISTRIBUTION FOR EACH LANE:")
print("-"*80)

for lane_num in range(1, 9):
    print(f"\nLane {lane_num}:")

    # Find all classification columns for this lane
    cls_cols = [c for c in df_sensor.columns if c.startswith(f'cls_Lane{lane_num}')]

    if len(cls_cols) == 0:
        print(f"  No classification columns found")
        continue

    # Compute total from class distribution
    total_from_classes = 0
    for col in sorted(cls_cols):
        val = sample_row[col]
        if pd.notna(val):
            # Convert to numeric (handle strings)
            val_numeric = pd.to_numeric(val, errors='coerce')
            print(f"  {col:40} = {val:>6} (type: {type(val).__name__})")
            if pd.notna(val_numeric):
                total_from_classes += val_numeric
        else:
            print(f"  {col:40} = {str(val):>6}")

    print(f"  {'TOTAL from class distribution':40} = {total_from_classes:>6}")

    # Compare with lane flow
    lane_col_fast = f'Lane{lane_num}_Fast'
    lane_col_regular = f'Lane{lane_num}'

    if lane_col_fast in df_sensor.columns:
        flow_val = pd.to_numeric(sample_row[lane_col_fast], errors='coerce')
        print(f"  {lane_col_fast + ' (flow)':40} = {flow_val:>6}")
        if pd.notna(flow_val) and total_from_classes > 0:
            diff = total_from_classes - flow_val
            pct_diff = (diff / flow_val * 100) if flow_val != 0 else 0
            print(f"  {'Difference (class_total - flow)':40} = {diff:>6.1f} ({pct_diff:+.1f}%)")
    elif lane_col_regular in df_sensor.columns:
        flow_val = pd.to_numeric(sample_row[lane_col_regular], errors='coerce')
        print(f"  {lane_col_regular + ' (flow)':40} = {flow_val:>6}")
        if pd.notna(flow_val) and total_from_classes > 0:
            diff = total_from_classes - flow_val
            pct_diff = (diff / flow_val * 100) if flow_val != 0 else 0
            print(f"  {'Difference (class_total - flow)':40} = {diff:>6.1f} ({pct_diff:+.1f}%)")

# Check aggregated columns
print(f"\n" + "-"*80)
print("AGGREGATED COLUMNS (Direction and Total):")
print("-"*80)

print(f"\nDirection aggregation:")
dir_cls_cols = [c for c in df_sensor.columns if c.startswith('cls_Direction_')]
total_from_direction = 0
for col in sorted(dir_cls_cols):
    val = sample_row[col]
    if pd.notna(val):
        val_numeric = pd.to_numeric(val, errors='coerce')
        print(f"  {col:40} = {val:>6}")
        if pd.notna(val_numeric):
            total_from_direction += val_numeric

if 'Direction' in df_sensor.columns:
    direction_flow = sample_row['Direction']
    print(f"  {'Direction (flow)':40} = {direction_flow:>6}")
    print(f"  {'Total from cls_Direction':40} = {total_from_direction:>6}")

print(f"\nTotal aggregation:")
total_cls_cols = [c for c in df_sensor.columns if c.startswith('total_cls_')]
total_from_total_cls = 0
for col in sorted(total_cls_cols):
    val = sample_row[col]
    if pd.notna(val):
        val_numeric = pd.to_numeric(val, errors='coerce')
        print(f"  {col:40} = {val:>6}")
        if pd.notna(val_numeric):
            total_from_total_cls += val_numeric

if 'Total' in df_sensor.columns:
    total_flow = sample_row['Total']
    print(f"  {'Total (flow)':40} = {total_flow:>6}")
    print(f"  {'Total from total_cls':40} = {total_from_total_cls:>6}")

# Check if total_cls is double counting
print(f"\n" + "="*80)
print("POTENTIAL DOUBLE-COUNTING CHECK:")
print("="*80)

# Sum all individual lanes
individual_lane_totals = {}
for lane_num in range(1, 9):
    cls_cols = [c for c in df_sensor.columns if c.startswith(f'cls_Lane{lane_num}_')]
    lane_total = 0
    for col in cls_cols:
        val = sample_row[col]
        if pd.notna(val):
            val_numeric = pd.to_numeric(val, errors='coerce')
            if pd.notna(val_numeric):
                lane_total += val_numeric
    if lane_total > 0:
        individual_lane_totals[lane_num] = lane_total

print(f"\nSum of individual lane class totals:")
for lane_num, total in sorted(individual_lane_totals.items()):
    print(f"  Lane {lane_num}: {total:>6.0f}")

sum_of_individual_lanes = sum(individual_lane_totals.values())
print(f"  {'SUM of all lanes':12} {sum_of_individual_lanes:>6.0f}")

print(f"\nTotal from total_cls columns: {total_from_total_cls:>6.0f}")

if total_from_total_cls > 0:
    diff = sum_of_individual_lanes - total_from_total_cls
    print(f"Difference (individual lanes - total_cls): {diff:>6.0f}")

    if abs(diff) < 0.01:
        print("[OK] total_cls matches sum of individual lanes (no double counting)")
    else:
        print("[WARNING] total_cls does NOT match sum of individual lanes!")

# Show what columns the pcu_converter would use
print(f"\n" + "="*80)
print("COLUMNS THAT pcu_converter.py WOULD USE:")
print("="*80)

pcu_values = {
    "0_3_5": 0.5,
    "3_5_6": 1.0,
    "6_8": 1.5,
    "8_10": 2.0,
    "10_12": 2.5,
    "12_Infinity": 3.0
}

# Lane detection logic from pcu_converter.py
lane_cols = [col for col in df_sensor.columns if col.startswith('cls_Lane')]
lane_numbers = sorted(set([
    int(re.search(r'cls_Lane(\d+)', col).group(1))
    for col in lane_cols
    if re.search(r'cls_Lane(\d+)', col)
]))

print(f"\nDetected lanes: {lane_numbers}")

for lane in lane_numbers:
    print(f"\nLane {lane}:")
    class_cols = {}

    for class_name in pcu_values.keys():
        col_fast = f'cls_Lane{lane}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane}_{class_name}'

        if col_fast in df_sensor.columns:
            class_cols[class_name] = col_fast
        elif col_regular in df_sensor.columns:
            class_cols[class_name] = col_regular

    if class_cols:
        for class_name, col_name in sorted(class_cols.items()):
            val = sample_row[col_name]
            print(f"  {class_name:12} from {col_name:40} = {val if pd.notna(val) else 'None':>6}")
    else:
        print(f"  No columns found")

# Check if any columns are being used that shouldn't be
print(f"\n" + "="*80)
print("CHECKING FOR INCORRECT COLUMN USAGE:")
print("="*80)

all_cls_lane_cols = [c for c in df_sensor.columns if c.startswith('cls_Lane')]
print(f"\nTotal cls_Lane columns: {len(all_cls_lane_cols)}")

# Check for any cls_Lane columns that don't match expected pattern
unexpected_cols = []
for col in all_cls_lane_cols:
    # Expected patterns:
    # cls_Lane{N}_Fast_{class}
    # cls_Lane{N}_{class}
    expected = False
    for class_name in pcu_values.keys():
        for lane in lane_numbers:
            if col == f'cls_Lane{lane}_Fast_{class_name}' or col == f'cls_Lane{lane}_{class_name}':
                expected = True
                break
        if expected:
            break

    if not expected:
        unexpected_cols.append(col)

if unexpected_cols:
    print(f"\n[WARNING] Found unexpected cls_Lane columns:")
    for col in unexpected_cols:
        print(f"  {col}")
else:
    print(f"\n[OK] All cls_Lane columns match expected patterns")
