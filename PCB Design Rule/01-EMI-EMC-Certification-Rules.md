# 01 — EMI / EMC & Certification Design Rules

> **Sumber Utama:**
> - John Teel, Predictable Designs — [*11 PCB Design Rules to NEVER Break or You'll Fail Certification*](https://predictabledesigns.com/pcb-certification-rules-never-break/)
> - Texas Instruments — *SZZA009: PCB Design Guidelines For Reduced EMI*
> - Henry W. Ott — *Electromagnetic Compatibility Engineering* (Wiley)

Sebuah produk elektronika bisa bekerja 100% normal di meja kerja, namun **gagal total di laboratorium sertifikasi (FCC Part 15 / CE EN 55032 / IEC 61000)** karena radiasi EMI berlebih, kebocoran *conducted emissions* ke jala-jala listrik, atau *reset*/rusak saat disengat listrik statis (ESD).

---

## 11 Aturan Wajib Sertifikasi PCB (Predictable Designs)

### Rule #1 — NEVER Let a Cable Leave the Board Without a Filter
* **Masalah:** Kabel sepanjang ~1 meter (USB, LAN, power 24V, bus I2C antar-board) adalah antena resonansi sempurna pada frekuensi uji FCC/CE (30 MHz – 1 GHz). Hanya beberapa **mikroampere (µA)** *common-mode current* pada kabel sudah cukup membuat produk gagal uji *radiated emissions*.
* **Solusi:**
  * Tempatkan filter **tepat di tepi konektor**:
    * **Jalur daya & sinyal lambat:** *Ferrite bead* + kapasitor keramik ke GND (`100nF` / `1nF`) membentuk filter RC/LC.
    * **Jalur diferensial cepat (USB/Ethernet):** *Common-mode choke* (CMC) khusus interface tersebut atau magnetics RJ45 (`HR911105A`).
    * **Kabel berpelindung (*shielded*):** Ikat *shield* langsung ke *chassis*/enclosure logam tepat di titik masuk kabel.
  * **Tips Lab:** Jika belum yakin butuh filter, selalu sediakan *footprint* resistor `0Ω` seri (yang bisa diganti *ferrite bead* saat uji lab tanpa spin ulang PCB).

### Rule #2 — NEVER Route a Fast Signal Over a Gap in the Plane Below It
* **Masalah:** Arus balik (*return current*) sinyal berfrekuensi tinggi selalu mengalir tepat di bawah jalurnya pada *reference plane*. Celah pada *ground plane* (karena *split ground*, jalur di layer GND, atau deretan via yang *antipad*-nya menyatu menjadi slot panjang) memaksa arus balik memutar jauh — membentuk **loop antenna** yang memancarkan EMI kuat.
* **Solusi:**
  * Pertahankan **satu *solid ground plane* utuh** di bawah seluruh jalur cepat (SPI, clock, Ethernet, USB).
  * Pisahkan rangkaian bising dan sensitif secara **tata letak fisik (*placement*)**, bukan dengan memotong *ground plane*.
  * Sebelum pesan PCB, tampilkan layer GND sendirian (*single layer view*) dan pastikan tidak ada celah/slot di bawah sinyal cepat.

### Rule #3 — NEVER Break the Conditions of Your Pre-Certified Module
* **Masalah:** Modul wireless pra-sertifikasi (seperti **ESP32-WROOM-32** / ESP32 DevKit) menghemat puluhan ribu dolar biaya uji radio FCC/CE, **hanya jika** seluruh syarat datasheet-nya dipatuhi.
* **Solusi:**
  * Tempatkan antena PCB tepat di tepi luar papan (atau menjorok keluar dari tepi PCB utama).
  * Salin dimensi **Antenna Keep-Out Zone** persis sesuai datasheet pada **SEMUA layer** (tidak boleh ada copper pour, track, via, komponen, maupun sekrup logam di area tersebut).
  * Jangan mengganti antena eksternal dengan tipe atau *gain* yang tidak tercantum di sertifikat modul.

### Rule #4 — NEVER Let Return Current Change Layers Without a Nearby Path
* **Masalah:** Ketika sinyal berpindah layer lewat via, *reference plane*-nya ikut berubah. Tanpa jalur pendek bagi arus balik untuk berpindah bidang, arus menyebar mencari via GND/kapasitor terdekat dan menciptakan loop radiasi besar.
* **Solusi:**
  * Letakkan **Ground Return Via** tepat di sebelah via sinyal cepat (clock, SPI, differential pair) saat berpindah antar bidang GND.
  * Jika berpindah antara bidang GND dan bidang Power, pasang **stitching capacitor** (`10nF–100nF`) di dekat via sinyal.
  * Pasang **barisan *perimeter ground stitching vias*** mengelilingi tepi PCB (jarak $\le \lambda/20$ atau tiap 5–10 mm) untuk membentuk *Faraday cage* dan mencegah *edge cavity radiation*.

### Rule #5 — NEVER Put Connectors on Opposite Edges of the Board
* **Masalah:** Bidang ground tetap memiliki sedikit resistansi dan induktansi, sehingga ada beda potensial beberapa milivolt antara sisi kiri dan kanan PCB. Jika dua kabel dipasang di sisi berlawanan, beda tegangan tersebut menggerakkan kedua kabel seperti **antena dipol**.
* **Solusi:**
  * Kelompokkan seluruh konektor eksternal (power, LAN, USB, I/O) di **satu tepi yang sama** agar semua kabel berada pada potensial ground yang identik.
  * Jauhkan rangkaian bising (buck converter, crystal) dari area di antara konektor.
  * *Pengecualian (misal bus daisy-chain DIN-rail kiri-kanan):* Wajib memperkuat koneksi ground/shield di kedua konektor, menambahkan isolasi galvanik di antara domain bus dan daya lapangan, serta memfilter jalur yang keluar.

### Rule #6 — NEVER Let a Signal Leave the Board Without ESD Protection
* **Masalah:** Uji imunitas ESD (**IEC 61000-4-2**, ±8 kV kontak / ±15 kV udara) menyengat langsung konektor, tombol, dan bagian logam. Jika proteksi salah letak, lonjakan tegangan tetap menembus ke MCU.
* **Solusi:**
  * Pasang dioda TVS/ESD **tepat di tepi konektor** (sebelum sinyal menyentuh komponen lain).
  * Gunakan **straight-through (flow-through) routing** — sinyal masuk langsung melewati pad dioda TVS lalu keluar ke IC, **bukan cabang (stub)**.
  * Berikan jalur GND terpendek dari pin ground TVS langsung ke *ground plane* via lubang via tersendiri tepat di pad.

### Rule #7 — NEVER Drive an External Line With a Full-Speed Edge
* **Masalah:** Radiasi EMI tidak hanya ditentukan oleh frekuensi clock, melainkan oleh **kecepatan naik-turun sisi sinyal (*rise/fall time*, $dv/dt$)**. Sinyal lambat (100 kHz I2C atau GPIO relay) dengan *rise time* 2 ns tetap menghasilkan harmonik hingga > 150 MHz!
* **Solusi:**
  * Pasang **resistor damping seri (`22Ω – 100Ω`, standar `47Ω`)** tepat di pin driver yang keluar ke kabel/konektor (misal `SDA`, `SCL`, `INT`, `SPI`).
  * Atur *GPIO drive strength / slew rate* di firmware MCU ke level paling lambat yang masih memenuhi *timing*.
  * *Pengecualian:* Interface berimpedansi terkontrol seperti USB HS atau Ethernet MDI mengikuti terminasi spesifik datasheet.

### Rule #8 — NEVER Let the Switching Regulator's Hot Loop Grow
* **Masalah:** Pada buck converter, *hot loop* (jalur arus pulsa tinggi $di/dt$: Input Cap $\rightarrow$ High-Side FET $\rightarrow$ Freewheeling Diode/Low-Side FET $\rightarrow$ Input Cap GND) berpindah dalam hitungan nanodetik. Semakin luas area loop, semakin besar radiasi magnetik EMI.
* **Solusi:**
  * Tempatkan **kapasitor input keramik (`100nF`–`1µF` 50V)** menempel langsung ke pin `VIN` dan `GND` IC regulator (usahakan tanpa via di antara pin IC dan kapasitor).
  * Buat area tembaga **switch node (`SW`)** sekecil dan sependek mungkin (cukup lebar untuk arus beban, jangan dijadikan *copper pour* luas karena merupakan antena medan listrik $dv/dt$).
  * Ikuti persis contoh layout pada datasheet IC buck converter.

### Rule #9 — NEVER Skip the Filter on the Power Input
* **Masalah:** Uji *conducted emissions* mengukur noise switching (150 kHz – 30 MHz) yang didorong balik oleh PCB melalui kabel daya menuju stopkontak PLN. Adaptor bersertifikat (Mean Well, dll.) **tidak** melindungi PCB Anda dari uji ini.
* **Solusi:**
  * Pasang filter input tepat di terminal masuk daya (kombinasi **TVS + Bulk Electrolytic + High-Frequency Ceramic `100nF` + Ferrite Bead/Pi-Filter**).
  * Pisahkan secara fisik sisi input ("bersih") dan sisi output ("bising") filter agar noise tidak melompat secara kapasitif melewati filter.

### Rule #10 — NEVER Route Traces Under or Beside the Crystal
* **Masalah:** Rangkaian crystal oscillator (25 MHz / 40 MHz) sekaligus merupakan **sumber harmonik kuat** dan **rangkaian analog paling sensitif**. Jalur lain di dekatnya bisa memungut harmonik clock dan memancarkannya ke kabel, atau menginjeksikan noise yang menggeser frekuensi clock (*jitter*/gagal link Ethernet/Wi-Fi).
* **Solusi:**
  * Tempatkan crystal & *load capacitor* sedekat mungkin ke pin `XI`/`XO` IC dengan jalur simetris dan pendek (tanpa via).
  * Jauhkan crystal dari tepi papan dan konektor eksternal.
  * Jangan pernah meletakkan jalur daya atau sinyal digital melintas di bawah atau persis di samping crystal.

### Rule #11 — NEVER Ignore Creepage and Clearance on Mains / Isolated Boards
* **Masalah:** Keselamatan pengguna (*safety*, **IEC 62368-1**) mensyaratkan jarak aman udara (*clearance*, ditentukan tegangan puncak) dan jarak permukaan (*creepage*, ditentukan tegangan RMS + derajat polusi + CTI material FR-4).
* **Solusi:**
  * Pisahkan zona tegangan tinggi / terisolasi ke area khusus di PCB.
  * Buat **copper keep-out moat** atau **slot/slit potongan mekanis** ($\ge 1$ mm) di bawah komponen isolasi (optocoupler, `ADuM1250`, `B0505S-1W`, trafo).
  * Gunakan adaptor AC-DC eksternal bersertifikat agar tegangan jala-jala 220V AC tidak masuk ke papan kontrol bila memungkinkan.

---

## Ringkasan Sumber Kebisingan & Mitigasi Cepat

| Masalah Uji Lab | Penyebab Paling Umum | Solusi Cepat Desain PCB |
| :--- | :--- | :--- |
| **Radiated Emissions (30 MHz – 1 GHz)** | *Common-mode current* di kabel, celah di GND plane, *hot loop* buck lebar, *edge rate* terlalu cepat. | Filter di konektor, GND plane solid, `C_BIN 100nF` rapat di buck, resistor seri `47Ω`, *perimeter stitching vias*. |
| **Conducted Emissions (150 kHz – 30 MHz)** | Switching buck converter memompa ripple balik ke kabel power. | Pi-filter / `C_EMI 100nF` + elko bulk tepat di terminal input daya. |
| **ESD Immunity Failure (IEC 61000-4-2)** | TVS terlalu jauh dari konektor, routing bercabang (*stub*), jalur GND TVS panjang. | TVS *straight-through* di tepi konektor + via GND ganda langsung di pad. |
| **RF / Wi-Fi Range Buruk** | Copper pour/track masuk ke *antenna keep-out*, komponen logam dekat antena. | Keep-out total semua layer di bawah antena + letakkan antena di tepi papan. |
