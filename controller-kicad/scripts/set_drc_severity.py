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
data["board"]["design_settings"]["rule_severities"]["courtyards_overlap"] = "warning"
with open(PRO, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("courtyards_overlap = warning")
