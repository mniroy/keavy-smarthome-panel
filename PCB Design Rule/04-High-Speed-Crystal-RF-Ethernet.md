# 04 — High-Speed, Crystal Oscillator, RF/ESP32, Ethernet & I2C Layout

> **Sumber Utama:**
> - Espressif Systems — [*ESP32 Hardware Design Guidelines*](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/)
> - WIZnet — [*W5500 Hardware Design Guide*](https://docs.wiznet.io/Product/iEthernet/W5500/Application/hardware-design-guide)
> - NXP — *UM10204: I2C-Bus Specification and User Manual*
> - Texas Instruments — *SCAA082 (High-Speed Layout Guidelines)*

---

## 1. Panduan RF & Modul ESP32 (Espressif)

1. **Antenna Keep-Out Zone (Aturan Mutlak):**
   * Di bawah dan di sekitar antena PCB modul ESP32 (ESP32-WROOM-32 / DevKit V1), **WAJIB 100% bebas tembaga** pada semua layer (`F.Cu`, `In1`, `In2`, `B.Cu`): tidak boleh ada *ground pour*, trace, via, komponen, maupun sekrup/mur logam.
   * Posisikan antena tepat di **tepi terluar PCB** atau menjorok keluar dari tepi papan dasar.
   * Jauhkan minimal **15 mm** dari komponen tinggi berbahan logam (trafo, konektor RJ45 berpelindung, terminal blok, relai).
2. **Power Supply ESP32:**
   * ESP32 menarik pulsa arus puncak hingga **500 mA** saat kalibrasi/transmisi Wi-Fi.
   * Trace daya `+5V` / `+3V3` minimal lebar **0.5 mm – 0.8 mm (20–32 mil)** dengan kapasitor bulk (`100µF–220µF`) + keramik (`100nF`) di dekat pin daya.

---

## 2. Layout Crystal Oscillator (25 MHz W5500 / 40 MHz MCU)

Crystal pasif sangat rentan terhadap kapasitansi parasitik dan gangguan EMI:

1. **Penempatan & Load Capacitors (`C_Y1`, `C_Y2`):**
   * Tempatkan crystal sedekat mungkin ke pin `XI` & `XO` IC.
   * Hitung nilai *load capacitor* eksternal sesuai spesifikasi $C_L$ crystal:
     $$C_1 = C_2 = 2 \cdot (C_L - C_{\text{stray}})$$
     *(Dengan $C_{\text{stray}} \approx 3\text{–}5\text{ pF}$; untuk crystal 25 MHz dengan $C_L = 12\text{ pF}$, nilai ideal adalah **15 pF – 18 pF**).*
   * Tanpa *load capacitor*, frekuensi clock Ethernet 25 MHz bisa bergeser melampaui toleransi ±50 ppm dan menyebabkan link LAN gagal negosiasi atau sering putus.
2. **No Vias & Short Traces:** Usahakan trace `XI` dan `XO` tetap pada satu layer (`F.Cu`), pendek, simetris, dan tanpa melewati jalur daya.
3. **Ground Shielding:** Hubungkan pin ground casing crystal (pin 2 & 4 pada SMD 3225) langsung ke *solid ground plane* melalui via pendek di dekat pad. Jangan lewatkan sinyal cepat atau *switching trace* di bawah area crystal.

---

## 3. Layout Ethernet 100BASE-TX (WIZnet W5500 + HanRun HR911105A)

1. **Pasangan Diferensial (`TX+/TX-`, `RX+/RX-`):**
   * Target impedansi diferensial: **$100\,\Omega \pm 10\%$**.
   * Rute paralel berdekatan, panjang sama (*length matched*), tanpa sudut 90° (gunakan 45° atau kurva halus), dan jaga jarak dari jalur digital/power lain ($\ge 3W$).
   * Pertahankan **solid GND plane utuh** di bawah trace dari W5500 hingga konektor RJ45 magnetics.
2. **Magnetics & RJ45 (`HR911105A`) Moat:**
   * Letakkan RJ45 sedekat mungkin dengan W5500 (< 25 mm).
   * Pada desain sertifikasi ketat, kosongkan tembaga di bawah area magnetics/transformator RJ45 (memisahkan sisi PHY dari sisi kabel Ethernet 1500 Vrms).
3. **Komponen Kritis W5500:**
   * **Resistor Bias `EXRES1` (Pin 10):** Wajib **12.4 kΩ presisi 1%** sedekat mungkin dengan pin 10 ke GND (resistor 5% dapat menyebabkan link Ethernet tidak stabil saat suhu berubah).
   * **Cap Regulator Internal `1V2O` (Pin 22):** Pasang `100nF` tepat di pin 22 ke GND.
   * **Decoupling `3V3_ETH`:** Pasang `100nF` lokal dekat IC W5500 (`C_W55`) selain elko/keramik `10µF` di LDO `AMS1117-3.3`.

---

## 4. Aturan Crosstalk (3W Rule) & High-Speed SPI

* **3W Rule:** Untuk meminimalkan *crosstalk* kapasitif/induktif antar jalur sinyal sejajar (terutama jalur clock `SCK` SPI dan jalur paralel panjang), jaga jarak pusat-ke-pusat minimal **$3 \times W$** (atau celah udara minimal **$2 \times W$** di antara tepi trace).
* **Crossings Orthogonal:** Jika dua sinyal cepat terpaksa bersilangan pada layer berbeda (`F.Cu` vs `B.Cu`), persilangkan secara tegak lurus (**90°**) untuk meminimalkan luas area tumpang tindih (*overlap capacitance*).

---

## 5. Hardening Bus I2C di Lingkungan Panel Industrial (EMI Relay/PWM)

Bus I2C dirancang untuk komunikasi *on-board*, sehingga jika ditarik lewat kabel pita antar-board (seperti `KEAVY-BUS` `DC3-10P`) di dalam panel relay/dimmer 24V, wajib menerapkan teknik *hardening*:

1. **Pull-Up Kuat (`2.2kΩ` di Master, `4.7kΩ` di sisi terisolasi):** Lebih kebal terhadap induksi EMI dibanding `10kΩ` standar, sekaligus menjaga *rise time* tetap tajam meski kapasitansi kabel pita meningkat.
2. **Resistor Damping Seri (`47Ω`):** Dipasang seri pada `SDA`, `SCL`, dan `INT` tepat sebelum konektor keluar untuk meredam *ringing* kabel dan menekan harmonik EMI (Predictable Designs Rule #7).
3. **Pinout Kabel Pita Berpelindung GND:** Jangan pernah menaruh `SDA` dan `SCL` bersebelahan langsung tanpa pemisah! Di `KEAVY-BUS REV 2.0`, **Pin 8 (`GND_BUS`)** diletakkan persis di antara Pin 7 (`I2C_SDA`) dan Pin 9 (`I2C_SCL`) sebagai *shield* anti-*crosstalk*.
4. **Frekuensi Clock Konservatif (`100 kHz`):** Gunakan Standard Mode `100 kHz` (bukan 400 kHz) pada panel relay/dimmer untuk margin kebisingan maksimum.
5. **Proteksi ESD (`USBLC6-2SC6`):** Pasang TVS kapasitansi ultra-rendah (< 1 pF) secara *straight-through* tepat di konektor `DC3-10P`.
