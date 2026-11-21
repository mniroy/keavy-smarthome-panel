# KEAVY 24V DC DIN-Rail Relay & Dimmer Automation Platform

This repository contains two complete, DRC-verified (0 violations, 0 unconnected items) DIN-Rail ESPHome hardware architectures:

## 1. [`standalone/`](standalone/) — All-in-One 16-Channel LAN Relay Driver
- **Single-board `152.0 × 72.0 mm` (UM72 DIN-Rail)** exact replica of the 6-CH dimmer form factor.
- Built-in ESP32 DevKit + W5500 Ethernet LAN + `MCP23017` + `2× ULN2803G` + 16 status LEDs + 3.81mm screw terminals for **Omron G2R-1-E 24VDC NPN** relay modules.
- See [`standalone/README.md`](standalone/README.md).

## 2. [`modular/`](modular/) — Side-by-Side Chainable PLC Ecosystem (`KEAVY-BUS`, `DC3-10P`)
- Sized specifically to fit off-the-shelf DIN-Rail PLC enclosures (**SZOMK AK-P-08 `145×90×40mm`** & **AK-P-01 `115×90×40mm`**) as well as **UM72** carriers.
- Interconnected side-by-side via keyed, anti-reverse **Shrouded IDC Box Headers (`DC3-10P`, 2×5 2.54mm)** + standard `FC-10P` flat ribbon jumpers:
  - [`modular/brain/`](modular/brain/) — **KEAVY-BRAIN** (`120 × 72 mm`): ESP32 + W5500 LAN + 24V→5V Buck + `KEAVY-BUS` Master
  - [`modular/relay_16ch/`](modular/relay_16ch/) — **KEAVY-RELAY16** (`96 × 72 mm`): 16-CH NPN Relay Driver (`MCP23017` + `2× ULN2803G`, DIP `0x20–0x27`)
  - [`modular/dimmer_6ch/`](modular/dimmer_6ch/) — **KEAVY-DIMMER6** (`96 × 72 mm`): 6-CH 60W/CH LED Dimmer (`PCA9685PW` + `6× AOD4184A`, DIP `0x40–0x47`)
- See [`modular/README.md`](modular/README.md).
