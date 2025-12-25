<h1 align="center"> MetaTimeChanger v2.0 - Smart Extractor Edition </h1>
   
<p align="center"> <img src="https://raw.githubusercontent.com/DeJavi08/MetaTimeChanger/refs/heads/main/ss.png" alt="Digital Literacy Banner" width="300px" /> </p> <p align="center"> <img src="https://img.shields.io/badge/version-2.0-blue.svg" /> <img src="https://img.shields.io/badge/tool-Python%203-orange.svg" /> <img src="https://img.shields.io/badge/license-educational-lightgrey.svg" /> <img src="https://img.shields.io/badge/status-active-brightgreen.svg" /> </p> <p align="center"> </p>

MetaTimeChanger adalah alat **cerdas** untuk mengubah metadata dan tanggal modifikasi file video serta gambar. Versi 2.0 memiliki kemampuan **smart pattern extraction** yang bisa mengekstrak tanggal dari berbagai format nama file, tidak peduli prefix atau suffix!

## 🎯 **Fitur Utama v2.0**

### 🧠 **Smart Pattern Detection**
Program sekarang bisa mengekstrak pola `YYYYMMDD_HHMMSS` dari **mana saja** dalam nama file:
- ✅ `lv_0_20231225143045.mp4`
- ✅ `holiday_20231225_143045(1).mp4`  
- ✅ `YYYYMMDD_HHMMSS_backup.mp4`
- ✅ `video_2023-12-25_14-30-45_final.mp4`

### 🔧 **Dual Engine Support**
- **ExifTool**: Untuk foto & video (cepat, metadata only)
- **FFmpeg**: Untuk video (lebih compatible, mungkin re-encode)
- **Auto Selection**: Pilih otomatis tool terbaik

### 🤖 **Interactive Processing**
- **Smart Suggestions**: Generate saran tanggal dari angka dalam filename
- **User Confirmation**: Konfirmasi sebelum update metadata
- **Multiple Choices**: Pilih antara tanggal terdeteksi, saran lain, atau input manual

## 🚀 **Cara Menggunakan v2.0**

### **Menu Utama Baru:**
```
=== SMART METADATA EXTRACTOR ===
[1] 📹 Update Video Files (Mode Cerdas)
[2] 📸 Update Photo Files (Mode Cerdas)  
[3] 🧠 Test Smart Extraction
[4] ⚙️ Settings
[5] 🚪 Exit
```

### **Mode Pemrosesan:**
1. **Otomatis Cerdas** (Rekomendasi):
   - Ekstrak otomatis dari nama file
   - Konfirmasi ke user sebelum update
   - Tanya user jika format tidak sesuai

2. **Manual Interaktif**:
   - Tanya setiap file dengan saran cerdas
   - Multiple choice options
   - Skip jika diperlukan

## 📁 **Format File yang Didukung**

### **Standard Formats:**
- `VID_YYYYMMDD_HHMMSS.mp4`
- `IMG_YYYYMMDD_HHMMSS.jpg`

### **Smart Formats (Baru!):**
- `lv_0_20231225143045.mp4` (Xiaomi screen recording)
- `PXL_20231225_143045.jpg` (Google Pixel)
- `IMG-20231225-WA143045.jpg` (WhatsApp)
- `Screenshot_20231225-143045.png` (Samsung)
- `holiday_20231225_143045(1).mp4` (Renamed files)
- `2023.12.25_14.30.45_vacation.jpg` (Dotted format)

### **Separator Variations:**
- `YYYYMMDD_HHMMSS` (underscore)
- `YYYYMMDDHHMMSS` (no separator)
- `YYYY-MM-DD HH-MM-SS` (dash)
- `YYYY.MM.DD HH.MM.SS` (dot)

## 🛠 **Persyaratan v2.0**

### **Wajib:**
1. **Python 3.6+**
2. **ExifTool** (untuk metadata lengkap)

### **Opsional (tapi direkomendasikan):**
3. **FFmpeg** (untuk video processing yang lebih baik)

### **Python Libraries:**
```bash
pip install colorama
```

## 📱 **Android (Termux) Support**

### **Instalasi Termux:**
```bash
pkg update && pkg upgrade
pkg install python ffmpeg git
pip install colorama
```

### **Catatan Android:**
- Tidak bisa mengubah **date created**, hanya **date modified** dan metadata
- Gunakan `termux-setup-storage` untuk akses file
- FFmpeg di Termux support sebagian besar format

## 🐛 **Troubleshooting v2.0**

### **Jika tanggal tidak terdeteksi:**
1. Program akan **bertanya ke user** (tidak langsung skip)
2. Pilih **"Input tanggal manual"** untuk masukkan manual
3. Atau **"Skip file ini"** untuk lewati

### **Jika metadata tidak update:**
1. Cek apakah **ExifTool terinstall** dengan `exiftool -ver`
2. Coba **ganti tool** ke FFmpeg atau Basic mode
3. Pastikan **file tidak sedang digunakan** oleh program lain

## 🔄 **Migrasi dari v1.x**

### **Perubahan Perilaku:**
- **Tidak langsung skip** file dengan format tidak sesuai
- **Lebih banyak format** yang didukung
- **Interaktif** - konfirmasi user diperlukan

### **New Features:**
- Smart pattern extraction
- Device-specific format recognition  
- Dual engine (ExifTool + FFmpeg)
- Interactive user interface

## 🤝 **Kontribusi v2.0**

### **Format Baru yang Mau Ditambahkan?**
1. Fork repository
2. Tambahkan pattern di fungsi `smart_extract_datetime()`
3. Test dengan file contoh
4. Buat pull request

### **Bug Reports:**
1. Sertakan **nama file contoh**
2. **Tanggal yang diharapkan**
3. **Output error** (jika ada)

---

📌 **MetaTimeChanger v2.0 - Lebih Cerdas, Lebih Fleksibel, Lebih User-Friendly!**

Dibuat dengan ❤️ untuk mempermudah pengelolaan metadata file media Anda, terutama setelah proses backup dan kompresi!
