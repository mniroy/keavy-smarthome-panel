# KEAVY Modular DIN-Rail PLC Ecosystem (REV 2.0 — Industrial Galvanic Isolation & Hot-Swap Bus)

A modular, side-by-side chainable **DIN-Rail Smart Automation Ecosystem** built for **ESPHome** and **Home Assistant**, sized to fit off-the-shelf **PLC DIN-Rail Enclosures** (`SZOMK AK-P-08` & `AK-P-01`) as well as open **UM72 (72mm)** DIN-Rail carriers.

---

## REV 2.0 Industrial Upgrades

1. **Full 2500 Vrms Galvanic Isolation (`ADuM1250ARZ` + `B0505S-1W`) on Every Slave Module**:
   - **Zero Ground Loop**: Bus ground (`GND_BUS`) and 24V high-current power ground (`GND_ISO`) are **100% electrically separated** on both `KEAVY-RELAY16` and `KEAVY-DIMMER6`.
   - **Isolated Power**: Each slave uses a `B0505S-1W` (5V→5V 1W isolated DC-DC) + local `AMS1117-3.3` (`+3V3_ISO`) to power its `MCP23017` / `PCA9685PW` and `ADuM1250ARZ` Side 2.
   - **Isolated Bidirectional I²C**: `ADuM1250ARZ` (pin-compatible with `ISO1540DR` / `CA-IS3020S`) isolates `SDA` & `SCL` up to 2500 Vrms with dedicated `4.7kΩ` pull-ups on the isolated side.
2. **Hot-Swap & Short-Circuit Protection on `KEAVY-BRAIN`**:
   - **Dedicated Bus LDO (`U5_BUS`, `AMS1117-3.3`)**: `+3V3_BUS` is generated independently from the ESP32 DevKit's internal 3.3V regulator — hot-plugging or shorting a slave module will **not** brownout or reset the ESP32.
   - **Dual 500mA SMD PTC Polyfuses (`F_5V`, `F_3V3`)**: Auto-resetting overcurrent protection on both `+5V_BUS` and `+3V3_BUS`.
3. **EMI & ESD Hardening for Relay/Contactor Panels**:
   - **EMI-Shielded `DC3-10P` Pinout**: `GND_BUS` (Pin 8) physically separates `I2C_SDA` (Pin 7) from `I2C_SCL` (Pin 9) inside the 10-pin IDC ribbon cable.
   - **Strong `2.2kΩ` Pull-Ups + `47Ω` Series Damping Resistors** (`R_DSDA`, `R_DSCL`) + **`USBLC6-2SC6` ESD TVS Diode** (`D_ESD`) right at the `J_BUS_OUT` connector.
   - **100 kHz I²C Bus Clock** configured in [`firmware/keavy_modular.yaml`](firmware/keavy_modular.yaml) for maximum noise margin.

---

## System Architecture (`KEAVY-BUS` REV 2.0)

```
┌───────────────────────────┐   DC3-10P IDC    ┌────────────────────────┐   DC3-10P IDC    ┌────────────────────────┐
│     KEAVY-BRAIN V2.0      │ ═══════════════▶ │   KEAVY-RELAY16 V2.0   │ ═══════════════▶ │   KEAVY-DIMMER6 V2.0   │
│  120.0 × 72.0 mm          │  (Hot-Swap Bus)  │   96.0 × 72.0 mm       │  (Hot-Swap Bus)  │   96.0 × 72.0 mm       │
│  ESP32 + W5500 + U5_BUS   │                  │  2500V ISO (ADuM1250 + │                  │  2500V ISO (ADuM1250 + │
│  2×500mA PTC + USBLC6 ESD │                  │  B0505S) + MCP23017 +  │                  │  B0505S) + PCA9685 +   │
│  Fits: AK-P-08 / UM72     │                  │  2×ULN2803G (16-CH)    │                  │  6×AOD4184A (60W/CH)   │
└───────────────────────────┘                  └────────────────────────┘                  └────────────────────────┘
```

### Modules Included (All 0 DRC Violations, 0 Unconnected Items)

| Module | PCB Size | Market PLC Casing Fit | Function | Addressing / Scalability |
|---|---|---|---|---|
| **KEAVY-BRAIN** | `120.0 × 72.0 mm` | **SZOMK AK-P-08** (`145×90×40mm`) & **UM72** | ESP32 DevKit + W5500 LAN + RJ45 + 24V→5V Buck (`XL1509-5.0`) + Dedicated `U5_BUS` 3.3V + Dual `500mA PTC` + `USBLC6-2SC6` ESD | 1 Brain per bus (1 Ethernet cable) |
| **KEAVY-RELAY16** | `96.0 × 72.0 mm` | **SZOMK AK-P-01** (`115×90×40mm`) & **UM72** | **2500Vrms Isolated** 16-CH 24VDC NPN Relay Driver (`B0505S-1W` + `ADuM1250ARZ` + `MCP23017` + `2× ULN2803G`) for Omron G2R-1-E | 3-bit DIP `SW1`: `0x20`–`0x27` (up to **8 boards = 128 relays**) |
| **KEAVY-DIMMER6** | `96.0 × 72.0 mm` | **SZOMK AK-P-01** (`115×90×40mm`) & **UM72** | **2500Vrms Isolated** 6-CH 60W/CH LED Dimmer (`B0505S-1W` + `ADuM1250ARZ` + `PCA9685PW` 1.526kHz + `6× AOD4184A`, 15A fuse) | 3-bit DIP `SW1`: `0x40`–`0x47` (up to **8 boards = 48 dimmers**) |

### Standardized 10-Pin `KEAVY-BUS` REV 2.0 (`DC3-10P` Shrouded Keyed IDC Header)

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| **1** | `+5V_BUS` (500mA PTC) | **2** | `+5V_BUS` (500mA PTC) |
| **3** | `GND_BUS` | **4** | `GND_BUS` |
| **5** | `+3V3_BUS` (Dedicated LDO + 500mA PTC) | **6** | `GND_BUS` (Shield) |
| **7** | `I2C_SDA` (`GPIO21`, 47Ω + ESD) | **8** | `GND_BUS` **(EMI Shield between SDA & SCL)** |
| **9** | `I2C_SCL` (`GPIO22`, 47Ω + ESD) | **10** | `BUS_INT` (`GPIO16`) |

*(High-current 24V coil/LED power is fed separately to each slave module's own `J1` 24V terminal block, with `GND_ISO` 100% galvanically isolated from `GND_BUS`.)*

---

## Firmware & Manufacturing Files

- **Unified ESPHome Config (100 kHz I²C)**: [`firmware/keavy_modular.yaml`](firmware/keavy_modular.yaml)
- **JLCPCB Packages** (Gerber ZIP + BOM with LCSC Part # + CPL):
  - `brain/manufacturing/jlcpcb/`
  - `relay_16ch/manufacturing/jlcpcb/`
  - `dimmer_6ch/manufacturing/jlcpcb/`
