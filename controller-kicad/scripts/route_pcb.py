#!/usr/bin/env python3
"""Assign nets and auto-route the controller PCB with Freerouting.

Run with the KiCad AppImage Python:
  /home/fum198/.local/opt/squashfs-root/bin/python3.11 scripts/route_pcb.py
"""
import os
import subprocess
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")
DSN = os.path.join(HERE, "controller.dsn")
SES = os.path.join(HERE, "controller.ses")
FREEROUTING = ["/home/fum198/.local/opt/jre25/bin/java", "-jar",
               "/home/fum198/.local/opt/freerouting/freerouting.jar"]


def get_fp(board, ref):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise RuntimeError(f"Footprint {ref} not found")
    return fp


def pad(fp, num):
    p = fp.FindPadByNumber(str(num))
    if p is None:
        raise RuntimeError(f"Pad {num} not found on {fp.GetReference()}")
    return p


def make_net(board, name):
    net = board.FindNet(name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
    return net


def assign(board, ref, num, netname):
    if netname is None:
        return
    p = pad(get_fp(board, ref), num)
    p.SetNet(make_net(board, netname))


def main():
    board = pcbnew.LoadBoard(PCB)

    # --- USB-C ---
    for n in ["A1B12", "B1A12", "1", "2", "3", "4"]:
        assign(board, "J1", n, "GND")
    for n in ["A4B9", "B4A9"]:
        assign(board, "J1", n, "VBUS")
    assign(board, "J1", "A5", "CC1")
    assign(board, "J1", "B5", "CC2")
    for n in ["A6", "B6"]:
        assign(board, "J1", n, "USB_DP")
    for n in ["A7", "B7"]:
        assign(board, "J1", n, "USB_DM")

    # --- E73 module (pin numbers are module pads) ---
    mod = {
        1: None, 2: None, 3: None, 4: None, 5: "GND",
        6: "P1.13", 7: "P0.02", 8: "P0.29", 9: "P0.31",
        10: None, 11: None, 12: "P0.26", 13: None, 14: "P0.06",
        15: None, 16: "P0.08", 17: "P1.09", 18: "ADC",
        19: "3V3", 20: "P0.12", 21: "GND", 22: None,
        23: "VDDH", 24: "GND", 25: None, 26: "P0.18",
        27: "VBUS", 28: "P0.15", 29: "USB_DM", 30: None,
        31: "USB_DP", 32: "P0.20", 33: "P0.13", 34: "P0.22",
        35: "P0.24", 36: "P1.00", 37: "SWDIO", 38: None,
        39: "SWCLK", 40: None, 41: "P0.09", 42: None, 43: "P0.10",
    }
    for n, net in mod.items():
        assign(board, "U1", n, net)

    # --- TP4057 ---
    tp = {1: "CHRG", 2: "GND", 3: "VBAT", 4: "VBUS", 5: None, 6: "PROG"}
    for n, net in tp.items():
        assign(board, "U2", n, net)

    # --- Battery connector ---
    assign(board, "J2", 1, "VBAT")
    assign(board, "J2", 2, "GND")

    # --- DPDT switch ---
    sw = {1: "VBAT_SW", 2: "VBAT", 3: None, 4: None, 5: "P0.13", 6: "GND"}
    for n, net in sw.items():
        assign(board, "SW1", n, net)

    # --- FFC (reversed order: 1=GND, 2=SCLK, 3=SDIO, 4=MOTION, 5=CS, 6=3V3) ---
    ffc = {1: "GND", 2: "P0.12", 3: "P1.09", 4: "P0.15", 5: "P0.13", 6: "3V3", 7: "GND", 8: "GND"}
    for n, net in ffc.items():
        assign(board, "J3", n, net)

    # --- SWD header ---
    swd = {1: "3V3", 2: "SWDIO", 3: "GND", 4: "SWCLK", 5: "GND",
           6: None, 7: None, 8: None, 9: "GND", 10: "P0.18"}
    for n, net in swd.items():
        assign(board, "J4", n, net)

    # --- Passives ---
    assign(board, "R1", 1, "CC1"); assign(board, "R1", 2, "GND")
    assign(board, "R2", 1, "CC2"); assign(board, "R2", 2, "GND")
    assign(board, "R3", 1, "PROG"); assign(board, "R3", 2, "GND")
    assign(board, "R4", 1, "VBAT"); assign(board, "R4", 2, "ADC")
    assign(board, "R5", 1, "ADC"); assign(board, "R5", 2, "GND")
    assign(board, "R6", 1, "P0.18"); assign(board, "R6", 2, "LED_A")
    assign(board, "C1", 1, "VDDH"); assign(board, "C1", 2, "GND")
    assign(board, "C2", 1, "VDDH"); assign(board, "C2", 2, "GND")
    assign(board, "C3", 1, "3V3"); assign(board, "C3", 2, "GND")
    assign(board, "C5", 1, "ADC"); assign(board, "C5", 2, "GND")
    assign(board, "C6", 1, "VBUS"); assign(board, "C6", 2, "GND")
    # KiCad diode footprint pad 1 = cathode (K), pad 2 = anode (A)
    assign(board, "D1", 1, "VDDH"); assign(board, "D1", 2, "VBUS")
    assign(board, "D2", 1, "VDDH"); assign(board, "D2", 2, "VBAT_SW")
    # KiCad LED footprint pad 1 = cathode (K), pad 2 = anode (A)
    assign(board, "LED1", 1, "GND"); assign(board, "LED1", 2, "LED_A")

    # --- Conthrough ---
    con = {1: "P0.10", 2: "P0.09", 3: "P1.00", 4: "P0.24", 5: "P0.22",
           6: "P0.20", 7: None, 8: None, 9: None, 10: None,
           11: "P0.08", 12: "P0.06", 13: "P0.26", 14: "P0.31",
           15: "P0.29", 16: "P0.02", 17: None, 18: "P1.13"}
    for n, net in con.items():
        assign(board, "J5", n, net)

    # Default design rules for the autorouter.
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = pcbnew.FromMM(0.15)
    ds.m_MinClearance = pcbnew.FromMM(0.15)
    ds.m_ViasMinSize = pcbnew.FromMM(0.6)
    ds.m_ViasMinDrill = pcbnew.FromMM(0.3)

    # Do not ask Freerouting to route GND; a copper pour will do that later.
    gnd_pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == "GND":
                gnd_pads.append((fp.GetReference(), p.GetNumber()))
                p.SetNet(None)

    pcbnew.SaveBoard(PCB, board)
    pcbnew.ExportSpecctraDSN(board, DSN)
    print("Exported", DSN)

    # Run Freerouting headless.
    cmd = FREEROUTING + ["-de", DSN, "-do", SES, "-mp", "50", "-mt", "1"]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # Import the routed session and restore the GND pads.
    board2 = pcbnew.LoadBoard(PCB)
    pcbnew.ImportSpecctraSES(board2, SES)
    gnd = board2.FindNet("GND")
    if gnd is None:
        gnd = pcbnew.NETINFO_ITEM(board2, "GND")
        board2.Add(gnd)
    for ref, num in gnd_pads:
        fp = board2.FindFootprintByReference(ref)
        if fp is not None:
            p = fp.FindPadByNumber(str(num))
            if p is not None:
                p.SetNet(gnd)
    pcbnew.SaveBoard(PCB, board2)
    print("Saved routed board", PCB)


if __name__ == "__main__":
    main()
