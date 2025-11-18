"""Analyze PCU factors to understand the distribution."""

import pandas as pd
import numpy as np

# Load the parquet file
vcc_file = r"F:\OneDrive - Aimsun SLU\2218 - AD Mobility- Provision of Hybrid Model Enhancements\Task 3 - Model Maintenance and Automation\02_Data\02_InputData\vcc_data.parquet"
df = pd.read_parquet(vcc_file)

# Filter for a specific sensor
sensor_id = "SHZ_1_L71_IB"
df_sensor = df[df['Sensor_ID'] == sensor_id].copy()

print(f"Sensor: {sensor_id}")
print(f"Total rows: {len(df_sensor):,}")
print("\n" + "="*80)
print("VEHICLE DISTRIBUTION ANALYSIS")
print("="*80)

# PCU values
pcu_values = {
    "0_3_5": 0.5,
    "3_5_6": 1.0,
    "6_8": 1.5,
    "8_10": 2.0,
    "10_12": 2.5,
    "12_Infinity": 3.0
}

# Analyze distribution for each lane across ALL data
for lane_num in range(1, 8):  # Skip lane 8 (has None values)
    print(f"\n" + "-"*80)
    print(f"LANE {lane_num} - AGGREGATED STATISTICS")
    print("-"*80)

    # Find columns for this lane
    cls_cols = {}
    for class_name in pcu_values.keys():
        col_fast = f'cls_Lane{lane_num}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane_num}_{class_name}'

        if col_fast in df_sensor.columns:
            cls_cols[class_name] = col_fast
        elif col_regular in df_sensor.columns:
            cls_cols[class_name] = col_regular

    if not cls_cols:
        print(f"  No classification columns found")
        continue

    # Calculate total counts across ALL intervals
    total_counts = {}
    for class_name, col_name in cls_cols.items():
        # Convert to numeric and sum
        count = pd.to_numeric(df_sensor[col_name], errors='coerce').fillna(0).sum()
        total_counts[class_name] = count

    # Overall statistics
    grand_total = sum(total_counts.values())

    print(f"\nTotal vehicles observed: {grand_total:,.0f}")
    print(f"\nVehicle distribution:")

    for class_name in sorted(total_counts.keys()):
        count = total_counts[class_name]
        percentage = (count / grand_total * 100) if grand_total > 0 else 0
        pcu_val = pcu_values[class_name]
        print(f"  {class_name:12} : {count:>10,.0f} vehicles ({percentage:>5.1f}%) [PCU = {pcu_val}]")

    # Calculate overall PCU factor for this lane
    if grand_total > 0:
        overall_pcu = sum(
            (total_counts[class_name] / grand_total) * pcu_values[class_name]
            for class_name in total_counts.keys()
        )
        print(f"\nOverall PCU factor for Lane {lane_num}: {overall_pcu:.4f}")

        # Calculate what the flow would be with PCU conversion
        example_flow_veh = 1000  # vehicles/h
        example_flow_pcu = example_flow_veh * overall_pcu
        print(f"Example: {example_flow_veh} veh/h * {overall_pcu:.4f} = {example_flow_pcu:.0f} PCU/h")
    else:
        print(f"\nNo vehicles observed in Lane {lane_num}")

# Check if there are unusually high proportions of 0_3_5
print(f"\n" + "="*80)
print("CHECKING FOR UNUSUAL PATTERNS")
print("="*80)

# Calculate percentage of 0_3_5 across all lanes
all_lane_stats = []

for lane_num in range(1, 8):
    cls_cols = {}
    for class_name in pcu_values.keys():
        col_fast = f'cls_Lane{lane_num}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane_num}_{class_name}'

        if col_fast in df_sensor.columns:
            cls_cols[class_name] = col_fast
        elif col_regular in df_sensor.columns:
            cls_cols[class_name] = col_regular

    if not cls_cols:
        continue

    # Calculate total counts
    total_counts = {}
    for class_name, col_name in cls_cols.items():
        count = pd.to_numeric(df_sensor[col_name], errors='coerce').fillna(0).sum()
        total_counts[class_name] = count

    grand_total = sum(total_counts.values())

    if grand_total > 0:
        pct_0_3_5 = (total_counts.get('0_3_5', 0) / grand_total * 100)
        pct_3_5_6 = (total_counts.get('3_5_6', 0) / grand_total * 100)

        all_lane_stats.append({
            'lane': lane_num,
            'total': grand_total,
            'pct_0_3_5': pct_0_3_5,
            'pct_3_5_6': pct_3_5_6,
            'count_0_3_5': total_counts.get('0_3_5', 0),
            'count_3_5_6': total_counts.get('3_5_6', 0)
        })

# Show comparison
df_stats = pd.DataFrame(all_lane_stats)
print(f"\nSummary across all lanes:")
print(f"{'Lane':<6} {'Total Veh':>12} {'% 0-3.5m':>12} {'% 3.5-6m':>12}")
print("-"*50)

