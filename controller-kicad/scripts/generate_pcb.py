#!/usr/bin/env python3
"""Generate the AKDK-compatible wireless controller PCB (KiCad 9).

Run with the KiCad AppImage Python:
  /home/fum198/.local/opt/squashfs-root/bin/python3.11 scripts/generate_pcb.py
"""
import os
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRETTY = os.path.join(HERE, "controller.pretty")
KICAD_FP = "/home/fum198/.local/opt/squashfs-root/usr/share/kicad/footprints"
OUT = os.path.join(HERE, "controller.kicad_pcb")

MM = pcbnew.FromMM
V = pcbnew.VECTOR2I_MM


def add_outline(board):
    # Board outline: 98.0 x 29.0 mm, origin at top-left.
    pts = [(0, 0), (98, 0), (98, 29), (0, 29)]
    for i in range(4):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*pts[i]))
        s.SetEnd(V(*pts[(i + 1) % 4]))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)


def load_fp(libpath, name, ref, value, lcsc, x, y, rot=0.0, bottom=False, flip_top_bottom=False):
    fp = pcbnew.FootprintLoad(libpath, name)
    if fp is None:
        raise RuntimeError(f"Footprint not found: {libpath}/{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(V(x, y))
    fp.SetOrientationDegrees(rot)
    fp.SetField("LCSC Part", lcsc)
    fp.SetField("Manufacturer", "")
    fp.SetField("Description", "")
    BOARD.Add(fp)
    if bottom:
        fp.Flip(fp.GetPosition(), flip_top_bottom)
    # NPTH mechanical pads should not trigger annular-ring DRC.
    for p in fp.Pads():
        if p.GetNumber() == "" and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
            p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    return fp


def main():
    global BOARD
    board = pcbnew.BOARD()
    BOARD = board
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(MM(1.6))
    ds.m_TrackMinWidth = MM(0.1)
    ds.m_MinClearance = MM(0.1)
    ds.m_ViasMinSize = MM(0.6)
    ds.m_ViasMinDrill = MM(0.3)
    ds.m_HoleClearance = MM(0.2)
    ds.m_HoleToHoleMin = MM(0.3)
    ds.m_CopperEdgeClearance = MM(0.2)
    try:
        ds.m_NetSettings.GetDefaultNetclass().SetClearance(MM(0.1))
        ds.m_NetSettings.GetDefaultNetclass().SetTrackWidth(MM(0.2))
    except Exception:
        pass

    add_outline(board)

    # Main components
    usb = load_fp(PRETTY, "USB_C", "J1", "USB-C", "C165948", 30.85, 3.5, 0.0, True, False)
    mod = load_fp(PRETTY, "E73-2G4M08S1C", "U1", "E73-2G4M08S1C", "C356849", 87.0, 14.5, 270.0, True)
    tp = load_fp(PRETTY, "MCP73831_SOT-23-5", "U2", "MCP73831", "C14879", 39.0, 8.0, 0.0, True)
    bat = load_fp(PRETTY, "JST_PH_2P", "J2", "Battery PH2", "C131337", 36.0, 14.5, 0.0, True)
    sw = load_fp(PRETTY, "SW_DPDT", "SW1", "DPDT", "C97434", 46.0, 14.5, 0.0, True)
    ffc = load_fp(PRETTY, "FFC_6P", "J3", "FFC 6P 0.5mm", "C202118", 55.0, 14.5, 270.0, True)
    test = load_fp(PRETTY, "TestPads_6x2.54", "J4", "Pogo test pads", "", 0.0, 0.0, 0.0, False)
    test.SetAttributes(test.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    con = load_fp(PRETTY, "Conthrough_2x9_THT", "J5", "Conthrough 2x9 THT", "", 0.0, 0.0, 0.0, False)
    con.SetAttributes(con.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)

    # Passives (0603 / SMA).  Values are set later after checking the schematic.
    r_lib = os.path.join(KICAD_FP, "Resistor_SMD.pretty")
    c_lib = os.path.join(KICAD_FP, "Capacitor_SMD.pretty")
    led_lib = os.path.join(KICAD_FP, "LED_SMD.pretty")
    d_lib = os.path.join(KICAD_FP, "Diode_SMD.pretty")

    def r(ref, val, lcsc, x, y, rot=0.0):
        return load_fp(r_lib, "R_0603_1608Metric", ref, val, lcsc, x, y, rot, True)
    def c(ref, val, lcsc, x, y, rot=0.0):
        return load_fp(c_lib, "C_0603_1608Metric", ref, val, lcsc, x, y, rot, True)
    def led(ref, val, lcsc, x, y, rot=0.0):
        return load_fp(led_lib, "LED_0603_1608Metric", ref, val, lcsc, x, y, rot, True)
    # SS14 (C2480) is SMA / DO-214AC, not SOD-323.
    def d(ref, val, lcsc, x, y, rot=0.0):
        return load_fp(d_lib, "D_SMA", ref, val, lcsc, x, y, rot, True)

    r("R1", "5.1k", "C23186", 22.0, 5.0, 90)
    r("R2", "5.1k", "C23186", 24.0, 5.0, 90)
    r("R3", "6.2k", "C4260", 40.5, 12.0, 0)
    r("R4", "2M", "C22976", 50.0, 7.0, 90)
    r("R5", "1M", "C22935", 50.0, 10.0, 90)
    r("R6", "1k", "C21190", 91.0, 2.5, 0)
    c("C1", "1uF", "C15849", 80.5, 5.0, 0)
    c("C2", "0.1uF", "C14663", 79.4, 8.0, 0)
    c("C3", "4.7uF", "C19666", 88.0, 4.0, 0)
    c("C5", "0.1uF", "C14663", 50.0, 12.0, 0)
    c("C6", "10uF", "C19702", 39.0, 3.0, 0)
    c("C7", "10uF", "C19702", 35.0, 9.0, 0)
    c("C8", "10uF", "C19702", 37.0, 1.8, 0)
    c("C9", "10uF", "C19702", 32.4, 10.0, 0)
    d("D1", "SS14", "C2480", 40.0, 5.0, 0)
    d("D2", "SS14", "C2480", 49.5, 4.4, 0)
    led("LED1", "Green", "C2986031", 89.0, 1.5, 180)

    # The E73 runs in high-voltage mode: VDDH is fed from the battery/USB
    # through the Schottky diodes, and VDD is the module's internal 3.3 V
    # regulator output that feeds the 3V3 rail.  VDD and VDDH are NOT tied
    # together on the board; DCCH is left unconnected (LDO mode).

    pcbnew.SaveBoard(OUT, board)
    print("Saved", OUT)


if __name__ == "__main__":
    main()
