"""Test PCU calculation logic to find overestimation issue."""

import pandas as pd
import numpy as np
import re
from pathlib import Path

# Add the workflow directory to path to import pcu_converter
import sys
sys.path.insert(0, r"C:\Users\jean-noel.diltoer\software\sources\aimsun-python-scripts\FW_Abu_Dhabi\workflow")

from domains._00_RealDataSet.analyse.pcu_converter import (
    compute_hourly_pcu_factor,
    DEFAULT_PCU_VALUES
)

# Load the parquet file
vcc_file = r"F:\OneDrive - Aimsun SLU\2218 - AD Mobility- Provision of Hybrid Model Enhancements\Task 3 - Model Maintenance and Automation\02_Data\02_InputData\vcc_data.parquet"
df = pd.read_parquet(vcc_file)

# Filter for a specific sensor
sensor_id = "SHZ_1_L71_IB"
df_sensor = df[df['Sensor_ID'] == sensor_id].copy()

print(f"Sensor: {sensor_id}")
print(f"Total rows: {len(df_sensor)}")
print(f"Date range: {df_sensor['Db_Date'].min()} to {df_sensor['Db_Date'].max()}")
print("\n" + "="*80)
print("MANUAL PCU CALCULATION TEST")
print("="*80)

# Take a small sample - one day, one specific hour
test_date = pd.to_datetime('2024-04-01')
df_test = df_sensor[df_sensor['Db_Date'] == test_date].copy()

print(f"\nTest data: {test_date}")
print(f"Rows for this date: {len(df_test)}")

if len(df_test) == 0:
    # Try with first available date
    test_date = pd.to_datetime(df_sensor['Db_Date'].iloc[0])
    df_test = df_sensor[df_sensor['Db_Date'] == test_date].copy()
    print(f"\nNo data for 2024-04-01, using {test_date}")
    print(f"Rows for this date: {len(df_test)}")

# Extract hour from start_time
from domains._00_RealDataSet.analyse.pcu_converter import extract_hour_robust
df_test['hour'] = extract_hour_robust(df_test['start_time'])

# Focus on hour 9 (morning rush)
test_hour = 9
df_hour = df_test[df_test['hour'] == test_hour].copy()

print(f"\nTest hour: {test_hour}")
print(f"Rows for this hour: {len(df_hour)} (expected: 4 for 15-min intervals)")
print("\n" + "="*80)

# Manual calculation for Lane 1
print("LANE 1 (Fast Lane) - MANUAL CALCULATION:")
print("="*80)

lane = 1
pcu_values = DEFAULT_PCU_VALUES

# Build column mapping
class_cols = {}
for class_name in pcu_values.keys():
    col_fast = f'cls_Lane{lane}_Fast_{class_name}'
    col_regular = f'cls_Lane{lane}_{class_name}'

    if col_fast in df_hour.columns:
        class_cols[class_name] = col_fast
    elif col_regular in df_hour.columns:
        class_cols[class_name] = col_regular

print(f"\nColumn mapping for Lane {lane}:")
for class_name, col_name in class_cols.items():
    print(f"  {class_name:12} -> {col_name}")

# Show the data for each 15-min interval
print(f"\nData for each 15-min interval (hour {test_hour}):")
print("-"*80)

for idx, row in df_hour.iterrows():
    print(f"\nInterval: {row['start_time']} to {row['end_time']}")
    for class_name, col_name in class_cols.items():
        value = row[col_name]
        print(f"  {class_name:12} = {value}")

# Sum counts per class (as pcu_converter does)
print(f"\n" + "="*80)
print("SUMMING ACROSS 15-MIN INTERVALS (pcu_converter logic):")
print("="*80)

class_counts = {}
for class_name, col_name in class_cols.items():
    # This is the exact logic from pcu_converter.py
    count = pd.to_numeric(df_hour[col_name], errors='coerce').fillna(0).sum()
    class_counts[class_name] = count
    print(f"  {class_name:12} total count = {count:>8.1f}")

# Calculate total and PCU factor
total_vehicles = sum(class_counts.values())
print(f"\n  Total vehicles: {total_vehicles:.1f}")

if total_vehicles == 0:
    pcu_factor = 1.0
