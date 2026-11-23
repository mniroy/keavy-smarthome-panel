# 05 — Galvanic Isolation, Creepage/Clearance & ESD/Surge Protection

> **Sumber Utama:**
> - **IEC 62368-1 / IEC 60664-1** — *Audio/Video, IT & Communication Technology Equipment Safety & Insulation Coordination*
> - **IPC-2221B (Table 6-1)** — *Generic Standard on Printed Board Design (Electrical Conductor Spacing)*
> - Analog Devices — [*ADuM1250 iCoupler Bidirectional I2C Isolator Datasheet & PCB Layout Guide*](https://www.analog.com/en/products/adum1250.html)
> - Semtech & Texas Instruments — *IEC 61000-4-2 ESD/TVS Straight-Through PCB Layout Guidelines*

---

## 1. Clearance vs Creepage (Standar Keselamatan)

* **Clearance (Jarak Udara):** Jarak terpendek **melalui udara** antara dua konduktor. Ditentukan oleh **tegangan puncak (*Peak Voltage*)** untuk mencegah loncatan bunga api (*arcing / flashover*).
* **Creepage (Jarak Permukaan):** Jarak terpendek **menyusuri permukaan isolasi** (FR-4 / solder mask). Ditentukan oleh **tegangan RMS**, **Pollution Degree (PD)**, dan **Comparative Tracking Index (CTI)** bahan PCB untuk mencegah kebocoran arus karbonisasi (*tracking*) akibat debu & kelembapan.

### Tabel Referensi Cepat Jarak Isolasi (IPC-2221B & IEC 62368-1, PD2, FR-4 CTI IIIa)

| Tegangan Kerja | IPC-2221B External Coated (Clearance Min) | IEC 62368-1 Basic Insulation (Creepage PD2) | IEC 62368-1 Reinforced Insulation (Creepage PD2) | Catatan Praktis |
| :--- | :-: | :-: | :-: | :--- |
| **0 – 30V DC** | 0.13 mm | 0.6 mm | 1.2 mm | Sirkuit kontrol 24V DC / SELV |
| **31 – 50V DC** | 0.13 mm | 0.6 mm | 1.2 mm | Rail 24V–48V dengan margin surja |
| **51 – 150V Peak** | 0.40 mm | 1.5 mm | 3.0 mm | Isolasi fungsional / DC bus |
| **230V AC Mains (325V Peak)** | 0.80 mm (Internal) / 1.25 mm (Ext) | 2.5 – 3.0 mm | **5.0 – 6.4 mm** | Wajib *milled air slot* ($\ge 1$ mm) bila ruang sempit |
| **2500 Vrms Galvanic Barrier** | — | ≥ 3.8 mm (SOIC-8 body) | ≥ 7.6 mm (SOIC-16W) | `ADuM1250ARZ` (SOIC-8) + `B0505S-1W` + `TLP281-4` |

> **Catatan Penting:** Solder mask standar PCB **TIDAK diakui** oleh lab keselamatan (UL/TÜV/CE) sebagai penghalang isolasi jangka panjang karena bisa tergores atau berlubang mikro (*pinholes*). Selalu hitung jarak antar tembaga terbuka/tertutup sesuai aturan *basic/reinforced insulation*.

---

## 2. Desain Galvanic Isolation Moat (Menghilangkan Ground Loop 100%)

Pada sistem panel dengan beban arus besar (misal Dimmer LED 15A atau 16 Relay 24V), penyatuan ground antara bus logika ESP32 (`GND_BUS`) dan ground daya 24V (`GND_ISO`) menyebabkan **Ground Loop** — arus balik beban 24V merembes masuk ke kabel pita tipis `DC3-10P` dan membakar kabel/mengacaukan I2C!

### Aturan Wajib Layout Isolator (`ADuM1250ARZ` + `B0505S-1W` & `TLP281-4`)
1. **True Isolation Moat (Copper Keep-Out):**
   * Kosongkan **100% tembaga (`F.Cu`, `In1`, `In2`, `B.Cu`)** tepat di bawah badan IC isolator (`ADuM1250ARZ`, `B0505S-1W`, `TLP281-4`) dan di sepanjang batas antara domain `GND_BUS` dan `GND_ISO` / `GND_FIELD`.
   * Jangan pernah membiarkan *copper pour* `GND_ISO` merayap mendekati pin sisi bus hanya dengan jarak 0.4 mm — itu menghancurkan rating isolasi 2500 Vrms! Gunakan **Zone Keep-Out Area** khusus.
2. **Jangan Tumpang-Tindih Plane (*Zero Plane Overlap*):**
   * Bidang `GND_BUS` (Layer 1) dan `GND_ISO` (Layer 2) tidak boleh saling bertumpuk luas karena membentuk kapasitor parasitik yang menurunkan **CMTI (*Common-Mode Transient Immunity*)** dan membocorkan noise switching melewati barrier.
3. **Decoupling Wajib di Kedua Sisi Isolator:**
   * Datasheet Analog Devices mewajibkan kapasitor keramik **`100nF` X7R** (< 2 mm dari pin) di **Side 1** (`VDD1–GND1`) **DAN** di **Side 2** (`VDD2–GND2`) untuk menekan radiasi RF dari transformator *iCoupler* internal.

---

## 3. Jebakan Fatal: Kenapa Isolator Unidirectional (`ISO7721` / `ADuM1201`) TIDAK BISA untuk I2C!

| Parameter | Bus I2C (`SDA` & `SCL`) | Isolator Standar (`ISO7721DR`, `ADuM1201`) | Isolator Khusus I2C (`ADuM1250ARZ`, `TI ISO1540`) |
| :--- | :--- | :--- | :--- |
| **Arah Sinyal** | **Bidirectional** (2 arah bolak-balik di 1 kawat) | **Unidirectional** (1 arah tetap) | **Bidirectional** dengan *direction steering* |
| **Tipe Output** | **Open-Drain** (butuh pull-up) | **Push-Pull** (aktif drive HIGH/LOW) | **Open-Drain** dengan logika *anti-latch* |
| **Hasil di I2C** | — | ❌ **FATAL: Bus Lockup / Latch-up LOW permanen!** | ✅ **Berfungsi sempurna & Hot-Swappable** |

* **Kapan `ISO7721` bisa dipakai?** Hanya untuk sinyal searah: **UART (TX/RX)**, **SPI (MOSI/MISO/SCK)**, atau sinyal trigger digital 1 arah.
* **Untuk I2C:** Wajib pakai **`ADuM1250ARZ`** (Analog Devices) atau **`TI ISO1540` / `ISO1541`** (Texas Instruments) + suplai terisolasi **`B0505S-1W`**.

---

## 4. Layout Proteksi ESD / TVS (*Straight-Through Routing* — IEC 61000-4-2)

Tegangan lonjakan ESD memiliki *rise time* **< 1 nanodetik** ($I_{pp}$ hingga 30A pada Level 4 ±8 kV kontak / ±15 kV udara).

$$V_{\text{IC}} = V_{\text{clamp, TVS}} + L_{\text{parasitik}} \cdot \frac{di}{dt}$$

Hanya **5 nH** induktansi dari *stub* sepanjang 5 mm sudah menambah lonjakan $5\text{ nH} \times 30\text{ A/ns} = \mathbf{+150\text{ V}}$ tepat di pin MCU!

### 4 Aturan Emas Layout TVS/ESD (Semtech & TI):
1. **Inline / Straight-Through Routing:** Trace dari konektor **WAJIB masuk ke pad TVS terlebih dahulu**, lalu keluar dari pad seberangnya menuju IC. **Dilarang membuat cabang (T-stub)** ke TVS.
2. **Dekat Konektor:** Letakkan dioda TVS (`USBLC6-2SC6`, `SMBJ28A`) sedekat mungkin dengan tepi konektor (sebelum sinyal lewat via atau komponen lain).
3. **Via GND Terpendek:** Hubungkan pin ground TVS langsung ke *solid ground plane* menggunakan via tepat di sebelah pad (atau beberapa via paralel untuk TVS daya besar).
4. **Proteksi Input Analog 0–10V (`KEAVY-INPUT12A4`):** Kombinasikan resistor seri pembagi (`22kΩ 1%`) + **Zener 3.3V (`BZT52C3V3`)** tepat di depan pin ADC (`ADS1115`) — jika kabel 24V tidak sengaja tersambung ke input analog, arus terbatas hanya ~0.94 mA dan tegangan terkunci aman di 3.3V.
