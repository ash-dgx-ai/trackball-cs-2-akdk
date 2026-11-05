#!/usr/bin/env python3
"""Generate a KiCad 9 block-diagram schematic for the controller board.

The schematic uses one custom symbol per component and global labels for every
connection.  It is intended as a reviewable connection diagram; the PCB is the
authoritative layout.
"""
import os
import uuid

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "controller.kicad_sch")


def uid():
    return str(uuid.uuid4())


def esc(s):
    return s.replace('"', '\\"')


# Component definitions: (name, reference, value, footprint, lcsc, pins)
# pins: list of (number, name, net or None).  None means no-connect.
COMPONENTS = []


def add(name, ref, value, footprint, lcsc, pins):
    COMPONENTS.append((name, ref, value, footprint, lcsc, pins))


add("E73", "U1", "E73-2G4M08S1C", "controller:E73-2G4M08S1C", "C356849", [
    (1, "P1.11", None), (2, "P1.10", None), (3, "P0.03", None), (4, "P0.28", None),
    (5, "GND", "GND"), (6, "P1.13", "P1.13"), (7, "P0.02", "P0.02"),
    (8, "P0.29", "P0.29"), (9, "P0.31", "P0.31"), (10, "P0.30", None),
    (11, "P0.00", None), (12, "P0.26", "P0.26"), (13, "P0.01", None),
    (14, "P0.06", "P0.06"), (15, "P0.05", None), (16, "P0.08", "P0.08"),
    (17, "P1.09", "P1.09"), (18, "P0.04", "ADC"), (19, "VDD", "3V3"),
    (20, "P0.12", "P0.12"), (21, "GND", "GND"), (22, "P0.07", None),
    (23, "VDDH", "VDDH"), (24, "GND", "GND"), (25, "DCCH", None),
    (26, "P0.18", "P0.18"), (27, "VBUS", "VBUS"), (28, "P0.15", "P0.15"),
    (29, "D-", "USB_DM"), (30, "P0.17", None), (31, "D+", "USB_DP"),
    (32, "P0.20", "P0.20"), (33, "P0.13", "P0.13"), (34, "P0.22", "P0.22"),
    (35, "P0.24", "P0.24"), (36, "P1.00", "P1.00"), (37, "SWDIO", "SWDIO"),
    (38, "P1.02", None), (39, "SWDCLK", "SWCLK"), (40, "P1.04", None),
    (41, "P0.09", "P0.09"), (42, "P1.06", "P1.06"), (43, "P0.10", "P0.10"),
])

add("USB_C", "J1", "USB-C", "controller:USB_C", "C165948", [
    ("A1B12", "GND", "GND"), ("A4B9", "VBUS", "VBUS"), ("A5", "CC1", "CC1"),
    ("A6", "DP1", "USB_DP"), ("A7", "DN1", "USB_DM"), ("A8", "SBU1", None),
    ("B1A12", "GND", "GND"), ("B4A9", "VBUS", "VBUS"), ("B5", "CC2", "CC2"),
    ("B6", "DP2", "USB_DP"), ("B7", "DN2", "USB_DM"), ("B8", "SBU2", None),
    (1, "SHIELD", "GND"), (2, "SHIELD", "GND"), (3, "SHIELD", "GND"), (4, "SHIELD", "GND"),
])

add("TP4057", "U2", "TP4057", "controller:TP4057", "C725791", [
    (1, "CHRG", "CHRG"), (2, "GND", "GND"), (3, "BAT", "VBAT"),
    (4, "VCC", "VBUS"), (5, "STDBY", None), (6, "PROG", "PROG"),
])

add("BAT", "J2", "Battery PH2", "controller:JST_PH_2P", "C131337", [
    (1, "+", "VBAT"), (2, "-", "GND"),
])

add("SW", "SW1", "DPDT", "controller:SW_DPDT", "C97434", [
    (1, "1", "VBAT_SW"), (2, "2", "VBAT"), (3, "3", None),
    (4, "4", None), (5, "5", "P0.13"), (6, "6", "GND"),
])

add("FFC", "J3", "FFC 6P 0.5mm", "controller:FFC_6P", "C202118", [
    (1, "1", "GND"), (2, "2", "P0.12"), (3, "3", "P1.09"),
    (4, "4", "P0.15"), (5, "5", "P0.13"), (6, "6", "3V3"),
    (7, "MP", "GND"), (8, "MP", "GND"),
])

