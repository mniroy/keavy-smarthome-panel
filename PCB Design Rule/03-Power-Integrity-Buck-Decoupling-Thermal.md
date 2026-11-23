# 03 — Power Integrity, Switching Regulators, Decoupling & Thermal Design

> **Sumber Utama:**
> - Texas Instruments — *SLVAER0C / SLVA157: DC/DC Converter PCB Layout Guidelines*
> - Texas Instruments — *SZZA009: Decoupling & Bypassing Techniques*
> - **IPC-2152** — *Standard for Determining Current Carrying Capacity in Printed Board Design*
> - Predictable Designs — *Rules #8 & #9*

---

## 1. Layout Switching Regulator / Buck Converter (*Hot Loop*)

Buck converter (seperti **XL1509-5.0** pada `KEAVY-BRAIN` & `Standalone`) adalah sumber EMI nomor 1 pada papan daya.

### Anatomi *Hot Loop* (Arus Pulsa Tinggi $di/dt$)
* Jalur kritisnya adalah: **`C_IN (+)` $\rightarrow$ Pin `VIN` IC Buck $\rightarrow$ Pin `SW` $\rightarrow$ Dioda Schottky (`SS34`) $\rightarrow$ `C_IN (GND)`**.
* **Aturan Layout Wajib:**
  1. **Kapasitor Keramik Input (`C_BIN`, `100nF – 1µF` 50V X7R):** Letakkan **menempel langsung** di pin `VIN` dan `GND` IC buck pada layer yang sama (`F.Cu`), dengan loop tembaga sekecil mungkin. Jangan hanya mengandalkan elko THT (ESR & ESL elko terlalu tinggi untuk frekuensi switching > 100 kHz).
  2. **Switch Node (`SW`):** Hubungkan pin `SW` IC, katoda dioda Schottky (`SS34`), dan input induktor (`L1`) dengan jalur pendek dan lebar secukupnya — **jangan pernah** membuat *copper pour* luas pada node `SW` (menjadi pemancar medan listrik $dv/dt$).
  3. **Jalur Feedback (`FB`):** Jauhkan trace feedback dari induktor (`L1`) dan node `SW`. Ambil titik sampling feedback **setelah** kapasitor output (`C5`), bukan langsung di kaki induktor.
  4. **Induktor Berpelindung (*Shielded Inductor*):** Gunakan induktor *shielded* (seperti `Bourns SRN6045TA 33µH 3A`) untuk menahan kebocoran medan magnetik ke rangkaian sekitar.

---

## 2. Filter Input Daya & Proteksi Industrial 24V DC

Untuk sistem panel 24V DC (industrial / smarthome), urutan komponen proteksi dari konektor masuk (`J1`) harus berurutan secara fisik dan elektrik:

```text
[J1 24V_IN] ─┬─ [C_EMI 100nF 50V] (Filter EMI HF ke GND)
             └─ [F1 Fuse 3A/15A] ─► [Q_REV P-MOSFET AOD403 + DZ1 12V + R_REV 100k]
                                         │
                                         ├─ [D_TVS SMBJ28A] (Clamp Surja 28V-45V ke GND)
                                         ├─ [C_BULK 100uF–470uF 35V] (Reservoir Arus)
                                         └─ [C_HF 100nF 50V] ─► +24V_BUS
```

* **Kenapa P-MOSFET (`AOD403`) lebih baik dari Dioda Seri untuk Reverse Polarity?**
  * Dioda biasa menjatuhkan tegangan ~0.7V (pada 10A = **7 Watt panas terbuang!**).
  * P-MOSFET `AOD403` ($R_{DS(on)} \approx 8\text{ m}\Omega$) hanya membuang $I^2 R = 10^2 \times 0.008 = 0.8\text{ W}$! Zener `BZT52C12` melindungi gate agar $|V_{GS}|$ tidak melebihi batas maksimum 20V saat input 24V.
* **Proteksi Hot-Swap Bus (`KEAVY-BUS REV 2.0`):**
  * Jangan pernah menyuplai modul eksternal langsung dari regulator 3.3V internal ESP32 DevKit (rawan *brownout/reset* akibat *inrush current* saat hot-plug).
  * Gunakan **LDO 3.3V terdedikasi** (`AMS1117-3.3` terpisah) + **PTC Polyfuse 500mA** pada rail `+5V_BUS` dan `+3V3_BUS` agar hubung singkat di kabel modul tidak mematikan `KEAVY-BRAIN`.

