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
        date_str = new_datetime.strftime("%Y:%m:%d %H:%M:%S")
        filename = os.path.basename(file_path)
        
        ext = os.path.splitext(filename)[1].lower()
        is_video = ext in ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.webm']
        is_photo = ext in ['.jpg', '.jpeg', '.png', '.heic', '.gif', '.bmp', '.tiff', '.webp']
        
        command = [
            exiftool_path,
            '-overwrite_original',
        ]
        
        if is_video:
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
            command.extend([
                f'-AllDates="{date_str}"',
                f'-DateTimeOriginal="{date_str}"',
                f'-CreateDate="{date_str}"',
                f'-ModifyDate="{date_str}"',
            ])
        else:
            command.extend([
                f'-AllDates="{date_str}"',
                f'-DateTimeOriginal="{date_str}"',
            ])
        
        command.extend([
            '-FileModifyDate<DateTimeOriginal',
            file_path
        ])
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True
        else:
            return False
            
    except:
        return False

def update_metadata_ffmpeg(ffmpeg_path, file_path, new_datetime, output_folder):
    """Update metadata video dengan FFmpeg"""
    try:
        date_str = new_datetime.strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(file_path)
        
        temp_file = os.path.join(output_folder, f"temp_{filename}")
        output_file = os.path.join(output_folder, filename)
        
        command = [
            ffmpeg_path,
            '-i', file_path,
            '-metadata', f'creation_time={date_str}',
            '-metadata', f'date={date_str}',
            '-metadata', f'creation_date={date_str}',
            '-movflags', 'use_metadata_tags',
            '-c', 'copy',
            '-y',
            temp_file
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                if os.path.exists(output_file):
                    os.remove(output_file)
                os.rename(temp_file, output_file)
                
                timestamp = time.mktime(new_datetime.timetuple())
                os.utime(output_file, (timestamp, timestamp))
                
                return True
            else:
                return False
        else:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False
            
    except:
        return False

def update_timestamps_basic(file_path, new_datetime):
    """Basic file timestamp update"""
    try:
        timestamp = time.mktime(new_datetime.timetuple())
        os.utime(file_path, (timestamp, timestamp))
        return True
    except:
        return False

def smart_extract_datetime(filename, is_video=True):
    """
    Fungsi cerdas untuk ekstrak datetime dari berbagai format file
    """
    filename_without_ext = os.path.splitext(filename)[0]
    
    # DAFTAR PATTERN YANG DICARI
    patterns = [
        # Pattern dengan SPASI: "Vid 20210327 092658"
        (r'(?:Vid|Video|IMG|Image|Photo|Pic|Pict|Screen|Screenshot|Record|Recording)[ _-]*(\d{4})(\d{2})(\d{2})[ _-]*(\d{2})(\d{2})(\d{2})', 'Vid YYYYMMDD HHMMSS'),
        
        # Pattern umum dengan SPASI: "20210327 092658"
        (r'(\d{4})(\d{2})(\d{2})[ _-]+(\d{2})(\d{2})(\d{2})', 'YYYYMMDD HHMMSS'),
        
        # Pattern dengan underscore: "20210327_092658"
        (r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', 'YYYYMMDD_HHMMSS'),
        
        # Pattern tanpa separator: "20210327092658"
        (r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', 'YYYYMMDDHHMMSS'),
        
        # Pattern dengan dash: "2021-03-27-09-26-58"
        (r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})', 'YYYY-MM-DD-HH-MM-SS'),
        
        # Pattern dengan dot: "2021.03.27.09.26.58"
        (r'(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})', 'YYYY.MM.DD.HH.MM.SS'),
    ]
    
    # Cari semua kemungkinan pattern
    all_matches = []
    
    for pattern, pattern_name in patterns:
        matches = list(re.finditer(pattern, filename_without_ext, re.IGNORECASE))
        for match in matches:
            try:
                groups = match.groups()
                
                if len(groups) >= 6:
                    # Pattern dengan jam
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])
                    hour = int(groups[3])
                    minute = int(groups[4])
                    second = int(groups[5])
                    
                    # Validasi
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
                    
                    datetime_obj = datetime(year, month, day, hour, minute, second)
                    
                    all_matches.append({
                        'datetime': datetime_obj,
                        'pattern': pattern_name,
                        'has_time': True,
                        'position': match.start()
                    })
                    
            except (ValueError, IndexError):
                continue
    
    if not all_matches:
        # Coba cari hanya tanggal
        date_patterns = [
            r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            matches = list(re.finditer(pattern, filename_without_ext))
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) >= 3:
                        year = int(groups[0])
                        month = int(groups[1])
                        day = int(groups[2])
                        
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            datetime_obj = datetime(year, month, day, 12, 0, 0)
                            return datetime_obj, False
                except ValueError:
                    continue
        
        return None, False
    
    # Pilih match terbaik
    best_match = min(all_matches, key=lambda x: x['position'])
    return best_match['datetime'], best_match['has_time']

