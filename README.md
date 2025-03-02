# MetaTimeChanger

MetaTimeChanger adalah alat untuk mengubah metadata dan tanggal modifikasi file video serta gambar secara otomatis berdasarkan format nama file, atau secara manual dengan memilih tanggal untuk setiap file.

## 🎯 **Latar Belakang**
Saya sering melakukan **backup rutin setiap akhir bulan** dengan memindahkan file foto dan video dari HP ke laptop. Namun, setelah melakukan **proses kompresi menggunakan HandBrake atau software lainnya**, saya mengalami masalah di mana **date modified dan metadata berubah menjadi tanggal hari ini**.

HP saya (Redmi) memiliki fitur penamaan file yang rapi, seperti:
- `IMG_YYYYMMDD_id.jpg`
- `VID_YYYYMMDD_id.mp4`

Untuk mengatasi masalah ini, saya berpikir untuk membuat **program yang dapat mengganti date modified dan metadata file setelah dikompres**, agar sesuai dengan tanggal asli berdasarkan format nama file.

Alhamdulillah, akhirnya program ini selesai dan bisa digunakan oleh siapa saja yang mengalami masalah serupa. 😊

## 📥 **Persyaratan**
1. **Python** harus terinstall di sistem Anda. Unduh di [Python.org](https://www.python.org/downloads/)
2. **FFmpeg** diperlukan untuk memproses metadata. Unduh dari situs resminya:
   - 🔗 [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Setelah diunduh, tambahkan `ffmpeg.exe` ke dalam sistem PATH agar bisa digunakan oleh skrip ini.

## 📁 **Struktur File**
```
📂 MetaTimeChanger
├── 📝 README.md  # Dokumentasi ini
├── 📜 MetaTimeChanger.py  # Program utama
└── ⚡ start.bat  # Jalankan program dengan sekali klik
```

## 🚀 **Cara Menggunakan**

MetaTimeChanger dapat dijalankan di **Windows** dan **Android (Termux)**.

---

## 🖥️ **Cara Menggunakan di Windows**

### **1️⃣ Instalasi**
1. **Unduh & Ekstrak** repository ini.
2. **Pastikan** Python dan FFmpeg sudah terinstall dengan benar.
3. **Jalankan `start.bat`** untuk memulai program.

### **2️⃣ Menu Utama**
Saat program berjalan, Anda akan melihat menu berikut:
```
[1] Change Date Metadata Videos
[2] Change Date Metadata Images
[3] Exit
```
Pilih opsi sesuai kebutuhan Anda.

### **3️⃣ Mode Otomatis & Manual**
Setelah memilih kategori (Video atau Gambar), Anda bisa memilih metode pemrosesan:
```
[1] Automatic Based On Format
[2] Manual Formatting
[3] Back
```
- **Automatic Based On Format** → Menggunakan format nama file (`VID_YYYYMMDD_Id.mp4` atau `IMG_YYYYMMDD_Id.jpg/png/jpeg`).
- **Manual Formatting** → Anda harus memasukkan tanggal secara manual untuk setiap file.

### **4️⃣ Output File**
- File asli di folder input **tidak akan dihapus**.
- File yang sudah diperbarui akan **disalin ke folder output** yang Anda tentukan.

## 🛠 **Catatan Penting**
- Pastikan **folder input tidak kosong** sebelum menjalankan program.
- Jika terjadi error, cek apakah path FFmpeg sudah benar dan file yang diproses sesuai dengan format yang didukung.

---

## 📱 **Cara Menggunakan di HP (Termux)**
Jika Anda ingin menjalankan MetaTimeChanger di Android, Anda bisa menggunakan **Termux**.

### **1️⃣ Instalasi Termux & Dependensi**
1. **Unduh dan install Termux** dari Play Store atau F-Droid.
2. **Buka Termux** dan jalankan perintah berikut untuk menginstal dependensi:
   ```bash
   pkg update && pkg upgrade
   pkg install python ffmpeg git
   ```
3. **Clone repository ini** dan masuk ke direktori MetaTimeChanger:
   ```bash
   git clone https://github.com/username/MetaTimeChanger.git
   cd MetaTimeChanger
   ```
4. **Instal pustaka Python yang diperlukan:**
   ```bash
   pip install colorama
   ```

### **2️⃣ Menjalankan Program**
1. Jalankan skrip Python:
   ```bash
   python MetaTimeChanger.py
   ```
2. Ikuti instruksi pada layar, mirip dengan versi Windows.

### **3️⃣ Catatan Penting untuk Pengguna Termux**
- Termux tidak bisa mengubah **date created**, hanya **date modified** dan metadata.
- Pastikan FFmpeg dapat dijalankan dengan mengetik `ffmpeg` di Termux.
- Jika ada masalah izin akses file, gunakan `termux-setup-storage`.

## 🤝 **Kontribusi**
Jika Anda ingin mengembangkan atau meningkatkan program ini, silakan **fork repository ini** dan buat **pull request**!

---
📌 **Dibuat dengan ❤️ untuk mempermudah pengelolaan metadata file media Anda!**