---

## 3. Strategi Decoupling & Bypass Capacitor

Kapasitor nyata memiliki induktansi parasitik (ESL) sehingga hanya efektif di bawah frekuensi resonansi sendirinya (*Self-Resonant Frequency*):

* **Aturan Multi-Nilai:** Gabungkan kapasitor **Bulk (`10µF`–`100µF`)** untuk lonjakan arus frekuensi rendah + **Ceramic (`100nF` X7R 0805/0603)** tepat di setiap pin `VDD`/`VCC` IC untuk lonjakan nanodetik.
* **Aturan Jarak < 2 mm:** Letakkan `100nF` sedekat mungkin dengan pin daya IC (khususnya `W5500` < 1.5 mm, `ADuM1250` Side 1 & Side 2 < 2 mm, `MCP23017`, `PCA9685`, `ADS1115`).
* **Urutan Aliran Tembaga:** Power Plane/Trace $\rightarrow$ **Pad Kapasitor Decoupling** $\rightarrow$ Pin `VCC` IC (pastikan arus melewati kapasitor dulu sebelum masuk ke pin IC).
* **Via GND Langsung:** Taruh via GND tepat di sebelah pad ground kapasitor (hindari trace panjang dari pad kapasitor ke via).

---

## 4. Kapasitas Arus Trace & Via (Standar IPC-2152)

Estimasi lebar trace minimum untuk **1 oz Copper (35 µm)** pada layer luar (`F.Cu` / `B.Cu`), kenaikan suhu $\Delta T = 10^\circ\text{C}$ (konservatif & aman untuk panel tertutup):

| Arus (A) | Lebar Trace Min ($\Delta T = 10^\circ\text{C}$, 1 oz) | Lebar Trace Rekomendasi ($\Delta T = 10^\circ\text{C}$, 2 oz) | Contoh Penggunaan di KEAVY |
| :-: | :-: | :-: | :--- |
| **0.5 A** | 0.25 mm (10 mil) | 0.15 mm (6 mil) | Jalur logic `+3V3_BUS`, `+5V_BUS` |
| **1.0 A** | 0.65 mm (26 mil) | 0.35 mm (14 mil) | Jalur `+5V` ke ESP32 / W5500 |
| **2.0 A** | 1.50 mm (60 mil) | 0.75 mm (30 mil) | Output 1 channel Dimmer 24V (48W–60W) |
| **3.0 A** | 2.50 mm (100 mil) | 1.25 mm (50 mil) | Jalur utama `+24V_BUS` Relay16 |
| **5.0 A** | 4.50 mm (177 mil) | 2.25 mm (90 mil) | Main bus daya menengah |
| **10–15 A** | **Copper Pour (Polygon) + 2 oz Cu** | **Copper Pour + Solder-Mask Opening (Tinning)** | Bus 15A `KEAVY-DIMMER6` (`F.Cu` +24V pour & `B.Cu` GND pour) |

### Kapasitas Arus Via Standar (Plating 25 µm):
* Via drill `0.30 mm` (pad `0.60 mm`): **~0.8 – 1.0 A** per via (sinyal & daya kecil).
* Via drill `0.40 mm` (pad `0.80 mm`): **~1.2 – 1.5 A** per via.
* Untuk jalur daya > 2A yang pindah layer, gunakan **array beberapa via paralel** (misal 4–6 via) untuk membagi arus dan menurunkan induktansi + resistansi termal.

---

## 5. Manajemen Termal & Thermal Reliefs

* **Thermal Reliefs (Spoke Connections):** Wajib digunakan pada pad komponen SMD/THT yang terhubung ke *ground/power plane* luas agar panas solder saat reflow/penyolderan manual tidak langsung tersedot ke seluruh papan (mencegah *cold solder joint* / *tombstoning*).
  * Standar aman: *Gap* `0.25 mm`, *Spoke Width* `0.35 mm` (4 jari-jari).
* **Thermal Vias di Bawah MOSFET / LDO:** Pada komponen berdaya panas (`AOD4184A`, `AOD403`, `AMS1117-3.3`), perluas *copper pour* di sekitar Tab Drain/Output dan tambahkan via termal menuju bidang tembaga di layer seberang untuk disipasi panas.
