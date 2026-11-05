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

### Conthrough (KONSHU / コンスルー) mounting

The Conthrough used by this project is the 9-pin, 1.27 mm pitch, H2.5 mm
**through-hole** type (コンスルー 9ピン, 1.27 mm, 高さ2.5 mm). J5 is a 2 x 9
plated-through-hole footprint (0.7 mm drill, 1.1 mm pad, 1.27 mm pitch,
19.0 mm between rows) on the top side. Solder the Conthrough pins into these
holes.

- Hole/pad geometry: 0.7 mm finished hole, 1.1 mm pad, 1.27 mm pitch, 19.0 mm
  row spacing. The 1.1 mm pad leaves 0.17 mm between adjacent pads, above the
  0.1 mm clearance used by this board.
- The pads are plated through-holes, so the Conthrough is mechanically strong.
  Solder on the bottom side (all other components are also on the bottom).
- J5 is excluded from the JLCPCB BOM/CPL; it is a mechanical part. The board
  itself is ordered with the through-holes, so no extra drilling is needed.
- Board thickness is 1.6 mm. Conthrough H2.5 mm is designed for a 1.6 mm board
  plus a 0.9 mm gap; verify the gap to the main PCB after assembly.
- USB-C: 30.85 mm from the left edge, on the top edge. The left case opening
  is centred at x = -18.25 mm, z = -5.75 mm; the connector is horizontally
  centred in the opening. The 3D check shows the connector top is about
  0.17 mm above the case opening top; sand the opening by ~0.2 mm or lower the
  board by ~0.2 mm if it is tight.
- USB-C data: both plug orientations are supported. A6/B6 (D+) and A7/B7
  (D-) are tied with 0.4 mm via-in-pad and short F.Cu bridges. USB_DM is
  routed manually on F.Cu because Freerouting could not fit both data nets in
  the available corridor. Power, CC and charging also work in both
  orientations.
- The same board is used for the right half by flipping it over (the main PCB
  SIDE1/SIDE2 variants are different net assignments, not different boards).

## Power / charger

- Li-Po 1S, 3.7 V, with protection circuit, PH 2-pin connector.
- TP4057 charger, 6.2 k PROG resistor (~193 mA).
- Power switch: DPDT. OFF grounds P0.13 (the Adafruit bootloader DFU pin) and
  disconnects the battery; USB then powers VDDH through a Schottky diode.
- The E73 runs in **high-voltage mode**: VDDH is fed from the battery/USB
  through the Schottky diodes (D1/D2), and VDD is the module's internal 3.3 V
  LDO output (DC/DC disabled, DCCH unconnected). VDD and VDDH are **not**
  tied together on the board; the 3V3 rail is the module's VDD output.
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

- The board uses the Adafruit nRF52 UF2 bootloader. Flash it once via the
  solderless 6-pin 2.54 mm pogo test pads (J4). No header or extra parts are
  needed.
- Pogo pad mapping (pad 1 is the pad nearest the top edge; the row is on the
  left edge, 5 mm from the board edge, within the 25 mm clip depth):

  | Pogo pad | Signal | Pico H connection |
  |---|---|---|
  | 1 | VTref (3.3 V) | 3V3 (optional reference/power) |
  | 2 | SWDIO | GPIO3 |
  | 3 | SWCLK | GPIO2 |
  | 4 | GND | GND |
  | 5 | RESET (P0.18) | GPIO4 (optional) |
  | 6 | GND | GND |

  The Pico H runs the `debugprobe` firmware (SWCLK=GPIO2, SWDIO=GPIO3,
  RESET=GPIO4). Use female-female jumper wires from the Pico H header to the
  pogo clip. The clip clamps the left board edge; the 2.54 mm pitch pads are
  2.0 mm diameter with 0.54 mm gaps, so adjacent clip pins do not short.
- After the bootloader is flashed, power switch OFF + USB enters the UF2
  bootloader. Copy the ZMK UF2 built from the `trackball-cs-2-akdk` repo.
- The E73-2G4M08S1C exposes all GPIOs used by the `akdk_bt1` DTS except P1.15
  (connector pad 17), which is unused by the firmware. No firmware change is
  required for the matrix/trackball mapping. The module runs in high-voltage
  mode with its internal LDO; DCCH is left unconnected as in the E73 reference
  design.

## JLCPCB order

- Gerbers/drill: `controller_gerbers.zip`
- BOM: `jlcpcb_bom.csv`
- CPL: `jlcpcb_cpl.csv`
- PCB: 98 x 29 mm, 2 layers, 1.6 mm, HASL, default solder mask.
- PCBA: **Bottom side**. The BOM includes the JST PH battery connector and the
  ALPS DPDT switch (THT). JLCPCB THT assembly may be available; otherwise
  hand-solder those two parts. The pogo test pads J4 and the conthrough J5 are
  not in the BOM (J4 is bare copper; J5 is a THT mechanical part).
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

- `kicad-cli pcb drc --severity-error`: **0 violations, 0 unconnected pads,
  0 footprint errors**.
- Full-severity DRC still reports non-electrical warnings: 10 courtyard
  overlaps, silkscreen overlaps/clipping, and 15 dangling vias. These do not
  affect fabrication.
- The dense routing splits the B.Cu GND pour into islands. `scripts/stitch_zones.py`
  adds GND stitching vias so every island connects to the main GND; run it
  after `patch_pcb.py` when rebuilding. Skipping it leaves the ground pour
  split.
- The pogo test pads J4 are bare copper pads on the top side, 5 mm from the
  left edge, 2.54 mm pitch, 2.0 mm diameter. They are excluded from BOM/CPL.

## Rebuild

Run with the KiCad AppImage Python (see the scripts for the exact paths):

1. `generate_pcb.py`
2. `route_pcb.py` — assigns nets and imports `controller.ses`. The committed
   session is reused by default so the verified routing is reproducible. Set
   `REROUTE=1` to run Freerouting again; after a fresh route, run
   `export_ses.py` to freeze the new session.
3. `finish_pcb.py` — restores GND and adds the copper pours. Do not import the
   SES here again; `route_pcb.py` already did it.
4. `patch_pcb.py` — USB-C D+/D-, LED/P1.06, P0.12 stub, GND stitching.
5. `stitch_zones.py` — connects the remaining GND pour islands.

Then export Gerbers/drill, BOM/CPL, STEP and PDFs with `kicad-cli` and
`generate_bom_cpl.py`.

## Files

- `controller.kicad_pcb` — routed PCB
- `controller.kicad_sch` — block-diagram schematic (global-label connections)
- `controller.kicad_pro` — KiCad project
- `controller_gerbers.zip` — Gerbers + drill files
- `jlcpcb_bom.csv`, `jlcpcb_cpl.csv` — JLCPCB PCBA files
- `controller_sch.pdf`, `controller_pcb_front.pdf`, `controller_pcb_back.pdf`
- `controller.step` — 3D model for case/USB verification
- `scripts/` — generation/route/BOM scripts
