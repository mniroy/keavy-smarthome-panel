# KEAVY Smart Home Modular DIN-Rail & Standalone PLC Automation Platform

DRC-verified (0 violations, 0 unconnected items) industrial-grade DIN-Rail ESPHome & Home Assistant hardware ecosystem:

## 1. [`standalone/`](standalone/) — All-in-One 16-Channel LAN Relay Driver
- **Single-board `152.0 × 72.0 mm` (UM72 DIN-Rail)** exact replica of the 6-CH dimmer form factor.
- Built-in ESP32 DevKit + W5500 Ethernet LAN + `MCP23017` + `2× ULN2803G` + 16 status LEDs + 3.81mm screw terminals for **Omron G2R-1-E 24VDC NPN** relay modules.
- See [`standalone/README.md`](standalone/README.md).

## 2. [`modular/`](modular/) — Side-by-Side Chainable PLC Ecosystem (`KEAVY-BUS`, `DC3-10P`)
- Sized specifically to fit off-the-shelf DIN-Rail PLC enclosures (**SZOMK AK-P-08 `145×90×40mm`** & **AK-P-01 `115×90×40mm`**) as well as **UM72** carriers.
- Interconnected side-by-side via keyed, anti-reverse **Shrouded IDC Box Headers (`DC3-10P`, 2×5 2.54mm)** + standard `FC-10P` flat ribbon jumpers:
  - [`modular/brain/`](modular/brain/) — **KEAVY-BRAIN** (`120 × 72 mm`): ESP32 + W5500 LAN + 24V→5V Buck + `KEAVY-BUS` Master + Hot-Swap LDO & PTC
  - [`modular/relay_16ch/`](modular/relay_16ch/) — **KEAVY-RELAY16** (`96 × 72 mm`): 2500V Galvanic Isolated 16-CH NPN Relay Driver (`MCP23017` + `2× ULN2803G`, DIP `0x20–0x27`)
  - [`modular/dimmer_6ch/`](modular/dimmer_6ch/) — **KEAVY-DIMMER6** (`96 × 72 mm`): 2500V Galvanic Isolated 6-CH 60W/CH LED Dimmer (`PCA9685PW` + `6× AOD4184A`, DIP `0x40–0x47`)
  - [`modular/input_12a4/`](modular/input_12a4/) — **KEAVY-INPUT12A4** (`120 × 72 mm`): 12-CH Isolated Digital Inputs (Opto-Isolated 24V Dry/Wet) + 4-CH Industrial Analog Inputs (`ADS1115` 16-bit ADC, 0–10V / 4–20mA selectable)
- See [`modular/README.md`](modular/README.md).

## 3. [`PCB Design Rule/`](PCB%20Design%20Rule/) — Comprehensive PCB & EMI/EMC Design Guidelines
- Complete reference library covering:
  - `01-EMI-EMC-Certification-Rules.md`: Return paths, split-plane rules, certification checklists.
  - `02-Grounding-Return-Current-Stackup.md`: Star grounding, stitching vias, 2-layer and 4-layer stackups.
  - `03-Power-Integrity-Buck-Decoupling-Thermal.md`: SW node loop minimization, thermal vias, decoupling.
  - `04-High-Speed-Crystal-RF-Ethernet.md`: MII/RMII/SPI, differential impedance, isolation moat.
  - `05-Galvanic-Isolation-Creepage-Clearance-ESD.md`: IEC 60664-1 clearance/creepage, TVS diode layout.
  - `06-Routing-Geometry-DFM-DFA-JLCPCB.md`: Trace chamfering, acid traps, teardrops, SMD clearances.
  - `07-KEAVY-Project-Case-Study-and-Checklist.md`: Implementation record and DRC verification summary.
- See [`PCB Design Rule/README.md`](PCB%20Design%20Rule/README.md).
