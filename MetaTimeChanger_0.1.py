import os
import re
import subprocess
import sys
import time
from datetime import datetime
import shutil
from pathlib import Path

# Cek dan install colorama jika belum terinstal
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
except ModuleNotFoundError:
    print("colorama tidak ditemukan, menginstall colorama...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)

class ToolChecker:
    """Kelas untuk cek ketersediaan ExifTool dan FFmpeg"""
    
    @staticmethod
    def check_exiftool():
        """Cek ExifTool"""
        try:
            exiftool_path = shutil.which('exiftool') or shutil.which('exiftool.exe')
            if exiftool_path:
                result = subprocess.run([exiftool_path, '-ver'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return True, exiftool_path, result.stdout.strip()
            return False, None, None
        except:
            return False, None, None
    
    @staticmethod
    def check_ffmpeg():
        """Cek FFmpeg"""
        try:
            ffmpeg_path = shutil.which('ffmpeg') or shutil.which('ffmpeg.exe')
            if ffmpeg_path:
                result = subprocess.run([ffmpeg_path, '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse version dari output pertama
                    lines = result.stdout.split('\n')
                    version_line = lines[0] if lines else ""
                    return True, ffmpeg_path, version_line[:50]
            return False, None, None
        except:
            return False, None, None

# Header ASCII dengan warna kuning solid
header_ascii = (
    f"{Fore.YELLOW}███╗░░░███╗███████╗████████╗░█████╗░\n"
    f"{Fore.YELLOW}████╗░████║██╔════╝╚══██╔══╝██╔══██╗\n"
    f"{Fore.YELLOW}██╔████╔██║█████╗░░░░░██║░░░███████║\n"
    f"{Fore.YELLOW}██║╚██╔╝██║██╔══╝░░░░░██║░░░██╔══██║\n"
    f"{Fore.YELLOW}██║░╚═╝░██║███████╗░░░██║░░░██║░░██║\n"
    f"{Fore.YELLOW}╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░╚═╝{Style.RESET_ALL}\n"
)

def update_metadata_exif(exiftool_path, file_path, new_datetime):
    """Mengubah metadata EXIF menggunakan exiftool dengan TANGGAL dan JAM"""
    try:
        # Format: YYYY:MM:DD HH:MM:SS (format ExifTool)
        date_str = new_datetime.strftime("%Y:%m:%d %H:%M:%S")
        filename = os.path.basename(file_path)
        
        # Tentukan tipe file dari ekstensi
        ext = os.path.splitext(filename)[1].lower()
        is_video = ext in ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.webm']
        is_photo = ext in ['.jpg', '.jpeg', '.png', '.heic', '.gif', '.bmp', '.tiff', '.webp']
        
        print(f"{Fore.CYAN}  📅 Tanggal & Jam: {new_datetime.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  🔧 Menggunakan: ExifTool{Style.RESET_ALL}")
        
        # Perintah untuk mengubah berbagai tag EXIF
        command = [
            exiftool_path,
            '-overwrite_original',  # Menimpa file asli
        ]
        
        if is_video:
            # Untuk video, gunakan tag khusus video
            command.extend([
                f'-CreateDate="{date_str}"',
                f'-ModifyDate="{date_str}"',
                f'-MediaCreateDate="{date_str}"',
                f'-MediaModifyDate="{date_str}"',
                f'-TrackCreateDate="{date_str}"',
                f'-TrackModifyDate="{date_str}"',
                f'-DateTimeOriginal="{date_str}"',
            ])
        elif is_photo:
            # Untuk foto
            command.extend([
                f'-AllDates="{date_str}"',
                f'-DateTimeOriginal="{date_str}"',
                f'-CreateDate="{date_str}"',
                f'-ModifyDate="{date_str}"',
            ])
        else:
            # Untuk file lain
            command.extend([
                f'-AllDates="{date_str}"',
                f'-DateTimeOriginal="{date_str}"',
            ])
        
        # Sync file modify date dengan DateTimeOriginal
        command.extend([
            '-FileModifyDate<DateTimeOriginal',
            file_path
        ])
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}  ✅ Metadata diupdate: {filename}{Style.RESET_ALL}")
            return True
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            print(f"{Fore.RED}  ❌ Gagal: {filename}")
            print(f"     Error: {error_msg}{Style.RESET_ALL}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}  ❌ Timeout saat memproses {os.path.basename(file_path)}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}  ❌ Error: {str(e)}{Style.RESET_ALL}")
        return False

def update_metadata_ffmpeg(ffmpeg_path, file_path, new_datetime, output_folder):
    """Update metadata video dengan FFmpeg (support tanggal & jam)"""
    try:
        # Format untuk FFmpeg: YYYY-MM-DD HH:MM:SS
        date_str = new_datetime.strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(file_path)
        
        print(f"{Fore.CYAN}  📅 Tanggal & Jam: {new_datetime.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  🔧 Menggunakan: FFmpeg{Style.RESET_ALL}")
        
        # Buat nama file temporary
        temp_file = os.path.join(output_folder, f"temp_{filename}")
        output_file = os.path.join(output_folder, filename)
        
        # FFmpeg command untuk update metadata video
        # Gunakan -metadata untuk creation_time dan -movflags untuk kompatibilitas
        command = [
            ffmpeg_path,
            '-i', file_path,  # Input file
            '-metadata', f'creation_time={date_str}',
            '-metadata', f'date={date_str}',
            '-metadata', f'creation_date={date_str}',
            '-movflags', 'use_metadata_tags',  # Untuk format MP4/MOV
            '-c', 'copy',  # Copy semua stream tanpa re-encode
            '-y',  # Overwrite output file
            temp_file
        ]
        
        # Sembunyikan output FFmpeg yang verbose
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Verifikasi file berhasil dibuat
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                # Hapus file asli di output folder jika ada
                if os.path.exists(output_file):
                    os.remove(output_file)
                # Rename temp file ke output file
                os.rename(temp_file, output_file)
                
                # Juga update timestamp file sistem
                timestamp = time.mktime(new_datetime.timetuple())
                os.utime(output_file, (timestamp, timestamp))
                
                print(f"{Fore.GREEN}  ✅ Video metadata diupdate: {filename}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ❌ File output tidak valid: {filename}{Style.RESET_ALL}")
                return False
        else:
            # Hapus temp file jika gagal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            error_msg = result.stderr[-500:] if result.stderr else "Unknown error"
            print(f"{Fore.RED}  ❌ FFmpeg gagal: {filename}")
            print(f"     Error: {error_msg[:200]}...{Style.RESET_ALL}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}  ❌ Timeout FFmpeg: {os.path.basename(file_path)}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}  ❌ Error FFmpeg: {str(e)}{Style.RESET_ALL}")
        return False

def update_timestamps_basic(file_path, new_datetime):
    """Basic file timestamp update"""
    try:
        timestamp = time.mktime(new_datetime.timetuple())
        os.utime(file_path, (timestamp, timestamp))
        print(f"{Fore.CYAN}  🔧 Menggunakan: Basic timestamp{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  ✅ Timestamp file diupdate{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}  ❌ Gagal update timestamp: {str(e)}{Style.RESET_ALL}")
        return False

def extract_datetime_from_filename(filename, is_video=True):
    """Ekstrak tanggal DAN JAM dari nama file"""
    
    # Pattern untuk format dengan JAM (HHMMSS)
    patterns_with_time = [
        # Format: VID_YYYYMMDD_HHMMSS.mp4
        r"VID[_-](\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\.(mp4|mov|avi|mkv|m4v|webm|flv|3gp)",
        # Format: IMG_YYYYMMDD_HHMMSS.jpg
        r"IMG[_-](\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\.(jpg|jpeg|png|heic|webp|bmp|tiff|gif)",
        # Format: YYYYMMDD_HHMMSS.mp4
        r"(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\.(mp4|mov|avi|mkv|jpg|jpeg|png|heic|webp)",
        # Format: VIDEO_YYYYMMDD_HHMMSS.mp4
        r"VIDEO[_-]?(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\..*",
        # Format: WhatsApp: IMG-YYYYMMDD-WAHHMMSS.jpg
        r"IMG[_-](\d{4})(\d{2})(\d{2})[_-]WA(\d{2})(\d{2})(\d{2})\..*",
        # Format: Screenshot_YYYYMMDD-HHMMSS.png
        r"Screenshot[_-](\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\..*",
        # Format: PXL_YYYYMMDD_HHMMSS.mp4 (Google Pixel)
        r"PXL[_-](\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\..*",
        # Format: MVIMG_YYYYMMDD_HHMMSS.jpg (Motion Photo)
        r"MVIMG[_-](\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})\..*",
    ]
    
    # Pattern untuk format TANPA jam (hanya tanggal)
    patterns_without_time = [
        # Format: DSCXXXX.jpg (hanya nomor)
        r"DSC(\d{4})\.(jpg|jpeg|png)",
        # Format: IMG_YYYYMMDD.jpg (tanpa jam)
        r"IMG[_-](\d{4})(\d{2})(\d{2})\.(jpg|jpeg|png|heic)",
        # Format: VID_YYYYMMDD.mp4 (tanpa jam)
        r"VID[_-](\d{4})(\d{2})(\d{2})\.(mp4|mov|avi)",
    ]
    
    # Cari pattern DENGAN jam terlebih dahulu
    for pattern in patterns_with_time:
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                second = int(match.group(6))
                
                # Validasi nilai
                if not (1 <= month <= 12):
                    continue
                if not (1 <= day <= 31):
                    continue
                if not (0 <= hour <= 23):
                    continue
                if not (0 <= minute <= 59):
                    continue
                if not (0 <= second <= 59):
                    continue
                
                return datetime(year, month, day, hour, minute, second), True
            except (ValueError, IndexError):
                continue
    
    # Jika tidak ditemukan dengan jam, cari pattern TANPA jam
    for pattern in patterns_without_time:
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            try:
                if match.group(0).startswith('DSC'):
                    # Format DSCXXXX - biasanya hanya nomor urut
                    # Untuk format ini, kita tidak bisa dapat tanggal dari filename
                    return None, False
                else:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return datetime(year, month, day, 12, 0, 0), False  # Default jam 12:00:00
            except (ValueError, IndexError):
                continue
    
    return None, False

def get_user_datetime_for_file(filename):
    """Minta input tanggal dan jam dari user"""
    while True:
        print(f"\n{Fore.CYAN}📅 File: {filename}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Contoh: 25/12/2023 14:30:45{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Note: Jam bisa dikosongkan, default 12:00:00{Style.RESET_ALL}")
        
        user_input = input(f"{Fore.GREEN}Masukkan tanggal (dan jam): {Style.RESET_ALL}").strip()
        
        if not user_input:
            print(f"{Fore.YELLOW}⚠️  File di-skip{Style.RESET_ALL}")
            return None
        
        try:
            # Coba parse dengan format lengkap (dengan jam)
            if ":" in user_input and len(user_input) > 10:
                return datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
            else:
                # Hanya tanggal, set jam ke default 12:00:00
                date_only = datetime.strptime(user_input, "%d/%m/%Y")
                return datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0)
        except ValueError:
            print(f"{Fore.RED}❌ Format salah! Gunakan DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
            continue

def choose_processing_tool(file_ext, exif_available, ffmpeg_available, is_video=True):
    """Pilih tool processing berdasarkan file type dan availability"""
    
    file_ext = file_ext.lower()
    
    if is_video and file_ext in ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.webm']:
        # Untuk video, tampilkan pilihan tool
        print(f"\n{Fore.CYAN}=== PILIH TOOL UNTUK VIDEO ==={Style.RESET_ALL}")
        
        tools_available = []
        if exif_available:
            tools_available.append(("1", "ExifTool", "Cepat, hanya ubah metadata"))
        if ffmpeg_available:
            tools_available.append(("2", "FFmpeg", "Re-encode, lebih compatible"))
        
        tools_available.append(("3", "Basic", "Hanya ubah timestamp file"))
        
        if not tools_available:
            return "basic"
        
        for num, name, desc in tools_available:
            print(f"[{num}] {name}: {desc}")
        
        while True:
            choice = input(f"{Fore.YELLOW}Pilih tool (1-{len(tools_available)}): {Style.RESET_ALL}").strip()
            
            if choice == "1" and exif_available:
                return "exiftool"
            elif choice == "2" and ffmpeg_available:
                return "ffmpeg"
            elif choice == "3":
                return "basic"
            else:
                print(f"{Fore.RED}Pilihan tidak valid!{Style.RESET_ALL}")
    
    elif is_video:
        # Video format lain, gunakan ExifTool jika ada, else basic
        return "exiftool" if exif_available else "basic"
    
    else:
        # Untuk foto, selalu gunakan ExifTool jika ada
        return "exiftool" if exif_available else "basic"

def process_files(folder_path, output_folder, manual=False, is_video=True, 
                  exiftool_path=None, ffmpeg_path=None, exif_available=False, 
                  ffmpeg_available=False, tool_choice="auto"):
    """Memproses semua file dalam folder"""
    
    if not os.path.exists(folder_path):
        print(f"{Fore.RED}❌ Folder tidak ditemukan: {folder_path}{Style.RESET_ALL}")
        return 0
    
    # Tentukan ekstensi file berdasarkan tipe
    if is_video:
        extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.webm']
        file_type = "video"
    else:
        extensions = ['.jpg', '.jpeg', '.png', '.heic', '.gif', '.bmp', '.tiff', '.webp']
        file_type = "image"
    
    # Kumpulkan file
    files = []
    for filename in sorted(os.listdir(folder_path)):
        if os.path.splitext(filename)[1].lower() in extensions:
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                files.append((filename, file_path))
    
    if not files:
        print(f"{Fore.YELLOW}⚠️  Tidak ada file {file_type} ditemukan{Style.RESET_ALL}")
        return 0
    
    print(f"\n{Fore.CYAN}📊 Ditemukan {len(files)} file {file_type}{Style.RESET_ALL}")
    
    # Buat output folder
    os.makedirs(output_folder, exist_ok=True)
    
    processed_count = 0
    skipped_count = 0
    
    for idx, (filename, file_path) in enumerate(files, 1):
        print(f"\n{Fore.CYAN}[{idx}/{len(files)}] {filename}{Style.RESET_ALL}")
        
        # Tentukan tanggal dan jam
        if manual:
            datetime_obj = get_user_datetime_for_file(filename)
            has_time = True if datetime_obj and datetime_obj.hour != 12 or datetime_obj.minute != 0 or datetime_obj.second != 0 else False
        else:
            datetime_obj, has_time = extract_datetime_from_filename(filename, is_video)
        
        if not datetime_obj:
            print(f"{Fore.YELLOW}  ⏭️  Tidak bisa menentukan tanggal, di-skip{Style.RESET_ALL}")
            skipped_count += 1
            continue
        
        # Tampilkan info
        if has_time:
            print(f"{Fore.GREEN}  📅 Tanggal & Jam dari filename: {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}  📅 Hanya tanggal (jam default 12:00): {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        
        # Tentukan tool yang akan digunakan
        file_ext = os.path.splitext(filename)[1].lower()
        
        if tool_choice == "auto":
            selected_tool = choose_processing_tool(file_ext, exif_available, ffmpeg_available, is_video)
        else:
            selected_tool = tool_choice
        
        # Update metadata dengan tool yang dipilih
        success = False
        
        if selected_tool == "exiftool" and exif_available and exiftool_path:
            success = update_metadata_exif(exiftool_path, file_path, datetime_obj)
        
        elif selected_tool == "ffmpeg" and ffmpeg_available and ffmpeg_path and is_video:
            success = update_metadata_ffmpeg(ffmpeg_path, file_path, datetime_obj, output_folder)
        
        elif selected_tool == "basic":
            success = update_timestamps_basic(file_path, datetime_obj)
        
        if success:
            # Copy ke output folder (kecuali FFmpeg yang sudah handle sendiri)
            if selected_tool != "ffmpeg":
                try:
                    output_path = os.path.join(output_folder, filename)
                    shutil.copy2(file_path, output_path)
                    print(f"{Fore.BLUE}  📤 Disalin ke output folder{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}  ⚠️  Gagal menyalin: {str(e)}{Style.RESET_ALL}")
            processed_count += 1
        else:
            skipped_count += 1
    
    # Tampilkan summary
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📊 SUMMARY PROCESSING{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Total file: {len(files)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Berhasil diproses: {processed_count}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Di-skip: {skipped_count}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Output folder: {output_folder}{Style.RESET_ALL}")
    
    if processed_count > 0:
        print(f"\n{Fore.GREEN}✅ Selesai! File sudah diupdate dengan TANGGAL dan JAM.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   File siap diupload ke Google Photos!{Style.RESET_ALL}")
    
    return processed_count

def main_menu():
    """Menu utama program"""
    
    # Cek tools
    checker = ToolChecker()
    exif_available, exiftool_path, exif_version = checker.check_exiftool()
    ffmpeg_available, ffmpeg_path, ffmpeg_version = checker.check_ffmpeg()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(header_ascii)
        
        # Status tools
        print(f"{Fore.CYAN}=== TOOL STATUS ==={Style.RESET_ALL}")
        
        if exif_available:
            print(f"{Fore.GREEN}✅ ExifTool: {exif_version}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ ExifTool: Tidak ditemukan{Style.RESET_ALL}")
        
        if ffmpeg_available:
            print(f"{Fore.GREEN}✅ FFmpeg: {ffmpeg_version}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  FFmpeg: Tidak ditemukan (opsional){Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}=== GOOGLE PHOTOS METADATA UPDATER ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}   (Dengan support TANGGAL & JAM - ExifTool + FFmpeg){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print("[1] 📹 Update Video Files (MP4, MOV, AVI, dll)")
        print("[2] 📸 Update Photo Files (JPG, PNG, HEIC, dll)")
        print("[3] ⚙️  Test Tools (ExifTool & FFmpeg)")
        print("[4] ℹ️  Info Tools dan Format")
        print("[5] 🚪 Exit")
        
        try:
            choice = input(f"\n{Fore.YELLOW}Pilih menu (1-5): {Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Program dihentikan.{Style.RESET_ALL}")
            break
        
        if choice == "1":
            process_videos_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
        elif choice == "2":
            process_photos_menu(exif_available, exiftool_path)
        elif choice == "3":
            test_tools_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
        elif choice == "4":
            show_tools_info(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
        elif choice == "5":
            print(f"\n{Fore.GREEN}👋 Terima kasih! Sampai jumpa.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def process_videos_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Menu proses video"""
    print(f"\n{Fore.CYAN}=== PROSES FILE VIDEO ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Format yang didukung:{Style.RESET_ALL}")
    print("• VID_YYYYMMDD_HHMMSS.mp4")
    print("• VIDEO_YYYYMMDD_HHMMSS.mov")
    print("• YYYYMMDD_HHMMSS.avi")
    print("• ...dan format lain dengan pola serupa")
    
    folder = input(f"\n{Fore.GREEN}Masukkan folder input: {Style.RESET_ALL}").strip()
    if not os.path.exists(folder):
        print(f"{Fore.RED}❌ Folder tidak ditemukan!{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")
        return
    
    output = input(f"{Fore.GREEN}Folder output (enter untuk otomatis): {Style.RESET_ALL}").strip()
    if not output:
        output = os.path.join(os.path.dirname(folder), os.path.basename(folder) + "_updated")
        print(f"{Fore.BLUE}Output folder: {output}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}=== MODE PEMROSESAN ==={Style.RESET_ALL}")
    print("[1] Otomatis (ambil dari nama file)")
    print("[2] Manual (input untuk setiap file)")
    print("[3] Batch Manual (tanggal sama untuk semua)")
    
    mode = input(f"{Fore.YELLOW}Pilih mode (1-3): {Style.RESET_ALL}").strip()
    
    if mode == "3":
        batch_date = get_batch_datetime()
        if not batch_date:
            return
        process_batch_videos(folder, output, batch_date, exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
    else:
        manual_mode = mode == "2"
        
        # Tanya tool preference
        print(f"\n{Fore.CYAN}=== PILIHAN TOOL ==={Style.RESET_ALL}")
        print("[1] Auto (pilih tool terbaik otomatis)")
        print("[2] ExifTool (cepat, metadata only)")
        print("[3] FFmpeg (re-encode, lebih compatible)")
        print("[4] Basic (hanya timestamp file)")
        
        tool_choice = input(f"{Fore.YELLOW}Pilih tool (1-4): {Style.RESET_ALL}").strip()
        
        if tool_choice == "2" and exif_available:
            selected_tool = "exiftool"
        elif tool_choice == "3" and ffmpeg_available:
            selected_tool = "ffmpeg"
        elif tool_choice == "4":
            selected_tool = "basic"
        else:
            selected_tool = "auto"
        
        print(f"\n{Fore.YELLOW}⏳ Memproses video...{Style.RESET_ALL}")
        process_files(folder, output, manual=manual_mode, is_video=True, 
                     exiftool_path=exiftool_path, ffmpeg_path=ffmpeg_path,
                     exif_available=exif_available, ffmpeg_available=ffmpeg_available,
                     tool_choice=selected_tool)
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def process_photos_menu(exif_available, exiftool_path):
    """Menu proses foto"""
    print(f"\n{Fore.CYAN}=== PROSES FILE FOTO ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Format yang didukung:{Style.RESET_ALL}")
    print("• IMG_YYYYMMDD_HHMMSS.jpg")
    print("• YYYYMMDD_HHMMSS.png")
    print("• Screenshot_YYYYMMDD-HHMMSS.png")
    print("• ...dan format lain dengan pola serupa")
    
    folder = input(f"\n{Fore.GREEN}Masukkan folder input: {Style.RESET_ALL}").strip()
    if not os.path.exists(folder):
        print(f"{Fore.RED}❌ Folder tidak ditemukan!{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")
        return
    
    output = input(f"{Fore.GREEN}Folder output (enter untuk otomatis): {Style.RESET_ALL}").strip()
    if not output:
        output = os.path.join(os.path.dirname(folder), os.path.basename(folder) + "_updated")
        print(f"{Fore.BLUE}Output folder: {output}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}=== MODE PEMROSESAN ==={Style.RESET_ALL}")
    print("[1] Otomatis (ambil dari nama file)")
    print("[2] Manual (input untuk setiap file)")
    
    mode = input(f"{Fore.YELLOW}Pilih mode (1-2): {Style.RESET_ALL}").strip()
    manual_mode = mode == "2"
    
    print(f"\n{Fore.YELLOW}⏳ Memproses foto...{Style.RESET_ALL}")
    process_files(folder, output, manual=manual_mode, is_video=False, 
                 exiftool_path=exiftool_path, ffmpeg_path=None,
                 exif_available=exif_available, ffmpeg_available=False,
                 tool_choice="exiftool" if exif_available else "basic")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def get_batch_datetime():
    """Minta tanggal dan jam untuk batch processing"""
    while True:
        print(f"\n{Fore.CYAN}=== BATCH DATE SETTING ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Masukkan tanggal dan jam untuk SEMUA file:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Contoh: 25/12/2023 14:30:45{Style.RESET_ALL}")
        
        user_input = input(f"{Fore.GREEN}Tanggal & Jam: {Style.RESET_ALL}").strip()
        
        if not user_input:
            print(f"{Fore.YELLOW}⚠️  Batch processing dibatalkan{Style.RESET_ALL}")
            return None
        
        try:
            if ":" in user_input and len(user_input) > 10:
                return datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
            else:
                date_only = datetime.strptime(user_input, "%d/%m/%Y")
                return datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0)
        except ValueError:
            print(f"{Fore.RED}❌ Format salah!{Style.RESET_ALL}")
            continue

def process_batch_videos(folder, output, batch_date, exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Proses semua video dengan tanggal yang sama"""
    extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.webm']
    
    files = []
    for filename in sorted(os.listdir(folder)):
        if os.path.splitext(filename)[1].lower() in extensions:
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                files.append((filename, file_path))
    
    if not files:
        print(f"{Fore.YELLOW}⚠️  Tidak ada file video ditemukan{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}📊 Akan memproses {len(files)} file dengan tanggal:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📅 {batch_date.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
    
    # Pilih tool untuk batch
    print(f"\n{Fore.CYAN}=== PILIH TOOL UNTUK BATCH ==={Style.RESET_ALL}")
    if exif_available:
        print("[1] ExifTool (cepat, rekomendasi)")
    if ffmpeg_available:
        print("[2] FFmpeg (lebih compatible)")
    print("[3] Basic (hanya timestamp)")
    
    while True:
        tool_choice = input(f"{Fore.YELLOW}Pilih tool: {Style.RESET_ALL}").strip()
        
        if tool_choice == "1" and exif_available:
            selected_tool = "exiftool"
            break
        elif tool_choice == "2" and ffmpeg_available:
            selected_tool = "ffmpeg"
            break
        elif tool_choice == "3":
            selected_tool = "basic"
            break
        else:
            print(f"{Fore.RED}Pilihan tidak valid!{Style.RESET_ALL}")
    
    confirm = input(f"\n{Fore.YELLOW}Lanjutkan? (y/n): {Style.RESET_ALL}").strip().lower()
    if confirm != 'y':
        print(f"{Fore.YELLOW}⚠️  Dibatalkan{Style.RESET_ALL}")
        return
    
    os.makedirs(output, exist_ok=True)
    processed = 0
    
    for idx, (filename, file_path) in enumerate(files, 1):
        print(f"\n[{idx}/{len(files)}] {Fore.CYAN}{filename}{Style.RESET_ALL}")
        
        success = False
        
        if selected_tool == "exiftool" and exif_available and exiftool_path:
            success = update_metadata_exif(exiftool_path, file_path, batch_date)
        
        elif selected_tool == "ffmpeg" and ffmpeg_available and ffmpeg_path:
            success = update_metadata_ffmpeg(ffmpeg_path, file_path, batch_date, output)
        
        elif selected_tool == "basic":
            success = update_timestamps_basic(file_path, batch_date)
        
        if success:
            if selected_tool != "ffmpeg":  # FFmpeg sudah handle copy sendiri
                try:
                    output_path = os.path.join(output, filename)
                    shutil.copy2(file_path, output_path)
                    print(f"{Fore.BLUE}  📤 Disalin ke output folder{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}  ⚠️  Gagal menyalin: {str(e)}{Style.RESET_ALL}")
            processed += 1
    
    print(f"\n{Fore.GREEN}✅ Batch selesai! {processed}/{len(files)} file diproses.{Style.RESET_ALL}")

def test_tools_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Test ExifTool dan FFmpeg"""
    print(f"\n{Fore.CYAN}=== TEST TOOLS ==={Style.RESET_ALL}")
    
    if exif_available:
        print(f"\n{Fore.GREEN}✅ ExifTool tersedia{Style.RESET_ALL}")
        print(f"Path: {exiftool_path}")
        
        try:
            result = subprocess.run([exiftool_path, '-ver'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"Versi: {result.stdout.strip()}")
            
            # Test sample file
            print(f"\n{Fore.YELLOW}Test dengan file ini:{Style.RESET_ALL}")
            test_file = __file__
            result = subprocess.run([exiftool_path, '-DateTimeOriginal', '-CreateDate', '-FileModifyDate', test_file],
                                  capture_output=True, text=True, timeout=5)
            if result.stdout:
                print(f"Metadata: {result.stdout.strip()}")
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}❌ ExifTool tidak ditemukan!{Style.RESET_ALL}")
    
    if ffmpeg_available:
        print(f"\n{Fore.GREEN}✅ FFmpeg tersedia{Style.RESET_ALL}")
        print(f"Path: {ffmpeg_path}")
        
        try:
            result = subprocess.run([ffmpeg_path, '-version'], 
                                  capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            if lines:
                print(f"Versi: {lines[0][:100]}")
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  FFmpeg tidak ditemukan!{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def show_tools_info(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Tampilkan info tools dan format"""
    print(f"\n{Fore.CYAN}=== INFORMASI TOOLS & FORMAT ==={Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🛠️  TOOLS YANG TERSEDIA:{Style.RESET_ALL}")
    if exif_available:
        print(f"{Fore.GREEN}• ExifTool: {exif_version if 'exif_version' in locals() else 'Available'}{Style.RESET_ALL}")
        print(f"  - Untuk: Foto & Video")
        print(f"  - Kecepatan: Cepat (metadata only)")
        print(f"  - Kelebihan: Tidak re-encode, preserver kualitas")
    else:
        print(f"{Fore.RED}• ExifTool: Not installed{Style.RESET_ALL}")
    
    if ffmpeg_available:
        print(f"\n{Fore.GREEN}• FFmpeg: {ffmpeg_version if 'ffmpeg_version' in locals() else 'Available'}{Style.RESET_ALL}")
        print(f"  - Untuk: Video terutama")
        print(f"  - Kecepatan: Lambat (mungkin re-encode)")
        print(f"  - Kelebihan: Lebih compatible dengan beberapa player")
    else:
        print(f"\n{Fore.YELLOW}• FFmpeg: Not installed (optional){Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}📁 FORMAT YANG DIDUKUNG:{Style.RESET_ALL}")
    print("• Video: MP4, MOV, AVI, MKV, WebM, WMV, FLV, 3GP")
    print("• Foto: JPG, JPEG, PNG, HEIC, WebP, BMP, TIFF, GIF")
    
    print(f"\n{Fore.YELLOW}📝 POLA NAMA FILE:{Style.RESET_ALL}")
    print("• VID_YYYYMMDD_HHMMSS.mp4 → 25 Des 2023, 14:30:45")
    print("• IMG_YYYYMMDD_HHMMSS.jpg → 1 Jan 2024, 08:00:15")
    print("• 20231225_120000.png → 25 Des 2023, 12:00:00")
    
    print(f"\n{Fore.YELLOW}🎯 REKOMENDASI:{Style.RESET_ALL}")
    print("• Untuk FOTO: Gunakan ExifTool")
    print("• Untuk VIDEO: ExifTool > FFmpeg > Basic")
    print("• Google Photos: ExifTool memberikan hasil terbaik")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        print(f"{Fore.CYAN}🚀 Memulai Google Photos Metadata Updater...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Dengan ExifTool & FFmpeg support{Style.RESET_ALL}")
        time.sleep(1)
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Program dihentikan{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")