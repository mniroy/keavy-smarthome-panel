# 07 — Studi Kasus Proyek KEAVY, Master Pre-Fab Checklist & Daftar Pustaka

Dokumen ini merangkum seluruh penerapan nyata aturan desain PCB pada **5 board dalam repositori KEAVY Smart Home Panel**, daftar periksa wajib sebelum mengirim Gerber ke pabrik, serta referensi otoritatif.

---

## 1. Studi Kasus Penerapan Nyata pada 5 Board KEAVY

| Board | Dimensi & Casing | Masalah Awal yang Ditemukan Saat Audit | Perbaikan Nyata yang Diterapkan | Status DRC |
| :--- | :--- | :--- | :--- | :-: |
| **`KEAVY-BRAIN` REV 2.0** | `120 × 72 mm` (SZOMK AK-P-08) | • Bus 3.3V menumpang di ESP32 (risiko brownout saat hot-plug)<br>• Crystal 25MHz W5500 tanpa load cap 18pF & tanpa 100nF lokal W5500<br>• Buck `XL1509` tanpa keramik HF di hot loop & tanpa `C_EMI` di input 24V<br>• `BUS_INT` belum ada damping resistor 47Ω<br>• Belum ada perimeter GND stitching & masih banyak belokan 90° | • Dedicated LDO `AMS1117-3.3` (`U5_BUS`) + Dual PTC `500mA` (`F_5V`, `F_3V3`)<br>• Tambah `C_Y1`, `C_Y2` (18pF) + `C_W55` (100nF) + SPI GND return vias<br>• Tambah `C_BIN` (100nF 50V) di pin `U1` + `C_EMI` (100nF 50V) di `J1`<br>• Tambah `R_DINT` (47Ω) melengkapi `R_DSDA`/`R_DSCL` + `USBLC6-2SC6`<br>• *Faraday-cage perimeter GND stitching* + *45° chamfering* + `ANTENNA KEEP-OUT` | **0 Errors / 0 Unconn** |
| **`KEAVY-RELAY16` REV 2.0** | `96 × 72 mm` (SZOMK AK-P-01) | • Risiko ground loop arus 24V ke bus I2C<br>• `GND_ISO` pour terlalu dekat (0.4 mm) ke domain `KEAVY-BUS`<br>• `ADuM1250ARZ` belum punya bypass `100nF` wajib di kedua sisi<br>• Input 24V belum ada filter HF keramik `100nF` | • Isolasi galvanik penuh 2500 Vrms (`ADuM1250ARZ` + `B0505S-1W`)<br>• **True Isolation Moat** (`add_zone_keepout`) memisahkan total `GND_BUS` & `GND_ISO`<br>• Tambah `C_ISO1` & `C_ISO2` (100nF) tepat di pad `U_ISO` + `C1_HF` (100nF 50V)<br>• *Perimeter GND_ISO stitching* + *45° chamfering* | **0 Errors / 0 Unconn** |
| **`KEAVY-DIMMER6` REV 2.0** | `96 × 72 mm` (SZOMK AK-P-01) | • Risiko ground loop arus tinggi 15A PWM ke ESP32<br>• `GND_ISO` pour melintasi bawah `ADuM1250` & `B0505S-1W`<br>• Belum ada bypass `C_ISO1`/`C_ISO2` 100nF pada `U_ISO` | • Isolasi galvanik 2500 Vrms (`ADuM1250ARZ` + `B0505S-1W`) + **True Isolation Moat**<br>• Tambah `C_ISO1` & `C_ISO2` (100nF) + *F.Cu* +24V high-current pour (`AOD4184A` + `SS34`)<br>• *Perimeter GND_ISO stitching* + *45° chamfering* | **0 Errors / 0 Unconn** |
| **`KEAVY-INPUT12A4` REV 2.0** | `96 × 72 mm` (SZOMK AK-P-01) | • Kebutuhan baca 12 saklar dinding 24V (rawan induksi 220V) + 4 sensor analog 0–10V tanpa ground loop dan respon < 2 ms | • `3× TLP281-4` (3750 Vrms isolasi opto) + 6.3mA *wetting current* (`3.3k` 1206) + 12 LED seri + 12× `100nF` debounce<br>• `MCP23017` `INTA+INTB` ke Pin 10 `BUS_INT` (hardware interrupt)<br>• `TI ADS1115` 16-bit + divider `22k/10k 1%` + `100nF` RC + **Zener `BZT52C3V3`** tahan 24V<br>• **True 3750V Isolation Moat** + *perimeter GND stitching* + *45° chamfering* | **0 Errors / 0 Unconn** |
| **`Standalone 16-CH`** | `155 × 72 mm` (All-in-One) | • Sama seperti audit awal `KEAVY-BRAIN` (crystal load caps, W5500 decoupling, buck hot-loop, 90° bends, stitching vias) | • Seluruh upgrade sertifikasi (`C_Y1`/`C_Y2` 18pF, `C_W55`, `C_BIN`, `C_EMI`, SPI GND return vias, *perimeter stitching*, *45° chamfering*) diterapkan penuh | **0 Errors / 0 Unconn** |

---

## 2. Master Checklist Pre-Fabrikasi (Wajib Cek Sebelum Order PCB)