def ask_user_for_single_file(filename, default_datetime=None):
    """Tanya user untuk satu file yang tidak punya format"""
    print(f"\n{Fore.YELLOW}⚠️  File: {filename}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}   Tidak ditemukan format tanggal dalam nama file{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.CYAN}Pilihan:{Style.RESET_ALL}")
        print("[1] Input tanggal manual")
        print("[2] Gunakan tanggal default (jika ada)")
        print("[3] Skip file ini")
        print("[4] Gunakan tanggal yang sama untuk SEMUA file berikutnya")
        
        if default_datetime:
            print(f"{Fore.GREEN}   Tanggal default: {default_datetime.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        
        choice = input(f"{Fore.GREEN}Pilih (1-4): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            # Input manual
            while True:
                print(f"\n{Fore.CYAN}Manual input untuk: {filename}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Contoh: 27/03/2021 09:26:58{Style.RESET_ALL}")
                
                user_input = input(f"{Fore.GREEN}Masukkan tanggal (dan jam): {Style.RESET_ALL}").strip()
                
                if not user_input:
                    print(f"{Fore.YELLOW}Kembali ke menu pilihan{Style.RESET_ALL}")
                    break
                
                try:
                    if ":" in user_input and len(user_input) > 10:
                        return datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S"), False
                    else:
                        date_only = datetime.strptime(user_input, "%d/%m/%Y")
                        return datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0), False
                except ValueError:
                    print(f"{Fore.RED}❌ Format salah!{Style.RESET_ALL}")
                    continue
        
        elif choice == "2" and default_datetime:
            return default_datetime, False
        
        elif choice == "3":
            return None, False
        
        elif choice == "4":
            # Minta tanggal untuk semua file berikutnya
            while True:
                print(f"\n{Fore.CYAN}Tanggal untuk SEMUA file berikutnya:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
                
                user_input = input(f"{Fore.GREEN}Masukkan tanggal (dan jam): {Style.RESET_ALL}").strip()
                
                try:
                    if ":" in user_input and len(user_input) > 10:
                        batch_date = datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
                    else:
                        date_only = datetime.strptime(user_input, "%d/%m/%Y")
                        batch_date = datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0)
                    
                    return batch_date, True  # Flag True = apply ke semua file
                    
                except ValueError:
                    print(f"{Fore.RED}❌ Format salah!{Style.RESET_ALL}")
                    continue
        
        else:
            print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")

def process_files_with_options(folder_path, output_folder, processing_mode="auto", is_video=True, 
                               exiftool_path=None, ffmpeg_path=None, exif_available=False, 
                               ffmpeg_available=False, tool_choice="auto"):
    """
    Memproses file dengan berbagai mode:
    - "auto": Otomatis tanpa konfirmasi (hanya tanya jika format tidak ditemukan)
    - "confirm": Konfirmasi satu per satu
    - "batch": Tanggal sama untuk semua file
    """
    
    if not os.path.exists(folder_path):
        print(f"{Fore.RED}❌ Folder tidak ditemukan: {folder_path}{Style.RESET_ALL}")
        return 0
    
    if is_video:
        extensions = ['.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.webm']
        file_type = "video"
    else:
        extensions = ['.jpg', '.jpeg', '.png', '.heic', '.gif', '.bmp', '.tiff', '.webp']
        file_type = "image"
    
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
    
    os.makedirs(output_folder, exist_ok=True)
    
    processed_count = 0
    skipped_count = 0
    batch_date = None
    apply_to_all = False
    
    for idx, (filename, file_path) in enumerate(files, 1):
        print(f"\n{Fore.CYAN}[{idx}/{len(files)}] {filename}{Style.RESET_ALL}")
        
        datetime_obj = None
        skip_file = False
        
        # MODE BATCH: Gunakan tanggal yang sama untuk semua
        if processing_mode == "batch" or apply_to_all:
            if batch_date is None and processing_mode == "batch":
                # Minta tanggal batch
                while True:
                    print(f"\n{Fore.CYAN}=== TANGGAL UNTUK SEMUA FILE ==={Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Contoh: 27/03/2021 09:26:58{Style.RESET_ALL}")
                    
                    user_input = input(f"{Fore.GREEN}Masukkan tanggal untuk SEMUA file: {Style.RESET_ALL}").strip()
                    
                    try:
                        if ":" in user_input and len(user_input) > 10:
                            batch_date = datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
                        else:
                            date_only = datetime.strptime(user_input, "%d/%m/%Y")
                            batch_date = datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0)
                        break
                    except ValueError:
                        print(f"{Fore.RED}❌ Format salah!{Style.RESET_ALL}")
                        continue
            
            datetime_obj = batch_date
            print(f"{Fore.GREEN}  📅 Menggunakan tanggal batch: {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        
        # MODE AUTO: Coba ekstrak otomatis, hanya tanya jika gagal
        elif processing_mode == "auto":
            datetime_obj, has_time = smart_extract_datetime(filename, is_video)
            
            if datetime_obj:
                if has_time:
                    print(f"{Fore.GREEN}  ✅ Ditemukan: {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  ✅ Ditemukan (hanya tanggal): {datetime_obj.strftime('%d/%m/%Y')} (jam: 12:00){Style.RESET_ALL}")
            else:
                # Tidak ditemukan format, tanya user
                result = ask_user_for_single_file(filename)
                if result:
                    datetime_obj, apply_to_all_flag = result
                    if apply_to_all_flag:
                        apply_to_all = True
                        batch_date = datetime_obj
                else:
                    skip_file = True
        
        # MODE CONFIRM: Konfirmasi satu per satu
        elif processing_mode == "confirm":
            datetime_obj, has_time = smart_extract_datetime(filename, is_video)
            
            if datetime_obj:
                if has_time:
                    print(f"{Fore.GREEN}  📅 Ditemukan: {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  📅 Ditemukan (hanya tanggal): {datetime_obj.strftime('%d/%m/%Y')} (jam: 12:00){Style.RESET_ALL}")
                
                # Tanya konfirmasi
                print(f"{Fore.CYAN}  Apakah tanggal ini benar?{Style.RESET_ALL}")
                print(f"  [1] Ya, gunakan tanggal ini")
                print(f"  [2] Tidak, input tanggal lain")
                print(f"  [3] Skip file ini")
                
                confirm = input(f"{Fore.GREEN}Pilihan (1-3): {Style.RESET_ALL}").strip()
                
                if confirm == "1":
                    # Gunakan tanggal yang ditemukan
                    pass
                elif confirm == "2":
                    # Input manual
                    while True:
                        print(f"\n{Fore.CYAN}Input manual untuk: {filename}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
                        
                        user_input = input(f"{Fore.GREEN}Masukkan tanggal (dan jam): {Style.RESET_ALL}").strip()
                        
                        try:
                            if ":" in user_input and len(user_input) > 10:
                                datetime_obj = datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
                            else:
                                date_only = datetime.strptime(user_input, "%d/%m/%Y")
                                datetime_obj = datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0)
                            break
                        except ValueError:
                            print(f"{Fore.RED}❌ Format salah!{Style.RESET_ALL}")
                            continue
                elif confirm == "3":
                    skip_file = True
                else:
                    print(f"{Fore.RED}  ❌ Pilihan tidak valid, skip file{Style.RESET_ALL}")
                    skip_file = True
            else:
                # Tidak ditemukan format
                result = ask_user_for_single_file(filename)
                if result:
                    datetime_obj, apply_to_all_flag = result
                    if apply_to_all_flag:
                        apply_to_all = True
                        batch_date = datetime_obj
                else:
                    skip_file = True
        
        # Skip file jika diperlukan
        if skip_file:
            print(f"{Fore.YELLOW}  ⏭️  File di-skip{Style.RESET_ALL}")
            skipped_count += 1
            continue
        
        if not datetime_obj:
            print(f"{Fore.YELLOW}  ⏭️  File di-skip{Style.RESET_ALL}")
            skipped_count += 1
            continue
        
        # Tentukan tool yang akan digunakan
        file_ext = os.path.splitext(filename)[1].lower()
        
        if tool_choice == "auto":
            if is_video:
                if exif_available:
                    selected_tool = "exiftool"
                elif ffmpeg_available:
                    selected_tool = "ffmpeg"
                else:
                    selected_tool = "basic"
            else:
                selected_tool = "exiftool" if exif_available else "basic"
        else:
            selected_tool = tool_choice
        
        # Update metadata dengan tool yang dipilih
        success = False
        
        if selected_tool == "exiftool" and exif_available and exiftool_path:
            success = update_metadata_exif(exiftool_path, file_path, datetime_obj)
            if success:
                print(f"{Fore.GREEN}  ✅ Metadata diupdate (ExifTool){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ❌ Gagal update metadata{Style.RESET_ALL}")
        
        elif selected_tool == "ffmpeg" and ffmpeg_available and ffmpeg_path and is_video:
            success = update_metadata_ffmpeg(ffmpeg_path, file_path, datetime_obj, output_folder)
            if success:
                print(f"{Fore.GREEN}  ✅ Metadata diupdate (FFmpeg){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ❌ Gagal update metadata{Style.RESET_ALL}")
        
        elif selected_tool == "basic":
            success = update_timestamps_basic(file_path, datetime_obj)
            if success:
                print(f"{Fore.GREEN}  ✅ Timestamp file diupdate{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ❌ Gagal update timestamp{Style.RESET_ALL}")
        
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
    
    checker = ToolChecker()
    exif_available, exiftool_path, exif_version = checker.check_exiftool()
    ffmpeg_available, ffmpeg_path, ffmpeg_version = checker.check_ffmpeg()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(header_ascii)
        
        print(f"{Fore.CYAN}=== SMART METADATA EXTRACTOR ==={Style.RESET_ALL}")
        
        if exif_available:
            print(f"{Fore.GREEN}✅ ExifTool: {exif_version}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ ExifTool: Tidak ditemukan{Style.RESET_ALL}")
        
        if ffmpeg_available:
            print(f"{Fore.GREEN}✅ FFmpeg: {ffmpeg_version}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  FFmpeg: Tidak ditemukan (opsional){Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}=== METATIMECHANGER v2.0 ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}   (Multiple Processing Modes){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print("[1] 📹 Update Video Files")
        print("[2] 📸 Update Photo Files")
        print("[3] ⚙️  Settings & Testing")
        print("[4] 🚪 Exit")
        
        try:
            choice = input(f"\n{Fore.YELLOW}Pilih menu (1-4): {Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Program dihentikan.{Style.RESET_ALL}")
            break
        
        if choice == "1":
            process_videos_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
        elif choice == "2":
            process_photos_menu(exif_available, exiftool_path)
        elif choice == "3":
            settings_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
        elif choice == "4":
            print(f"\n{Fore.GREEN}👋 Terima kasih! Sampai jumpa.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def process_videos_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Menu proses video"""
    print(f"\n{Fore.CYAN}=== PROSES FILE VIDEO ==={Style.RESET_ALL}")
    
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
    print("[1] Auto Fast (rekomendasi)")
    print("    • Otomatis ekstrak tanggal dari nama file")
    print("    • Hanya tanya jika format tidak ditemukan")
    print("    • Cepat dan efisien")
    
    print("\n[2] Confirm One-by-One")
    print("    • Konfirmasi setiap file")
    print("    • Aman tapi lebih lambat")
    
    print("\n[3] Batch Same Date")
    print("    • Tanggal sama untuk semua file")
    print("    • Input tanggal satu kali")
    
    mode_choice = input(f"\n{Fore.YELLOW}Pilih mode (1-3): {Style.RESET_ALL}").strip()
    
    if mode_choice == "1":
        processing_mode = "auto"
    elif mode_choice == "2":
        processing_mode = "confirm"
    elif mode_choice == "3":
        processing_mode = "batch"
    else:
        print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")
        return
    
    # Pilihan tool
    print(f"\n{Fore.CYAN}=== PILIHAN TOOL ==={Style.RESET_ALL}")
    print("[1] Auto (rekomendasi)")
    print("[2] ExifTool (cepat, metadata only)")
    print("[3] FFmpeg (lebih compatible)")
    print("[4] Basic (hanya timestamp)")
    
    tool_choice = input(f"{Fore.YELLOW}Pilih tool (1-4): {Style.RESET_ALL}").strip()
    
    if tool_choice == "2" and exif_available:
        selected_tool = "exiftool"
    elif tool_choice == "3" and ffmpeg_available:
        selected_tool = "ffmpeg"
    elif tool_choice == "4":
        selected_tool = "basic"
    else:
        selected_tool = "auto"
    
    print(f"\n{Fore.YELLOW}⏳ Memproses video dengan mode {processing_mode}...{Style.RESET_ALL}")
    process_files_with_options(folder, output, processing_mode, is_video=True, 
                               exiftool_path=exiftool_path, ffmpeg_path=ffmpeg_path,
                               exif_available=exif_available, ffmpeg_available=ffmpeg_available,
                               tool_choice=selected_tool)
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def process_photos_menu(exif_available, exiftool_path):
    """Menu proses foto"""
    print(f"\n{Fore.CYAN}=== PROSES FILE FOTO ==={Style.RESET_ALL}")
    
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
    print("[1] Auto Fast (rekomendasi)")
    print("[2] Confirm One-by-One")
    print("[3] Batch Same Date")
    
    mode_choice = input(f"{Fore.YELLOW}Pilih mode (1-3): {Style.RESET_ALL}").strip()
    
    if mode_choice == "1":
        processing_mode = "auto"
    elif mode_choice == "2":
        processing_mode = "confirm"
    elif mode_choice == "3":
        processing_mode = "batch"
    else:
        print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.YELLOW}⏳ Memproses foto dengan mode {processing_mode}...{Style.RESET_ALL}")
    process_files_with_options(folder, output, processing_mode, is_video=False, 
                               exiftool_path=exiftool_path, ffmpeg_path=None,
                               exif_available=exif_available, ffmpeg_available=False,
                               tool_choice="exiftool" if exif_available else "basic")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def settings_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Menu pengaturan"""
    while True:
        print(f"\n{Fore.CYAN}=== PENGATURAN & TESTING ==={Style.RESET_ALL}")
        print("[1] Test ExifTool")
        print("[2] Test FFmpeg")
        print("[3] Test Smart Extraction")
        print("[4] Info Format yang Didukung")
        print("[5] Kembali ke Menu Utama")
        
        choice = input(f"{Fore.YELLOW}Pilih (1-5): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            test_exiftool(exif_available, exiftool_path)
        elif choice == "2":
            test_ffmpeg(ffmpeg_available, ffmpeg_path)
        elif choice == "3":
            test_smart_extraction()
        elif choice == "4":
            show_format_info()
        elif choice == "5":
            break
        else:
            print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")

def test_smart_extraction():
    """Test smart extraction dengan contoh file"""
    print(f"\n{Fore.CYAN}=== TEST SMART EXTRACTION ==={Style.RESET_ALL}")
    
    test_files = [
        "Vid 20210327 092658.mp4",  # Format dengan SPASI
        "VID_20231225_143045.mp4",  # Format standar
        "lv_0_20231225143045.mp4",  # Prefix aneh
        "holiday_20231225_143045(1).mp4",  # Suffix
        "IMG-20231225-WA143045.jpg",  # WhatsApp
        "my_photo_20231225.jpg",  # Hanya tanggal
    ]
    
    for filename in test_files:
        print(f"\n{Fore.CYAN}Testing: {filename}{Style.RESET_ALL}")
        datetime_obj, has_time = smart_extract_datetime(filename, True)
        
        if datetime_obj:
            if has_time:
                print(f"{Fore.GREEN}  ✅ Ditemukan: {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}  ⚠️  Hanya tanggal: {datetime_obj.strftime('%d/%m/%Y')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ❌ Tidak ditemukan{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def test_exiftool(exif_available, exiftool_path):
    """Test ExifTool"""
    print(f"\n{Fore.CYAN}=== TEST EXIFTOOL ==={Style.RESET_ALL}")
    
    if exif_available:
        print(f"{Fore.GREEN}✅ ExifTool tersedia{Style.RESET_ALL}")
        print(f"Path: {exiftool_path}")
        
        try:
            result = subprocess.run([exiftool_path, '-ver'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"Versi: {result.stdout.strip()}")
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ ExifTool tidak ditemukan!{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def test_ffmpeg(ffmpeg_available, ffmpeg_path):
    """Test FFmpeg"""
    print(f"\n{Fore.CYAN}=== TEST FFMPEG ==={Style.RESET_ALL}")
    
    if ffmpeg_available:
        print(f"{Fore.GREEN}✅ FFmpeg tersedia{Style.RESET_ALL}")
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
        print(f"{Fore.YELLOW}⚠️  FFmpeg tidak ditemukan!{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def show_format_info():
    """Tampilkan info format yang didukung"""
    print(f"\n{Fore.CYAN}=== FORMAT YANG DIDUKUNG ==={Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🎯 CONTOH FILE YANG BISA DIEKSTRAK OTOMATIS:{Style.RESET_ALL}")
    print("• Vid 20210327 092658.mp4 (format dengan spasi)")
    print("• VID_20231225_143045.mp4 (format standar)")
    print("• IMG_20231225_143045.jpg")
    print("• lv_0_20231225143045.mp4 (prefix aneh)")
    print("• holiday_20231225_143045(1).mp4 (ada suffix)")
    print("• IMG-20231225-WA143045.jpg (WhatsApp)")
    print("• 20231225_143045_backup.png")
    
    print(f"\n{Fore.YELLOW}⚡ MODE AUTO FAST:{Style.RESET_ALL}")
    print("• Program otomatis ekstrak tanggal dari nama file")
    print("• Tidak tanya konfirmasi jika format valid")
    print("• Hanya tanya jika format tidak ditemukan")
    print("• Cepat dan efisien untuk banyak file")
    
    print(f"\n{Fore.YELLOW}🔍 MODE CONFIRM:{Style.RESET_ALL}")
    print("• Konfirmasi setiap file satu per satu")
    print("• Aman untuk file penting")
    print("• Bisa koreksi jika ekstraksi salah")
    
    print(f"\n{Fore.YELLOW}📅 MODE BATCH:{Style.RESET_ALL}")
    print("• Tanggal sama untuk semua file")
    print("• Input tanggal satu kali")
    print("• Cocok untuk file tanpa format tanggal")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        print(f"{Fore.CYAN}🚀 Memulai MetaTimeChanger v2.0...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   (Multiple Processing Modes){Style.RESET_ALL}")
        time.sleep(1)
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Program dihentikan{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
