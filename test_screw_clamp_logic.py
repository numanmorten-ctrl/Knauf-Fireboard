#!/usr/bin/env python3
"""
Validation script for screw/clamp layer logic.

Tests:
1. 40mm Fireboard (2×20mm layers) → merges identical screws/clamps
2. Different screw types across layers → remain separate
3. Single layer handling
"""

import pandas as pd
from pathlib import Path
import sys

# Load data
DATA_DIR = Path("data")
layer_logic_df = pd.read_csv(DATA_DIR / "layer_logic.csv", sep=";")
screw_clamp_logic_df = pd.read_csv(DATA_DIR / "screw_clamp_logic.csv", sep=";")
materials_df = pd.read_csv(DATA_DIR / "materials.csv", sep=";")

print("=" * 70)
print("SCREW/CLAMP LAYER LOGIC VALIDATION")
print("=" * 70)

# Test 1: 40mm Fireboard (2×20mm layers)
print("\n[TEST 1] 40mm Fireboard with 2×20mm layers")
print("-" * 70)

forty_mm_layers = layer_logic_df[layer_logic_df["total_mm"].astype(int) == 40]
print(f"Found {len(forty_mm_layers)} layer configuration(s) for 40mm:")
for idx, row in forty_mm_layers.iterrows():
    print(f"  - Total: {row['total_mm']}mm, Layer {row['layer_no']}: {row['board_mm']}mm")

print("\nLooking up screws/clamps for each layer:")
scraped_materials = {}
for idx, layer_row in forty_mm_layers.iterrows():
    layer_no = int(layer_row["layer_no"])
    board_mm = int(layer_row["board_mm"])
    
    screw_lookup = screw_clamp_logic_df[
        (screw_clamp_logic_df["layer_no"].astype(int) == layer_no) &
        (screw_clamp_logic_df["board_mm"].astype(int) == board_mm)
    ]
    
    if not screw_lookup.empty:
        screw_row = screw_lookup.iloc[0]
        screw_code = screw_row["screw"]
        clamp_code = screw_row["clamp"]
        print(f"  Layer {layer_no}, Board {board_mm}mm:")
        print(f"    → Screw code: {screw_code}")
        print(f"    → Clamp code: {clamp_code}")
        
        # Lookup material
        screw_material = materials_df[materials_df["ART.NR."] == screw_code]
        clamp_material = materials_df[materials_df["ART.NR."] == clamp_code]
        
        if not screw_material.empty:
            print(f"    → Screw material: {screw_material.iloc[0]['BESKRIVELSE_DK']}")
        else:
            print(f"    → Screw material: NOT FOUND")
            
        if not clamp_material.empty:
            print(f"    → Clamp material: {clamp_material.iloc[0]['BESKRIVELSE_DK']}")
        else:
            print(f"    → Clamp material: NOT FOUND")
        
        # Track for deduplication
        if screw_code not in scraped_materials:
            scraped_materials[screw_code] = {"type": "screw", "count": 0}
        scraped_materials[screw_code]["count"] += 1
        
        if clamp_code not in scraped_materials:
            scraped_materials[clamp_code] = {"type": "clamp", "count": 0}
        scraped_materials[clamp_code]["count"] += 1

print("\nDeduplication check:")
for code, info in scraped_materials.items():
    if info["count"] > 1:
        print(f"  ✓ {code} appears {info['count']}x → SHOULD BE MERGED")
    else:
        print(f"  • {code} appears {info['count']}x → separate row")

# Test 2: Check for different screw types
print("\n[TEST 2] Check layer configurations with different screw types")
print("-" * 70)

# Find configurations that use different screws
layer_configs = {}
for idx, row in screw_clamp_logic_df.iterrows():
    key = (int(row["layer_no"]), int(row["board_mm"]))
    layer_configs[key] = row

# Check 30mm which has 1×15mm + 1×15mm (should have consistent screws per layer)
thirty_mm_layers = layer_logic_df[layer_logic_df["total_mm"].astype(int) == 30]
print(f"30mm config (1×15mm or 1×30mm):")
for idx, layer_row in thirty_mm_layers.iterrows():
    layer_no = int(layer_row["layer_no"])
    board_mm = int(layer_row["board_mm"])
    key = (layer_no, board_mm)
    if key in layer_configs:
        row = layer_configs[key]
        print(f"  Layer {layer_no}, {board_mm}mm: screw={row['screw']}, clamp={row['clamp']}")

# Test 3: Single layer (e.g., 20mm)
print("\n[TEST 3] Single layer configuration (20mm)")
print("-" * 70)

twenty_mm_layers = layer_logic_df[layer_logic_df["total_mm"].astype(int) == 20]
if len(twenty_mm_layers) == 1:
    print("✓ Single layer configuration found for 20mm")
    layer_row = twenty_mm_layers.iloc[0]
    layer_no = int(layer_row["layer_no"])
    board_mm = int(layer_row["board_mm"])
    
    screw_lookup = screw_clamp_logic_df[
        (screw_clamp_logic_df["layer_no"].astype(int) == layer_no) &
        (screw_clamp_logic_df["board_mm"].astype(int) == board_mm)
    ]
    
    if not screw_lookup.empty:
        screw_row = screw_lookup.iloc[0]
        print(f"  Layer {layer_no}, Board {board_mm}mm:")
        print(f"    → Screw: {screw_row['screw']}")
        print(f"    → Clamp: {screw_row['clamp']}")
else:
    print(f"  Found {len(twenty_mm_layers)} configurations for 20mm (not expected)")

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)
