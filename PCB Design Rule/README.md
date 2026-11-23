# PCB Design Rule & Best Practices Knowledge Base

Direktori ini berisi panduan komprehensif standar industri untuk desain PCB yang **andal, lolos uji EMI/EMC & sertifikasi (FCC/CE/IEC), bebas cacat manufaktur (DFM/DFA), dan siap produksi massal (JLCPCB/SMT)**.

Seluruh aturan dirangkum dari sumber-sumber otoritatif industri elektronika (**Predictable Designs / John Teel, Texas Instruments, Analog Devices, Espressif Systems, WIZnet, Semtech, Henry Ott, Rick Hartley, IPC-2221B/IPC-2152, IEC 62368-1, JLCPCB**) serta pengalaman rekayasa nyata dari sistem panel smarthome industrial **KEAVY Modular DIN-Rail**.

---

## Daftar Panduan

| No. | File | Fokus Materi |
| :-: | :--- | :--- |
| **01** | [01-EMI-EMC-Certification-Rules.md](./01-EMI-EMC-Certification-Rules.md) | 11 Aturan Wajib Sertifikasi PCB (Predictable Designs), Radiated vs Conducted Emissions, Cable Filtering, Slew-Rate Control, & Connector Placement. |
| **02** | [02-Grounding-Return-Current-Stackup.md](./02-Grounding-Return-Current-Stackup.md) | Fisika *Return Current* (Rick Hartley & Henry Ott), Solid Ground Plane, Mixed-Signal Partitioning, Layer-Transition Return Vias, Faraday-Cage Perimeter Stitching, & Stack-up 2/4 Layer. |
| **03** | [03-Power-Integrity-Buck-Decoupling-Thermal.md](./03-Power-Integrity-Buck-Decoupling-Thermal.md) | Switching Regulator *Hot Loop* (Buck Converter), Filter Input Daya, Strategi Decoupling Multi-Nilai, Proteksi Polaritas Terbalik & Hot-Swap, Tabel Arus **IPC-2152**, & Thermal Relief. |
| **04** | [04-High-Speed-Crystal-RF-Ethernet.md](./04-High-Speed-Crystal-RF-Ethernet.md) | Panduan RF & Antenna Keep-Out **ESP32 (Espressif)**, Layout Crystal Oscillator (Load Caps, Guard Ring), Ethernet 100Ω Differential Pair & Magnetics Moat (**WIZnet W5500**), Aturan 3W Crosstalk, & Hardening Bus I2C. |
| **05** | [05-Galvanic-Isolation-Creepage-Clearance-ESD.md](./05-Galvanic-Isolation-Creepage-Clearance-ESD.md) | Standar **IEC 62368-1 / IPC-2221B** (Clearance vs Creepage, Pollution Degree, CTI), Isolation Moat (`ADuM1250ARZ` + `B0505S-1W`, `TLP281-4`), Kenapa Isolator Unidirectional (`ISO7721`) Gagal di I2C, & Straight-Through ESD/TVS (**IEC 61000-4-2**). |
| **06** | [06-Routing-Geometry-DFM-DFA-JLCPCB.md](./06-Routing-Geometry-DFM-DFA-JLCPCB.md) | Sudut 45° vs 90°, Acid Traps, Teardrops, Thermal Reliefs, Aturan Silkscreen & Courtyard, serta Tabel Lengkap Kapabilitas Manufaktur **JLCPCB**. |
| **07** | [07-KEAVY-Project-Case-Study-and-Checklist.md](./07-KEAVY-Project-Case-Study-and-Checklist.md) | Studi Kasus Penerapan Nyata pada 5 Board KEAVY (`Brain`, `Relay16`, `Dimmer6`, `Input12A4`, `Standalone`), Master Checklist Pre-Order Gerber, & Daftar Pustaka Lengkap. |

---

## Ringkasan 10 Aturan Emas (*Golden Rules*)

1. **Ground adalah jalur *return current*, bukan sekadar referensi 0V.** Jangan pernah memotong *ground plane* di bawah jalur sinyal cepat.
2. **Kabel eksternal adalah antena EMI terbesar.** Setiap kabel yang keluar dari PCB wajib difilter dan/atau dilindungi ESD tepat di tepi konektor.
3. **Perkecil *hot loop* switching regulator.** Kapasitor keramik input (`100nF`) harus menempel langsung ke pin `VIN` & `GND` IC buck tanpa via penghalang.
4. **Pasang kapasitor decoupling tepat di pin IC (< 2 mm).** Gunakan kombinasi bulk (`10µF`) + HF ceramic (`100nF`) dengan via GND langsung di pad.
5. **Selalu sediakan via return GND saat sinyal berpindah layer**, dan pasang barisan *stitching via* di sekeliling tepi PCB (*Faraday cage*).
6. **Jaga *Isolation Moat* bebas tembaga** di bawah optocoupler, digital isolator (`ADuM1250`), dan transformator Ethernet/DC-DC (`B0505S-1W`).
7. **ESD TVS harus *straight-through* (tanpa stub)** di tepi konektor dengan jalur GND terpendek.
8. **Hormati *Antenna Keep-Out* modul RF/Wi-Fi** di SEMUA layer tembaga (Top, Inner, Bottom) dan jauhkan dari logam/sekrup.
9. **Crystal oscillator wajib dekat pin IC**, dilengkapi *load capacitor* presisi, tanpa jalur daya/sinyal cepat lewat di bawahnya.
10. **Hindari sudut 90° dan sudut lancip (< 90° / *acid trap*).** Gunakan sudut bevel 45° atau kurva halus serta pastikan **0 DRC Violations & 0 Unconnected Items** sebelum ekspor Gerber.