for _, row in df_stats.iterrows():
    print(f"{int(row['lane']):<6} {row['total']:>12,.0f} {row['pct_0_3_5']:>11.1f}% {row['pct_3_5_6']:>11.1f}%")

avg_pct_0_3_5 = df_stats['pct_0_3_5'].mean()
avg_pct_3_5_6 = df_stats['pct_3_5_6'].mean()

print("-"*50)
print(f"{'AVG':<6} {'':<12} {avg_pct_0_3_5:>11.1f}% {avg_pct_3_5_6:>11.1f}%")

# Check if 0_3_5 is unusually high compared to expected traffic composition
print(f"\n" + "-"*80)
print("INTERPRETATION:")
print("-"*80)

if avg_pct_0_3_5 > 30:
    print(f"[WARNING] Average 0-3.5m percentage ({avg_pct_0_3_5:.1f}%) is unusually HIGH")
    print(f"          This category includes motorcycles and very light vehicles.")
    print(f"          Typical highway traffic: 5-15% motorcycles/light vehicles")
    print(f"          This suggests either:")
    print(f"          1. Heavy motorcycle usage (common in some regions)")
    print(f"          2. Data quality issue (possible misclassification)")
elif avg_pct_0_3_5 > 15:
    print(f"[INFO] Average 0-3.5m percentage ({avg_pct_0_3_5:.1f}%) is moderately HIGH")
    print(f"       This is plausible for regions with significant motorcycle traffic")
else:
    print(f"[OK] Average 0-3.5m percentage ({avg_pct_0_3_5:.1f}%) is within normal range")

print(f"\nExpected PCU impact:")
if avg_pct_0_3_5 > 30:
    print(f"  With {avg_pct_0_3_5:.1f}% at PCU=0.5 and {avg_pct_3_5_6:.1f}% at PCU=1.0:")
    approx_pcu = (avg_pct_0_3_5/100 * 0.5) + (avg_pct_3_5_6/100 * 1.0) + ((100-avg_pct_0_3_5-avg_pct_3_5_6)/100 * 1.5)
    print(f"  Approximate PCU factor: {approx_pcu:.3f}")
    print(f"  Flow will be REDUCED by ~{(1-approx_pcu)*100:.0f}% when converting veh to PCU")
    print(f"  (This is because small vehicles count as 0.5 PCU each)")

# Check specific suspicious intervals
print(f"\n" + "="*80)
print("CHECKING FOR INTERVALS WITH EXTREME 0_3_5 PROPORTIONS")
print("="*80)

# For each lane, find intervals where 0_3_5 is > 80%
suspicious_intervals = []

for lane_num in range(1, 8):
    cls_cols = {}
    for class_name in pcu_values.keys():
        col_fast = f'cls_Lane{lane_num}_Fast_{class_name}'
        col_regular = f'cls_Lane{lane_num}_{class_name}'

        if col_fast in df_sensor.columns:
            cls_cols[class_name] = col_fast
        elif col_regular in df_sensor.columns:
            cls_cols[class_name] = col_regular

    if not cls_cols:
        continue

    # Calculate row-by-row
    for idx, row in df_sensor.iterrows():
        # Get counts for this interval
        interval_counts = {}
        for class_name, col_name in cls_cols.items():
            val = pd.to_numeric(row[col_name], errors='coerce')
            interval_counts[class_name] = val if pd.notna(val) else 0

        interval_total = sum(interval_counts.values())

        if interval_total > 10:  # Only check intervals with reasonable traffic
            pct_0_3_5 = (interval_counts.get('0_3_5', 0) / interval_total * 100)

            if pct_0_3_5 > 80:  # More than 80% are 0-3.5m vehicles
                suspicious_intervals.append({
                    'lane': lane_num,
                    'date': row['Db_Date'],
                    'time': row['start_time'],
                    'total': interval_total,
                    'pct_0_3_5': pct_0_3_5,
                    'count_0_3_5': interval_counts.get('0_3_5', 0),
                    'count_3_5_6': interval_counts.get('3_5_6', 0),
                })

        if len(suspicious_intervals) >= 10:  # Limit output
            break

    if len(suspicious_intervals) >= 10:
        break

if suspicious_intervals:
    print(f"\nFound {len(suspicious_intervals)} intervals with >80% in 0-3.5m category:")
    print(f"{'Lane':<6} {'Date':<12} {'Time':<8} {'Total':>8} {'0-3.5m':>8} {'%':>6}")
    print("-"*60)
    for interval in suspicious_intervals[:10]:
        print(f"{interval['lane']:<6} {str(interval['date']):<12} {interval['time']:<8} "
              f"{interval['total']:>8.0f} {interval['count_0_3_5']:>8.0f} {interval['pct_0_3_5']:>5.0f}%")

    print(f"\n[WARNING] These intervals show extreme proportions of small vehicles")
    print(f"          This may indicate a data quality issue")
else:
    print(f"\n[OK] No intervals found with extreme (>80%) 0-3.5m proportions")
