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
  (D-) are tied with 0.4/0.2 mm via-in-pad and short F.Cu bridges. USB_DM is
  routed manually on F.Cu because Freerouting could not fit both data nets in
  the available corridor. Power, CC and charging also work in both
  orientations. The data vias are inside the 0.3 mm pads; see the JLCPCB
  via-in-pad note below.
- The same board is used for the right half by flipping it over (the main PCB
  SIDE1/SIDE2 variants are different net assignments, not different boards).

## Power / charger

- Li-Po 1S, 3.7 V, with protection circuit, PH 2-pin connector.
- MCP73831 4.2 V single-cell charger (LCSC C14879), 6.2 k PROG resistor
  (~160 mA). The TP4057 was replaced because its 4.24 V termination is above
  the usual 4.20 V Li-Po limit. The charger footprint is a 5-pad SOT-23-5 land
  pattern; PROG is pad 5.
- Charger bypass capacitors: C6 = 10 uF on VBUS and C7 = 10 uF on VBAT
  (LCSC C19702, 0603, 10 V). This meets the MCP73831 4.7 uF recommendation
  with margin; check the selected part's DC-bias curve at 5 V/4.2 V. C7 is
  placed next to U2 and connected to VBAT with a short B.Cu trace.
- Power switch: DPDT. OFF grounds P0.13 and disconnects the battery; USB then
  powers VDDH through a Schottky diode. Grounding P0.13 is the DFU pin only on
  bootloader builds that use it; see the bootloader section.
- The E73 runs in **high-voltage mode**: VDDH is fed from the battery/USB
  through the Schottky diodes (D1/D2), and VDD is the module's internal 3.3 V
  LDO output (DC/DC disabled, DCCH unconnected). VDD and VDDH are **not**
  tied together on the board; the 3V3 rail is the module's VDD output.
- Battery polarity: J2 pin 1 = +, pin 2 = -. Verify the battery lead polarity
  before plugging it in.
- A blank E73 has REGOUT0 = 1.8 V, so VDD (the 3V3 rail) is 1.8 V until the
  UICR is programmed. After the bootloader/firmware sets REGOUT0 to 3.3 V,
  verify 3.3 V on C3 before connecting the trackball FFC.
- **Battery operation / REG0 dropout**: VDDH = VBAT minus the D2 Schottky
  drop. REG0 regulates 3.3 V only while VDDH is at least about 3.6 V; below
  that it is in dropout and the 3V3 rail follows VDDH (roughly 2.6-3.0 V at
  the battery cutoff). The nRF52840 itself remains within its 1.8-3.6 V
  supply range, and the trackball module's 1.8 V sensor supply should remain
  in regulation, but the 3.3 V rail is not regulated. Measure VDDH/VDD at the
  battery low-voltage cutoff and check the trackball module's minimum VDDIO.
  If the module requires a regulated 3.3 V, add a boost converter (or use a
  higher-voltage supply); otherwise the existing high-voltage/LDO mode is
  acceptable.

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
- **First SWD connection / REGOUT0**: A blank nRF52840/E73 has
  REGOUT0 = 1.8 V, so VDD and the SWD pins are at 1.8 V. A 3.3 V probe can
  overdrive them. Use a debugger with VTref sensing and level shifting, or a
  1.8 V-compatible probe, for the first write. J4 pad 1 is the target VDD
  sense point; do **not** connect the Pico's 3V3 output to it. For a
  Pico-based first write, use a bidirectional level shifter (e.g., TXS0102
  or 74LVC2T45) with VCCA = J4 pad 1 (1.8 V) and VCCB = Pico 3V3, common GND.
- Flash a bootloader build that defines `UICR_REGOUT0_VALUE = 3V3` (for
  example the nice_nano or pillbug build). The bootloader sets REGOUT0 and
  resets; verify 3.3 V on C3. If the chosen build does not set REGOUT0,
  program it via SWD/UICR before using 3.3 V logic. After that, the Pico 2 WH
  3.3 V SWD signals are safe.
- Pogo pad mapping (pad 1 is the pad nearest the top edge; the row is on the
  left edge, 5 mm from the board edge, within the 25 mm clip depth):

  | Pogo pad | Signal | Pico 2 WH connection |
  |---|---|---|
  | 1 | VTref (module VDD sense) | debugger VTref; not Pico 3V3 |
  | 2 | SWDIO | GP3 (level-shifted for the first 1.8 V write) |
  | 3 | SWCLK | GP2 (level-shifted for the first 1.8 V write) |
  | 4 | GND | GND |
  | 5 | RESET (P0.18) | optional; not GP4 by default |
  | 6 | GND | GND |

  The Pico H/2 WH runs the `debugprobe` firmware (SWCLK=GPIO2, SWDIO=GPIO3).
  GP4 is not a guaranteed reset output in all debugprobe builds; leave pad 5
  open unless your probe provides a reset output. Use female-female jumper
  wires; the clip clamps the left board edge, and the 2.54 mm pitch pads are
  2.0 mm diameter with 0.54 mm gaps, so adjacent clip pins do not short.
