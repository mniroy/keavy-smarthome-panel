# 06 — Routing Geometry, DFM/DFA & Kapabilitas Manufaktur JLCPCB

> **Sumber Utama:**
> - **JLCPCB** — [*PCB Manufacturing & Assembly Capabilities*](https://jlcpcb.com/capabilities/pcb-capabilities)
> - **IPC-A-600 / IPC-7351** — *Acceptability of Printed Boards & Land Pattern Standard*
> - Altium / Sierra Circuits — *DFM & DFA Best Practices Guide*

---

## 1. Geometri Routing: Sudut 45°, Acid Traps, Teardrops & Thermal Relief

| Fitur Geometri | Aturan Praktik Terbaik | Alasan Teknis (SI / DFM / DFA) |
| :--- | :--- | :--- |
| **Belokan Trace (45° vs 90°)** | **Selalu gunakan belokan bevel 45°** (atau lengkung halus), hindari sudut tajam 90° (*L-bend*). | Mengurangi diskontinuitas impedansi (peningkatan lebar tembaga lokal $\sqrt{2}\times$ di sudut 90°), mengurangi refleksi frekuensi tinggi, dan mencegah penumpukan larutan etsa. |
| **Sudut Lancip (< 90° / Acid Trap)** | **Dilarang keras** pertemuan trace-ke-trace atau trace-ke-pad membentuk sudut lancip $< 90^\circ$. | Larutan kimia *etchant* terperangkap di celah sudut sempit ("V"), memakan tembaga berlebih (*over-etching*) hingga trace menipis atau putus saat fabrikasi. |
| **Teardrops** | Aktifkan *teardrop* pada sambungan trace tipis ke via dan pad komponen *fine-pitch*. | Memperkuat leher sambungan terhadap *thermal shock* / getaran dan memberi toleransi tambahan jika mata bor bergeser (*drill wander*). |
| **Thermal Reliefs** | Gunakan pola *spoke* (4 jari-jari, lebar `0.35 mm`, gap `0.25 mm`) pada pad yang terhubung ke *copper pour* luas. | Mencegah bidang tembaga menyedot panas solder terlalu cepat saat reflow/solder manual (mencegah *cold joint* & *tombstoning*). |
| **Via-in-Pad** | Hindari meletakkan via terbuka di dalam pad SMD biasa (kecuali menggunakan proses *via-in-pad plated over / VIPPO*). | Lubang via terbuka menyedot pasta timah (*solder wicking*) sehingga kaki komponen kekurangan timah saat reflow. |
| **Jarak Tembaga ke Tepi PCB** | Minimal **0.30 mm** untuk trace dan **0.50 mm – 1.0 mm** untuk *copper pour* & lubang PTH. | Mencegah tembaga tersayat pisau *V-cut / routing* saat pemotongan panel PCB di pabrik. |

---

## 2. Tabel Kapabilitas Standar JLCPCB (FR-4 Rigid PCB)

Gunakan kolom **Rekomendasi Aman (High-Yield)** agar papan diproduksi dengan biaya terendah (tanpa biaya tambahan *advanced process*) dan *yield* mendekati 100%:

| Parameter Manufaktur | Minimum JLCPCB (2-Layer 1 oz) | Minimum JLCPCB (4-Layer) | **Rekomendasi Aman (KEAVY Standard)** |
| :--- | :-: | :-: | :-: |
| **Lebar Trace Min (*Min Trace Width*)** | 0.127 mm (5 mil) | 0.10 mm (4 mil) | **≥ 0.20 mm (8 mil)** sinyal; **≥ 0.50–2.5 mm** daya |
| **Jarak Trace Min (*Min Clearance*)** | 0.127 mm (5 mil) | 0.10 mm (4 mil) | **≥ 0.15 mm** (*fine-pitch* 0.5 mm); **≥ 0.20 mm** standar |
| **Ukuran Bor Via Min (*Min Drill*)** | 0.15 mm (biaya ekstra) / 0.30 mm (gratis) | 0.15 mm / 0.20 mm | **≥ 0.30 mm** drill (**0.60 mm** pad) — bebas biaya ekstra! |
| **Annular Ring Min** | ≥ 0.13 mm (outer) | ≥ 0.10 mm (inner) | **≥ 0.15 mm** (`(0.60 - 0.30) / 2 = 0.15 mm`) |
| **Ukuran Bor Maksimum (Drill)** | 6.30 mm | 6.30 mm | Lubang M3 = **3.20 mm** (standar) |
| **Tinggi Teks Silkscreen Min** | 0.80 mm (high-precision) / 1.0 mm (std) | 0.80 mm | **≥ 0.80 mm** tinggi, ketebalan garis **≥ 0.13–0.15 mm** |
| **Silkscreen ke Pad (*Solder Mask*)** | Auto-clip jika < 0.15 mm | Auto-clip jika < 0.15 mm | **0 `silk_over_copper` & 0 `silk_overlap` di DRC!** |
| **Jarak Copper Pour ke Tepi PCB** | ≥ 0.30 mm | ≥ 0.30 mm | **≥ 1.0 mm** (aman dari *V-score* & rel casing DIN-rail) |
| **Ketebalan Tembaga Standar** | 1 oz (35 µm) / 2 oz (70 µm) | 1 oz outer, 0.5 oz inner | **1 oz** untuk Brain/Relay16/Input12A4; **2 oz** direkomendasikan untuk Dimmer6 (15A) |

---

## 3. Aturan Silkscreen & DFA (*Design for Assembly*)

1. **Label Komponen & Polaritas Jelas:**
   * Cantumkan **Designator + Nilai/Nama IC** yang terbaca jelas (tidak tertimpa badan komponen lain atau lubang bor).
   * Beri tanda polaritas jelas (`+` / `-`, pin 1 dot, tanda katoda dioda/LED, orientasi notch konektor `DC3-10P`).
   * Beri label fungsi terminal di sisi atas (`F.SilkS`) **dan** sisi bawah (`B.SilkS`) untuk memudahkan teknisi melakukan *wiring* saat papan sudah terpasang di dalam panel DIN-rail.
2. **Courtyard Clearance:**
   * Pastikan **0 `courtyards_overlap`** di DRC agar mesin *Pick-and-Place* SMT tidak menabrak komponen tetangga dan teknisi masih punya ruang untuk *rework* dengan solder/pinset.
3. **Standardisasi BOM (Menghemat Biaya SMT JLCPCB):**
   * Pilih komponen dari kategori **JLCPCB Basic Parts** sebanyak mungkin (0 biaya *extended part fee* per jenis komponen).
   * Gunakan komponen seragam lintas modul (misal `MCP23017`, `AMS1117-3.3`, `SMBJ28A`, `100nF 0805`, `10k 0805`, `DC3-10P`, terminal `3.81 mm` yang sama di seluruh seri KEAVY).
