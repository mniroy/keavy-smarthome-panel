# Project Brief: 24V DC 16-Channel LAN Relay Driver (NPN Sinking — REV 1.1 DIN)

## 1. Ringkasan & Tujuan Proyek
Replikasi fisik & arsitektur inti secara persis dari proyek **24V DC 6-Channel LED Dimmer (`152.0 mm × 72.0 mm`, profil UM72 DIN-Rail, LAN W5500, ESP32 DevKit 30-Pin modular)**, dengan fungsi output **16-Channel NPN Relay Driver** menggunakan **MCP23017 (I2C 16-bit I/O Expander)** + **2× ULN2803G (`ULN2803G-S18-R` SOP-18)** untuk mengontrol modul relay industri **16-Channel (atau 2× 8-Channel) 24VDC NPN (Omron G2R-1-E PLC Control)**.

## 2. Parameter Kunci & Spesifikasi Sistem

| Parameter | Spesifikasi Terpilih | Catatan Teknis |
|---|---|---|
| **Revisi & Tanggal Desain** | `REV 1.1 DIN` (`2026-11-21`) | Branding logo **KEAVY Instruments** di pojok kanan atas PCB |
| **Dimensi & Mounting PCB** | **`152.0 mm × 72.0 mm`**, 2-Layer FR4 | Identik 100% dengan dimmer 6CH (**UM72 DIN-Rail** + 4x M3 `3.2mm`) |
| **Orientasi Port (DIN-Rail)** | **Atas**: `RJ45 LAN`, `24V IN (5.08mm)`<br>**Bawah**: `USB-C`, `J2 (PWR 3.81mm)`, `J3 (CH1–8)`, `J4 (CH9–16)` | Sisi Kiri & Kanan bebas konektor (bisa dipasang rapat berdampingan) |
| **I/O Expander** | **MCP23017-E/SO** (`SOIC-28W`, I2C `0x20`) | Kontrol via `SDA=GPIO21`, `SCL=GPIO22` + pull-up `4.7k`, Hi-Z saat boot (bebas relay chatter) |
| **Driver Relay 16-Channel** | **2× ULN2803G (`ULN2803G-S18-R` SOP-18)** | `U5` (CH1–CH8) & `U6` (CH9–CH16), `50V / 500mA/ch`, internal clamp diode (`COM` → `+24V_BUS`) |
| **Target Beban Relay** | **Omron G2R-1-E 16-CH / 2× 8-CH 24VDC NPN** | ~21.8 mA per koil relay (`~350 mA` total jika 16 relay aktif bersamaan) |
| **Indikator Status Channel** | 16× SMD LED Hijau (`LED1`–`LED16`) + `RL1`–`RL16` (`10k`) | Sejajar langsung di atas terminal `CH1`–`CH16` |
| **Konektor Output** | Screw Terminal Block **3.81mm** (`J2` 2-pin + `J3` 8-pin + `J4` 8-pin) | Tersedia output `+24V/GND` terproteksi untuk langsung menyuplai modul relay |
| **Konektivitas & Daya** | **W5500 + HR911105A**, **XL1509-5.0**, **AMS1117-3.3**, **AOD403**, **5A Fuse**, **SMBJ28A** | Identik dengan arsitektur inti dimmer 6CH |

## 3. Verifikasi DRC & File Proyek
- **KiCad 10 PCB**: [relay_16ch.kicad_pcb](file:///Users/royyanwicaksono/Dev/PCB/DC%2024%208%20CH%20relay%20driver/relay_16ch.kicad_pcb) (`0 violations`, `0 unconnected items`)
- **Generator Script**: [generate_pcb.py](file:///Users/royyanwicaksono/Dev/PCB/DC%2024%208%20CH%20relay%20driver/generate_pcb.py)
- **Firmware ESPHome**: [firmware/relay_16ch.yaml](file:///Users/royyanwicaksono/Dev/PCB/DC%2024%208%20CH%20relay%20driver/firmware/relay_16ch.yaml)
- **JLCPCB Export Script**: [manufacturing/export_jlcpcb.py](file:///Users/royyanwicaksono/Dev/PCB/DC%2024%208%20CH%20relay%20driver/manufacturing/export_jlcpcb.py)