else:
    pcu_factor = sum(
        (class_counts[class_name] / total_vehicles) * pcu_values[class_name]
        for class_name in class_counts.keys()
    )

print(f"  PCU factor: {pcu_factor:.4f}")

# Show the breakdown
print(f"\n  PCU factor breakdown:")
for class_name in sorted(class_counts.keys()):
    if total_vehicles > 0:
        proportion = class_counts[class_name] / total_vehicles
        contribution = proportion * pcu_values[class_name]
        print(f"    {class_name:12}: {class_counts[class_name]:>6.1f} veh ({proportion:>6.1%}) x {pcu_values[class_name]} PCU = {contribution:.4f}")

# Now test with the actual function
print(f"\n" + "="*80)
print("TESTING ACTUAL compute_hourly_pcu_factor() FUNCTION:")
print("="*80)

try:
    pcu_factors = compute_hourly_pcu_factor(
        df_sensor,
        sensor_id,
        pcu_values=pcu_values,
        date_range={"start": str(test_date.date()), "end": str(test_date.date())}
    )

    # Filter to our test hour and lane
    test_result = pcu_factors[
        (pcu_factors['Db_Date'] == test_date) &
        (pcu_factors['hour'] == test_hour) &
        (pcu_factors['lane_number'] == lane)
    ]

    if len(test_result) > 0:
        print(f"\nResult from function:")
        print(f"  Lane: {lane}")
        print(f"  Date: {test_date.date()}")
        print(f"  Hour: {test_hour}")
        print(f"  PCU factor: {test_result['pcu_factor'].iloc[0]:.4f}")
        print(f"  Total vehicles: {test_result['total_vehicles'].iloc[0]:.1f}")

        # Compare with manual calculation
        print(f"\n  Comparison:")
        print(f"    Manual PCU factor:   {pcu_factor:.4f}")
        print(f"    Function PCU factor: {test_result['pcu_factor'].iloc[0]:.4f}")
        print(f"    Difference:          {abs(pcu_factor - test_result['pcu_factor'].iloc[0]):.6f}")

        if abs(pcu_factor - test_result['pcu_factor'].iloc[0]) < 0.0001:
            print(f"\n  [OK] Results match!")
        else:
            print(f"\n  [ERROR] Results don't match!")

            # Show class_counts from function
            print(f"\n  Class counts from function:")
            class_counts_func = test_result['class_counts'].iloc[0]
            for class_name, count in sorted(class_counts_func.items()):
                print(f"    {class_name:12} = {count:.1f}")
    else:
        print(f"\n  [WARNING] No result found for Lane {lane}, Hour {test_hour}")
        print(f"\n  Available results:")
        print(pcu_factors[['Db_Date', 'hour', 'lane_number', 'pcu_factor']].head(10))

except Exception as e:
    print(f"\n  [ERROR] Function failed: {e}")
    import traceback
    traceback.print_exc()

# Check for potential issues with column names
print(f"\n" + "="*80)
print("CHECKING FOR POTENTIAL COLUMN NAME ISSUES:")
print("="*80)

# Look for columns that might be incorrectly matched
all_cls_cols = [c for c in df_sensor.columns if 'cls_' in c.lower()]
print(f"\nAll columns with 'cls_' in name ({len(all_cls_cols)}):")

# Group by pattern
lane_fast_cols = [c for c in all_cls_cols if '_Fast_' in c]
lane_regular_cols = [c for c in all_cls_cols if c.startswith('cls_Lane') and '_Fast_' not in c]
other_cls_cols = [c for c in all_cls_cols if c not in lane_fast_cols and c not in lane_regular_cols]

print(f"\n  Lane_Fast columns ({len(lane_fast_cols)}):")
for col in sorted(lane_fast_cols)[:10]:  # Show first 10
    print(f"    {col}")
if len(lane_fast_cols) > 10:
    print(f"    ... and {len(lane_fast_cols) - 10} more")

print(f"\n  Lane regular columns ({len(lane_regular_cols)}):")
for col in sorted(lane_regular_cols)[:10]:
    print(f"    {col}")
if len(lane_regular_cols) > 10:
    print(f"    ... and {len(lane_regular_cols) - 10} more")

print(f"\n  Other cls columns ({len(other_cls_cols)}):")
for col in sorted(other_cls_cols):
    print(f"    {col}")