### A. Integritas Elektrik & DRC
- [ ] **KiCad DRC:** `0 Violations` (Error & Warning) dan `0 Unconnected Items`.
- [ ] Seluruh *copper zone* sudah di-**Refill** sebelum ekspor Gerber.
- [ ] Tidak ada *floating copper island* (pulau tembaga tak terhubung GND).
- [ ] Periksa ulang pinout IC kritis terhadap datasheet asli (khususnya orientasi Pin 1 `SOIC`, `SOP-16`, `MSOP-10`, `SOT-223`, `TO-252`, dan polaritas dioda/LED/elko).

### B. EMI / EMC & Sertifikasi
- [ ] **Kabel Keluar:** Semua konektor eksternal punya filter (`C_EMI` / ferrite / magnetics) dan/atau proteksi ESD (*straight-through* TVS tepat di tepi konektor).
- [ ] **Solid Ground Plane:** Tampilkan layer `B.Cu` (atau `L2` GND) sendirian — pastikan **tidak ada celah/slot** di bawah SPI, clock, Ethernet, atau USB.
- [ ] **Switching Regulator:** Keramik `100nF` menempel rapat di `VIN`/`GND`, node `SW` seminimal mungkin, jalur `FB` jauh dari induktor.
- [ ] **Crystal & RF:** Load capacitor (`18pF`) terpasang rapat di crystal, tidak ada jalur daya lewat bawah crystal, dan *Antenna Keep-Out* ESP32 kosong total di semua layer.
- [ ] **Isolasi Galvanik:** *Isolation moat* bebas tembaga di bawah `ADuM1250`, `B0505S-1W`, `TLP281-4`, serta kapasitor `100nF` terpasang di kedua sisi isolator.
- [ ] **Stitching Vias:** Barisan *perimeter ground stitching vias* & *return vias* di dekat klaster via sinyal cepat sudah terpasang.

### C. DFM / DFA & Manufaktur (JLCPCB)
- [ ] Semua belokan jalur menggunakan sudut **45°** (tidak ada *acid trap* < 90°).
- [ ] Lebar trace, clearance, ukuran bor via ($\ge 0.30$ mm), dan jarak ke tepi papan ($\ge 0.5$ mm) sesuai kapabilitas standar JLCPCB.
- [ ] Teks silkscreen minimal tinggi `0.80 mm`, tidak menimpa pad/lubang bor, dan polaritas (`+`, `-`, `COM`, `1..16`, `A1..A4`) jelas di sisi atas & bawah.
- [ ] File **Gerber ZIP + Excellon Drill + BOM CSV (dengan LCSC Part #) + CPL CSV** sudah dicek visual di Gerber Viewer / JLCPCB DFM Preview (pastikan rotasi IC di CPL sesuai *pin-1 orientation* JLCPCB!).

---

## 3. Daftar Pustaka & Sumber Otoritatif

1. **Predictable Designs (John Teel):** [*11 PCB Design Rules to NEVER Break or You'll Fail Certification*](https://predictabledesigns.com/pcb-certification-rules-never-break/)
2. **Texas Instruments:**
   - *SZZA009 — PCB Design Guidelines For Reduced EMI* (ti.com)
   - *SCAA082 — High-Speed Layout Guidelines* (ti.com)
   - *SLVAER0C / SLVA157 — DC/DC Converter PCB Layout Guidelines* (ti.com)
   - *SLVA680 — ESD Packaging and Layout Guide* (ti.com)
3. **Analog Devices:** [*ADuM1250 / ADuM1251 Hot-Swappable Dual I2C Isolator Datasheet & iCoupler PCB Layout Guidelines*](https://www.analog.com/en/products/adum1250.html)
4. **Espressif Systems:** [*ESP32 Hardware Design Guidelines (PCB Layout, Antenna Keep-Out, Crystal, Power)*](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/)
5. **WIZnet:** [*W5500 Hardware Design Guide (Differential Pairs, Magnetics, Crystal, EXRES1)*](https://docs.wiznet.io/Product/iEthernet/W5500/Application/hardware-design-guide)
6. **Semtech:** *IEC 61000-4-2 ESD Protection & Flow-Through PCB Layout Application Notes* (semtech.com)
7. **Henry W. Ott:** *Electromagnetic Compatibility Engineering* (John Wiley & Sons, ISBN 978-0-470-18930-6)
8. **Rick Hartley:** *Proper Grounding and Return Current Paths in High-Speed PCBs* (AltiumLive / IEEE EMC Society)
9. **IPC Standards:**
   - *IPC-2221B — Generic Standard on Printed Board Design*
   - *IPC-2152 — Standard for Determining Current-Carrying Capacity in Printed Board Design*
10. **IEC Safety Standards:**
    - *IEC 62368-1 — Audio/Video, Information and Communication Technology Equipment Safety Requirements*
    - *IEC 60664-1 — Insulation Coordination for Equipment Within Low-Voltage Supply Systems*
    - *IEC 61000-4-2 — Electrostatic Discharge (ESD) Immunity Test*
11. **JLCPCB:** [*PCB Manufacturing & SMT Assembly Capabilities*](https://jlcpcb.com/capabilities/pcb-capabilities)
