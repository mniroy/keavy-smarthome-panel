# 02 — Grounding, Return Current, Via Stitching & PCB Stack-Up

> **Sumber Utama:**
> - Rick Hartley — *Grounding and Return Current Paths in High-Speed PCBs*
> - Henry W. Ott — *Electromagnetic Compatibility Engineering*
> - Texas Instruments — *SZZA009* & *SCAA082 (High-Speed Layout Guidelines)*
> - NXP — *EMC and System-ESD Design Guidelines for Board Layout*

---

## 1. Fisika Dasar *Return Current* (Filosofi Rick Hartley & Henry Ott)

Kesalahan paling umum dalam desain PCB adalah menganggap **Ground** sekadar "tempat pembuangan arus 0V". Pada kenyataannya:

* **Energi sinyal merambat sebagai medan elektromagnetik** di dalam material dielektrik (FR-4) **di antara trace sinyal dan *reference plane*-nya**, bukan hanya elektron di dalam tembaga.
* **Arus balik DC** mencari jalur dengan **resistansi terendah** (jalur lurus terpendek antar titik).
* **Arus balik frekuensi tinggi (> ~100 kHz, atau semua sinyal digital dengan *rise time* cepat)** selalu mencari jalur dengan **induktansi terendah** — yaitu **tepat di bawah trace sinyal** pada bidang referensi terdekat!

$$\text{Radiasi EMI} \propto I \cdot f^2 \cdot A_{\text{loop}}$$

Di mana $A_{\text{loop}}$ adalah **luas area loop** antara jalur sinyal maju dan jalur arus baliknya. Meminimalkan $A_{\text{loop}}$ adalah kunci utama desain low-EMI.

---

## 2. Aturan Solid Ground Plane vs Split Ground

* **JANGAN memotong (split) Ground Plane** secara sembarangan untuk memisahkan "AGND" dan "DGND" pada rangkaian *mixed-signal* (ADC, DAC, MCU).
  * Jika satu saja jalur digital melintas di atas celah *split*, arus baliknya terpaksa memutar mengelilingi celah tersebut $\rightarrow$ menciptakan **slot antenna** dan *ground bounce*.
* **Praktik Terbaik (Partitioning di Atas 1 Solid Ground Plane):**
  1. Gunakan **satu bidang GND utuh (solid)** di seluruh papan (kecuali di batas **isolasi galvanik sejati** seperti 2500 Vrms `ADuM1250` / optocoupler!).
  2. Kelompokkan komponen secara fisik berdasarkan zona: **Zona Analog**, **Zona Digital/MCU**, **Zona Power/Switching**, dan **Zona RF**.
  3. Pastikan trace analog hanya berada di zona analog, dan trace digital hanya di zona digital — arus balik frekuensi tinggi secara alami akan tetap terpisah karena mengikuti trace-nya masing-masing!
* **Pengecualian Wajib Split:** Pada **Isolasi Galvanik** (`GND_BUS` vs `GND_ISO` atau `GND_FIELD`), *ground plane* **WAJIB dipisah total** dengan celah bebas tembaga (*isolation moat*) dan tidak boleh ada satu pun trace yang melintas kecuali lewat IC isolator/optocoupler.

---

## 3. Ground Return Vias pada Perpindahan Layer

Ketika jalur sinyal cepat (SPI, clock, Ethernet, USB) berpindah dari `F.Cu` ke `B.Cu` (atau antar layer pada PCB 4-layer) menggunakan via:
* Jika *reference plane* berubah (misal dari GND Layer 2 ke GND Layer 3), arus balik harus ikut berpindah bidang.
* **Aturan Wajib:** Tempatkan minimal **1 Ground Return Via sedekat mungkin** (< 1–2 mm) dari via sinyal tersebut.
* Untuk *bus* paralel (seperti 6 jalur SPI W5500), tempatkan beberapa *ground return via* mengapit klaster via sinyal tersebut.

---

## 4. Perimeter Ground Stitching Vias (*Faraday Cage*)

Pada PCB 2-layer maupun 4-layer, kebisingan frekuensi tinggi dapat merambat di antara bidang tembaga dan memancar keluar melalui tepi papan (*edge cavity radiation*).

* **Solusi:** Buat deretan *ground stitching vias* mengelilingi seluruh tepi papan (dan mengikat semua *copper pour* di `F.Cu` dan `B.Cu` agar tidak ada pulau tembaga mengambang / *floating copper islands*).
* **Aturan Jarak (*Pitch*) Stitching Via:**
  $$\text{Pitch} \le \frac{\lambda_{\min}}{20} = \frac{c}{20 \cdot f_{\max} \cdot \sqrt{\varepsilon_r}}$$
  * Untuk FR-4 ($\varepsilon_r \approx 4.2$):
    * $f_{\max} = 500\text{ MHz} \rightarrow \text{Pitch} \le 14.6\text{ mm}$ (rekomendasi praktis: **8–10 mm**).
    * $f_{\max} = 2.4\text{ GHz (Wi-Fi)} \rightarrow \text{Pitch} \le 3.0\text{ mm}$ di sekitar area RF (dan **wajib kosong** di area *antenna keep-out*).
* **Hindari Dangling Via (KiCad DRC):** Pada PCB 2-layer yang tidak memiliki *F.Cu ground pour* penuh di tepi papan, hubungkan *perimeter stitching vias* dengan jalur **Guard Ring `F.Cu` selebar 0.4–0.5 mm** agar setiap via terikat di kedua sisi (`F.Cu` dan `B.Cu`).

---

## 5. Rekomendasi Stack-Up PCB

### A. PCB 2-Layer (Ekonomis — Industrial Control, I2C, Relay, Dimmer, MCU)
* **Layer 1 (`F.Cu`):** Sebagian besar komponen SMD, routing sinyal utama, jalur daya, dan *ground pour* lokal.
* **Layer 2 (`B.Cu`):** **Solid Ground Plane** semaksimal mungkin!
  * *Aturan Emas 2-Layer:* Jika terpaksa meletakkan jumper/trace di `B.Cu`, buat **sependek mungkin** dan hindari memotong melintang tepat di bawah sinyal cepat (clock/SPI/Ethernet).

### B. PCB 4-Layer (Rekomendasi Utama untuk High-Speed, RF/Wi-Fi, EMC Ketat)
* **Stack-Up Standar (Paling Umum & Murah di JLCPCB):**
  1. `L1 (Top)`: Sinyal + Komponen
  2. `L2 (Inner 1)`: **Solid GND Plane** (sangat dekat dengan L1 $\rightarrow$ jarak prepreg ~0.1–0.2 mm, induktansi loop sangat kecil!)
  3. `L3 (Inner 2)`: **Power Plane** (`+3V3`, `+5V`, `+24V` terpartisi) atau **GND Plane ke-2**
  4. `L4 (Bottom)`: Sinyal Sekunder + GND Pour
* **Stack-Up Ultra-Low-EMI (SIG / GND / GND / SIG — Rekomendasi Rick Hartley):**
  * Kedua layer dalam (`L2` & `L3`) adalah **Solid GND**, sedangkan daya (`+3V3`, `+5V`) dirutekan sebagai trace lebar / poligon di `L1`/`L4`. Menghasilkan *shielding* terbaik dan impedansi konsisten di kedua sisi luar.