add("TEST", "J4", "Pogo test pads", "controller:TestPads_6x2.54", "", [
    (1, "VTref", "3V3"), (2, "SWDIO", "SWDIO"), (3, "SWCLK", "SWCLK"),
    (4, "GND", "GND"), (5, "RESET", "P0.18"), (6, "GND", "GND"),
])

add("CON", "J5", "Conthrough 2x9 THT", "controller:Conthrough_2x9_THT", "", [
    (1, "1", "P0.10"), (2, "2", "P0.09"), (3, "3", "P1.00"),
    (4, "4", "P0.24"), (5, "5", "P0.22"), (6, "6", "P0.20"),
    (7, "7", None), (8, "8", None), (9, "9", None), (10, "10", None),
    (11, "11", "P0.08"), (12, "12", "P0.06"), (13, "13", "P0.26"),
    (14, "14", "P0.31"), (15, "15", "P0.29"), (16, "16", "P0.02"),
    (17, "17", "GND"), (18, "18", "P1.13"),
])

# Passives: (ref, value, footprint, lcsc, pin1 net, pin2 net)
PASSIVES = [
    ("R1", "5.1k", "Resistor_SMD:R_0603_1608Metric", "C23186", "CC1", "GND"),
    ("R2", "5.1k", "Resistor_SMD:R_0603_1608Metric", "C23186", "CC2", "GND"),
    ("R3", "6.2k", "Resistor_SMD:R_0603_1608Metric", "C4260", "PROG", "GND"),
    ("R4", "2M", "Resistor_SMD:R_0603_1608Metric", "C22976", "VBAT", "ADC"),
    ("R5", "1M", "Resistor_SMD:R_0603_1608Metric", "C22935", "ADC", "GND"),
    ("R6", "1k", "Resistor_SMD:R_0603_1608Metric", "C21190", "P1.06", "LED_A"),
    ("C1", "1uF", "Capacitor_SMD:C_0603_1608Metric", "C15849", "VDDH", "GND"),
    ("C2", "0.1uF", "Capacitor_SMD:C_0603_1608Metric", "C14663", "VDDH", "GND"),
    ("C3", "1uF", "Capacitor_SMD:C_0603_1608Metric", "C15849", "3V3", "GND"),
    ("C5", "0.1uF", "Capacitor_SMD:C_0603_1608Metric", "C14663", "ADC", "GND"),
    ("C6", "1uF", "Capacitor_SMD:C_0603_1608Metric", "C15849", "VBUS", "GND"),
    ("D1", "SS14", "Diode_SMD:D_SMA", "C2480", "VBUS", "VDDH"),
    ("D2", "SS14", "Diode_SMD:D_SMA", "C2480", "VBAT_SW", "VDDH"),
    ("LED1", "Green", "LED_SMD:LED_0603_1608Metric", "C2986031", "LED_A", "GND"),
]
for ref, val, fp, lcsc, n1, n2 in PASSIVES:
    add(ref, ref, val, fp, lcsc, [(1, "1", n1), (2, "2", n2)])


