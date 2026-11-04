#!/usr/bin/env python3
"""Update LCSC part fields / values on the routed PCB."""
import os
import pcbnew

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(HERE, "controller.kicad_pcb")

UPDATES = {
    "R1": ("5.1k", "C23186"),
    "R2": ("5.1k", "C23186"),
    "R3": ("6.2k", "C4260"),
    "R4": ("2M", "C22976"),
    "R5": ("1M", "C22935"),
    "R6": ("1k", "C21190"),
    "C1": ("1uF", "C15849"),
    "C2": ("0.1uF", "C14663"),
    "C3": ("1uF", "C15849"),
    "C5": ("0.1uF", "C14663"),
    "C6": ("1uF", "C15849"),
    "D1": ("SS14", "C2480"),
    "D2": ("SS14", "C2480"),
    "LED1": ("Green", "C2986031"),
    "U1": ("E73-2G4M08S1C", "C356849"),
    "U2": ("TP4057", "C725791"),
    "J1": ("USB-C", "C165948"),
    "J2": ("Battery PH2", "C131337"),
    "J3": ("FFC 6P 0.5mm", "C202118"),
    "SW1": ("DPDT", "C97434"),
}


def main():
    board = pcbnew.LoadBoard(PCB)
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in UPDATES:
            value, lcsc = UPDATES[ref]
            fp.SetValue(value)
            fp.SetField("LCSC Part", lcsc)
    pcbnew.SaveBoard(PCB, board)
    print("Updated LCSC fields")


if __name__ == "__main__":
    main()