- **DFU entry**: The power switch OFF grounds P0.13, but that is the DFU
  button only on bootloader builds that define `BUTTON_DFU = P0.13`. The
  nice_nano build has no DFU button and uses the 1200-baud touch instead. If
  OFF + USB does not enter UF2, use the 1200-baud touch (or the reset pad)
  rather than assuming P0.13 works.
- After the bootloader is flashed, copy the ZMK UF2 built from the
  `trackball-cs-2-akdk` repo.
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
  - C14879 MCP73831 (4.2 V charger, in stock)
  - C19702 10uF 0603 10V (C6/C7 charger bypass, in stock)
  - C131337 JST PH 2P (215233)
  - C202118 FH12-6S-0.5SH (2179)
  - C97434 ALPS SSSS820101 DPDT (2131)
  - C2986031 green LED (20891)
  - C2480 SS14 (1713221)
  - C23186 5.1k, C4260 6.2k, C22976 2M, C22935 1M, C21190 1k, C15849 1uF,
    C14663 0.1uF (all basic/stock)
- **Via-in-pad**: the USB-C D+/D- pads still use 0.4/0.2 mm via-in-pad.
  Moving them outside the 0.3 mm pads conflicts with the CC1/CC2 fan-out, so
  the verified geometry is kept. For the 2-layer JLCPCB order, select the
  **Via in Pad** option (resin-filled and copper-capped, IPC-4761 Type VII)
  and confirm the price/availability; if it is unavailable, the USB-C vias
  must be moved. The P1.06 vias have been moved outside the U1/R6 pads, so
  only the USB-C vias need the special process.
- The CPL rotations are KiCad rotations. Check the JLCPCB placement preview;
  bottom-side rotations may need adjustment. The KiCad **Fabrication Toolkit**
  plugin can generate a JLCPCB-ready CPL if desired.

## DRC

- `kicad-cli pcb drc --severity-error`: **0 violations, 0 unconnected pads,
  0 footprint errors**.
- Run `scripts/set_drc_severity.py` after the PCB pipeline: KiCad rewrites
  the project when a board is saved, which resets courtyard overlaps to
  error. The script keeps them as warnings.
- Full-severity DRC still reports non-electrical warnings: 11 courtyard
  overlaps (bounding boxes; check the 3D preview), silkscreen overlaps/
  clipping, and 15 GND stitching vias that connect only to one pour. The
  stitching vias are intentional; they are not electrically dangling. The
  C7/J1 and C2/U1 overlaps are courtyard-only warnings: the USB-C body ends
  below C7, and C2's body ends at 80.2 mm while the E73 body starts at
  80.5 mm. C2 pad 1 overlaps the U1 VDDH pad by design (same net).
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
4. `patch_pcb.py` — USB-C D+/D-, LED/P1.06, C7 VBAT, P0.12 stub, GND stitching.
5. `stitch_zones.py` — connects the remaining GND pour islands.
6. `set_drc_severity.py` — keeps courtyard overlaps as warnings before the
   final DRC report.
7. `update_lcsc.py` is optional; it refreshes the LCSC fields from the table
   above (U2=MCP73831/C14879, C6/C7=C19702).

Then run `kicad-cli pcb drc --severity-error`, and export Gerbers/drill,
BOM/CPL, STEP and PDFs with `kicad-cli` and `generate_bom_cpl.py`.

## Files

- `controller.kicad_pcb` — routed PCB
- `controller.kicad_sch` — block-diagram schematic (global-label connections)
- `controller.kicad_pro` — KiCad project
- `controller_gerbers.zip` — Gerbers + drill files
- `jlcpcb_bom.csv`, `jlcpcb_cpl.csv` — JLCPCB PCBA files
- `controller_sch.pdf`, `controller_pcb_front.pdf`, `controller_pcb_back.pdf`
- `controller.step` — 3D model for case/USB verification
- `controller.pretty/MCP73831_SOT-23-5.kicad_mod` — 5-pad charger footprint (PROG=pad 5)
- `controller.3dshapes/SOT-23-5.wrl`, `controller.3dshapes/SOT-23-5.step`
- `scripts/` — generation/route/BOM/DRC scripts