def symbol_def(name, pins, width, height):
    # Split pins evenly left/right.
    n = len(pins)
    left = pins[: (n + 1) // 2]
    right = pins[(n + 1) // 2:]
    half = width / 2.0
    top = height / 2.0
    spacing = 2.54
    out = []
    out.append(f'    (symbol "controller:{name}"')
    out.append('      (exclude_from_sim no)')
    out.append('      (in_bom yes)')
    out.append('      (on_board yes)')
    out.append(f'      (property "Reference" "{name[0]}" (at 0 {top + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'      (property "Value" "{name}" (at 0 {-top - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    out.append('      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    out.append(f'      (symbol "{name}_0_1"')
    out.append(f'        (rectangle (start {-half:.2f} {top:.2f}) (end {half:.2f} {-top:.2f})')
    out.append('          (stroke (width 0.254) (type default))')
    out.append('          (fill (type background))')
    out.append('        )')
    out.append('      )')
    out.append(f'      (symbol "{name}_1_1"')
    for i, (num, pname, net) in enumerate(left):
        y = top - 2.54 - i * spacing
        out.append(f'        (pin passive line (at {-half:.2f} {y:.2f} 180) (length 2.54)')
        out.append(f'          (name "{esc(str(pname))}" (effects (font (size 1.27 1.27))))')
        out.append(f'          (number "{esc(str(num))}" (effects (font (size 1.27 1.27))))')
        out.append('        )')
    for i, (num, pname, net) in enumerate(right):
        y = top - 2.54 - i * spacing
        out.append(f'        (pin passive line (at {half:.2f} {y:.2f} 0) (length 2.54)')
        out.append(f'          (name "{esc(str(pname))}" (effects (font (size 1.27 1.27))))')
        out.append(f'          (number "{esc(str(num))}" (effects (font (size 1.27 1.27))))')
        out.append('        )')
    out.append('      )')
    out.append('    )')
    return "\n".join(out)


def main():
    parts = []
    parts.append('(kicad_sch')
    parts.append('  (version 20250114)')
    parts.append('  (generator "eeschema")')
    parts.append('  (generator_version "9.0")')
    parts.append(f'  (uuid "{uid()}")')
    parts.append('  (paper "A2")')
    parts.append('  (title_block')
    parts.append('    (title "Auto-KDK compatible wireless controller")')
    parts.append('    (rev "1")')
    parts.append('    (comment 1 "Reverse-engineered from trackball-cs-2 AKDK data")')
    parts.append('  )')
    parts.append('  (lib_symbols')
    for name, ref, value, fp, lcsc, pins in COMPONENTS:
        width = 30.48 if len(pins) > 12 else 20.32
        height = max(20.32, 2.54 * ((len(pins) + 1) // 2 + 2))
        parts.append(symbol_def(name, pins, width, height))
    parts.append('  )')

    # Place symbols in a grid and add labels/no-connects.
    x = 80.0
    y = 80.0
    col = 0
    for name, ref, value, fp, lcsc, pins in COMPONENTS:
        width = 30.48 if len(pins) > 12 else 20.32
        height = max(20.32, 2.54 * ((len(pins) + 1) // 2 + 2))
        sx, sy = x, y
        parts.append(f'  (symbol (lib_id "controller:{name}") (at {sx:.2f} {sy:.2f} 0) (unit 1)')
        parts.append('    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)')
        parts.append(f'    (uuid "{uid()}")')
        parts.append(f'    (property "Reference" "{ref}" (at {sx:.2f} {sy - height/2 - 2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
        parts.append(f'    (property "Value" "{value}" (at {sx:.2f} {sy + height/2 + 2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
        parts.append(f'    (property "Footprint" "{fp}" (at {sx:.2f} {sy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        parts.append(f'    (property "LCSC Part" "{lcsc}" (at {sx:.2f} {sy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        parts.append('  )')
        n = len(pins)
        left = pins[: (n + 1) // 2]
        right = pins[(n + 1) // 2:]
        half = width / 2.0
        top = height / 2.0
        spacing = 2.54
        for i, (num, pname, net) in enumerate(left):
            py = sy + top - 2.54 - i * spacing
            px = sx - half - 2.54
            if net:
                parts.append(f'  (global_label "{esc(net)}" (shape input) (at {px:.2f} {py:.2f} 180)')
                parts.append('    (effects (font (size 1.27 1.27)) (justify right))')
                parts.append(f'    (uuid "{uid()}")')
                parts.append('  )')
            else:
                parts.append(f'  (no_connect (at {px:.2f} {py:.2f}) (uuid "{uid()}"))')
        for i, (num, pname, net) in enumerate(right):
            py = sy + top - 2.54 - i * spacing
            px = sx + half + 2.54
            if net:
                parts.append(f'  (global_label "{esc(net)}" (shape input) (at {px:.2f} {py:.2f} 0)')
                parts.append('    (effects (font (size 1.27 1.27)) (justify left))')
                parts.append(f'    (uuid "{uid()}")')
                parts.append('  )')
            else:
                parts.append(f'  (no_connect (at {px:.2f} {py:.2f}) (uuid "{uid()}"))')
        # advance grid: two columns, then next row
        col += 1
        if col == 2:
            col = 0
            x = 80.0
            y += height + 30.0
        else:
            x += width + 70.0

    parts.append('  (sheet_instances')
    parts.append('    (path "/" (page "1"))')
    parts.append('  )')
    parts.append(')')
    open(OUT, 'w').write("\n".join(parts) + "\n")
    print("Saved", OUT)


if __name__ == "__main__":
    main()
