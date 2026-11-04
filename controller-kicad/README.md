# AKDK-compatible wireless controller board

Reverse-engineered from the `trackball-cs-2-akdk` repository data
(main-PCB controller footprint, case STL, ZMK `akdk_bt1` DTS, and the
Auto-KDK README).

## Board

- Size: 98.0 x 29.0 mm
- 2 layers, 1.6 mm thickness
- All components are on the **bottom side** (the side opposite the
  conthrough pads). Order JLCPCB PCBA with **Bottom side** assembly.
- Conthrough pads: 2 x 9, 1.27 mm pitch, 19.0 mm row spacing, on the top side.
- USB-C: 30.85 mm from the left edge, on the top edge. The left case opening
  is centred at x = -18.25 mm, z = -5.75 mm; the connector is horizontally
  centred in the opening. The 3D check shows the connector top is about
  0.17 mm above the case opening top; sand the opening by ~0.2 mm or lower the
  board by ~0.2 mm if it is tight.
- The same board is used for the right half by flipping it over (the main PCB
  SIDE1/SIDE2 variants are different net assignments, not different boards).

## Power / charger

- Li-Po 1S, 3.7 V, with protection circuit, PH 2-pin connector.
- TP4057 charger, 6.2 k PROG resistor (~193 mA).
- Power switch: DPDT. OFF grounds P0.13 (the Adafruit bootloader DFU pin) and
  disconnects the battery; USB then powers VDDH through a Schottky diode.
- Battery polarity: J2 pin 1 = +, pin 2 = -. Verify the battery lead polarity
  before plugging it in.

## Trackball FFC

The controller-side FFC connector is on the bottom side, while the trackball
module connector is on the opposite side. With a same-side FFC cable the pin
order is reversed. The controller board uses:

| Controller FFC pin | Signal |
|---|---|
| 1 | GND |
| 2 | SCLK (P0.12) |
| 3 | SDIO (P1.09) |
| 4 | MOTION (P0.15) |
| 5 | CS (P0.13) |
| 6 | 3.3 V |

The trackball module's own pinout is 1=3.3V, 2=CS, 3=MOTION, 4=SDIO, 5=SCLK,
6=GND. Verify the cable orientation before soldering/plugging.

## Bootloader / firmware

- The board uses the Adafruit nRF52 UF2 bootloader. Flash it once via SWD
  (J4, 2x5 1.27 mm header). The header is not in the JLCPCB BOM; hand-solder it
  or use pogo pads.
- After the bootloader is flashed, power switch OFF + USB enters the UF2
  bootloader. Copy the ZMK UF2 built from the `trackball-cs-2-akdk` repo.
- The E73-2G4M08S1C exposes all GPIOs used by the `akdk_bt1` DTS except P1.15
  (connector pad 17), which is unused by the firmware. No firmware change is
  required for the matrix/trackball mapping. The module's internal DC/DC is
  used; DCCH is left unconnected as in the E73 reference design.

## JLCPCB order

- Gerbers/drill: `controller_gerbers.zip`
- BOM: `jlcpcb_bom.csv`
- CPL: `jlcpcb_cpl.csv`
- PCB: 98 x 29 mm, 2 layers, 1.6 mm, HASL, default solder mask.
- PCBA: **Bottom side**. The BOM includes the JST PH battery connector and the
  ALPS DPDT switch (THT). JLCPCB THT assembly may be available; otherwise
  hand-solder those two parts. The SWD header J4 and the conthrough J5 are not
  in the BOM.
- All BOM LCSC parts were in stock at the time of writing:
  - C356849 E73-2G4M08S1C (472)
  - C165948 USB-C TYPE-C-31-M-12 (158981)
  - C725791 TP4057 (143683)
  - C131337 JST PH 2P (215233)
  - C202118 FH12-6S-0.5SH (2179)
  - C97434 ALPS SSSS820101 DPDT (2131)
  - C2986031 green LED (20891)
  - C2480 SS14 (1713221)
  - C23186 5.1k, C4260 6.2k, C22976 2M, C22935 1M, C21190 1k, C15849 1uF,
    C14663 0.1uF (all basic/stock)
- The CPL rotations are KiCad rotations. Check the JLCPCB placement preview;
  bottom-side rotations may need adjustment. The KiCad **Fabrication Toolkit**
  plugin can generate a JLCPCB-ready CPL if desired.

## DRC

- 0 unconnected items, 0 footprint errors.
- 6 courtyard overlaps remain (R3/J2, R4/D2, R5/C5/J3, C5/SW1). These are
  non-electrical; adjust the placement in KiCad if desired. The board is fully
  routed.

## Files

- `controller.kicad_pcb` — routed PCB
- `controller.kicad_sch` — block-diagram schematic (global-label connections)
- `controller.kicad_pro` — KiCad project
- `controller_gerbers.zip` — Gerbers + drill files
- `jlcpcb_bom.csv`, `jlcpcb_cpl.csv` — JLCPCB PCBA files
- `controller_sch.pdf`, `controller_pcb_front.pdf`, `controller_pcb_back.pdf`
- `controller.step` — 3D model for case/USB verification
- `scripts/` — generation/route/BOM scripts
