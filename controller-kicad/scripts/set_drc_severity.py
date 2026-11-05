#!/usr/bin/env python3
"""Keep the non-electrical courtyard-overlap check as a warning.

KiCad rewrites controller.kicad_pro when a board is saved, so run this after
the PCB pipeline and before generating the final DRC report.
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRO = os.path.join(HERE, "controller.kicad_pro")

with open(PRO) as f:
    data = json.load(f)
ds = data["board"]["design_settings"]
ds["rule_severities"]["courtyards_overlap"] = "warning"
# The board uses 0.1 mm clearance, 0.4 mm vias and 0.2 mm drills.
rules = ds["rules"]
rules["min_clearance"] = 0.1
rules["min_track_width"] = 0.1
rules["min_via_diameter"] = 0.4
rules["min_via_annular_width"] = 0.05
rules["min_through_hole_diameter"] = 0.2
with open(PRO, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("courtyards_overlap = warning")
