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
    f"{Fore.YELLow}██║╚██╔╝██║██╔══╝░░░░░██║░░░██╔══██║\n"
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
        
        print(f"{Fore.CYAN}  📅 Akan diupdate ke: {new_datetime.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  🔧 Menggunakan: ExifTool{Style.RESET_ALL}")
        
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
    """Update metadata video dengan FFmpeg"""
    try:
        date_str = new_datetime.strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(file_path)
        
        print(f"{Fore.CYAN}  📅 Akan diupdate ke: {new_datetime.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  🔧 Menggunakan: FFmpeg{Style.RESET_ALL}")
        
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
                
                print(f"{Fore.GREEN}  ✅ Video metadata diupdate: {filename}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}  ❌ File output tidak valid: {filename}{Style.RESET_ALL}")
                return False
        else:
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

def extract_datetime_from_filename_advanced(filename, is_video=True):
    """
    Ekstrak tanggal DAN JAM dari nama file dengan cara CERDAS
    Mencari pola YYYYMMDD_HHMMSS di mana saja dalam nama file
    """
    filename_without_ext = os.path.splitext(filename)[0]
    
    # PATTERN 1: YYYYMMDD_HHMMSS (format standar dengan underscore)
    pattern1 = r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})'
    
    # PATTERN 2: YYYYMMDDHHMMSS (tanpa underscore)
    pattern2 = r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})'
    
    # PATTERN 3: YYYY-MM-DD HH-MM-SS atau YYYY-MM-DD_HH-MM-SS
    pattern3 = r'(\d{4})-(\d{2})-(\d{2})[ _](\d{2})-(\d{2})-(\d{2})'
    
    # PATTERN 4: YYYY.MM.DD HH.MM.SS atau YYYY.MM.DD_HH.MM.SS
    pattern4 = r'(\d{4})\.(\d{2})\.(\d{2})[ _](\d{2})\.(\d{2})\.(\d{2})'
    
    patterns = [
        (pattern1, '_'),   # Pattern dengan underscore
        (pattern2, ''),    # Pattern tanpa separator
        (pattern3, '-'),   # Pattern dengan dash
        (pattern4, '.'),   # Pattern dengan dot
    ]
    
    for pattern, separator in patterns:
        matches = list(re.finditer(pattern, filename_without_ext))
        
        if matches:
            # Ambil match terakhir (biasanya yang paling relevan)
            match = matches[-1]
            
            try:
                if separator == '_' or separator == '':
                    # Pattern 1 atau 2
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    hour = int(match.group(4))
                    minute = int(match.group(5))
                    second = int(match.group(6))
                else:
                    # Pattern 3 atau 4
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    hour = int(match.group(4))
                    minute = int(match.group(5))
                    second = int(match.group(6))
                
                # Coba buat datetime object
                datetime_obj = datetime(year, month, day, hour, minute, second)
                
                # Tampilkan pola yang ditemukan
                found_pattern = match.group(0)
                print(f"{Fore.GREEN}  🔍 Pola ditemukan: {found_pattern}{Style.RESET_ALL}")
                
                return datetime_obj, True
                
            except ValueError:
                # Tanggal tidak valid, coba pattern lain
                continue
    
    # Jika tidak ditemukan pattern lengkap, coba cari hanya tanggal (YYYYMMDD)
    date_only_patterns = [
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{4})\.(\d{2})\.(\d{2})',  # YYYY.MM.DD
    ]
    
    for pattern in date_only_patterns:
        matches = list(re.finditer(pattern, filename_without_ext))
        if matches:
            match = matches[-1]  # Ambil yang terakhir
            
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                
                # Buat datetime dengan jam default 12:00
                datetime_obj = datetime(year, month, day, 12, 0, 0)
                
                found_pattern = match.group(0)
                print(f"{Fore.YELLOW}  🔍 Hanya tanggal ditemukan: {found_pattern} (jam: 12:00){Style.RESET_ALL}")
                
                return datetime_obj, False
                
            except ValueError:
                continue
    
    return None, False

def smart_extract_datetime(filename, is_video=True):
    """
    Fungsi cerdas untuk ekstrak datetime dari berbagai format file
    """
    filename_without_ext = os.path.splitext(filename)[0]
    
    print(f"{Fore.CYAN}  🤖 Menganalisis: {filename}{Style.RESET_ALL}")
    
    # Coba ekstrak dengan metode advanced terlebih dahulu
    datetime_obj, has_time = extract_datetime_from_filename_advanced(filename, is_video)
    
    if datetime_obj:
        return datetime_obj, has_time
    
    # Jika metode advanced gagal, coba cari pola umum
    common_patterns = [
        # WhatsApp pattern
        (r'IMG-(\d{8})-WA(\d{6})', '%Y%m%d', '%H%M%S'),
        (r'VID-(\d{8})-WA(\d{6})', '%Y%m%d', '%H%M%S'),
        (r'PTT-(\d{8})-WA(\d{6})', '%Y%m%d', '%H%M%S'),
        
        # Google Pixel pattern
        (r'PXL_(\d{8})_(\d{6})', '%Y%m%d', '%H%M%S'),
        
        # Samsung pattern
        (r'Screenshot_(\d{8})-(\d{6})', '%Y%m%d', '%H%M%S'),
        (r'Screenrecorder_(\d{8})-(\d{6})', '%Y%m%d', '%H%M%S'),
        
        # Huawei pattern
        (r'HUAWEI_(\d{8})_(\d{6})', '%Y%m%d', '%H%M%S'),
        
        # MIUI/Xiaomi pattern
        (r'MIUI_(\d{8})_(\d{6})', '%Y%m%d', '%H%M%S'),
        (r'Xiaomi_(\d{8})_(\d{6})', '%Y%m%d', '%H%M%S'),
    ]
    
    for pattern, date_fmt, time_fmt in common_patterns:
        match = re.match(pattern, filename_without_ext)
        if match:
            try:
                date_str = match.group(1)
                time_str = match.group(2)
                
                date_part = datetime.strptime(date_str, date_fmt)
                time_part = datetime.strptime(time_str, time_fmt)
                
                datetime_obj = datetime(
                    date_part.year, date_part.month, date_part.day,
                    time_part.hour, time_part.minute, time_part.second
                )
                
                print(f"{Fore.GREEN}  🔍 Pattern khusus ditemukan: {pattern}{Style.RESET_ALL}")
                return datetime_obj, True
            except ValueError:
                continue
    
    # Coba cari angka 14-digit (YYYYMMDDHHMMSS) di mana saja
    digit_pattern = r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})'
    matches = list(re.finditer(digit_pattern, filename_without_ext))
    
    for match in matches:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            hour = int(match.group(4))
            minute = int(match.group(5))
            second = int(match.group(6))
            
            datetime_obj = datetime(year, month, day, hour, minute, second)
            
            print(f"{Fore.GREEN}  🔍 14-digit ditemukan: {match.group(0)}{Style.RESET_ALL}")
            return datetime_obj, True
            
        except ValueError:
            continue
    
    return None, False

def ask_user_for_datetime(filename, extracted_date=None, suggestions=None):
    """Tanya user untuk input tanggal dengan opsi yang cerdas"""
    print(f"\n{Fore.YELLOW}⚠️  Format tanggal tidak dikenali untuk file: {filename}{Style.RESET_ALL}")
    
    options = []
    
    if extracted_date:
        options.append(("1", f"Gunakan tanggal yang terdeteksi: {extracted_date.strftime('%d/%m/%Y %H:%M:%S')}"))
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, start=2):
            options.append((str(i), f"Saran {i-1}: {suggestion.strftime('%d/%m/%Y %H:%M:%S')}"))
    
    # Tentukan starting index untuk manual input
    manual_index = len(options) + 1
    options.append((str(manual_index), "Input tanggal manual"))
    
    skip_index = manual_index + 1
    options.append((str(skip_index), "Skip file ini"))
    
    # Tampilkan semua opsi
    for num, desc in options:
        print(f"  [{num}] {desc}")
    
    while True:
        choice = input(f"{Fore.GREEN}Pilihan (1-{skip_index}): {Style.RESET_ALL}").strip()
        
        if choice == "1" and extracted_date:
            return extracted_date
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, start=2):
                if choice == str(i):
                    return suggestion
        
        if choice == str(manual_index):
            # Input manual
            while True:
                print(f"\n{Fore.CYAN}📅 Manual input untuk: {filename}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Format: DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Contoh: 25/12/2023 14:30:45{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Note: Jam bisa dikosongkan (default: 12:00:00){Style.RESET_ALL}")
                
                user_input = input(f"{Fore.GREEN}Masukkan tanggal (dan jam): {Style.RESET_ALL}").strip()
                
                if not user_input:
                    print(f"{Fore.YELLOW}  ⏭️  Kembali ke pilihan{Style.RESET_ALL}")
                    break
                
                try:
                    if ":" in user_input and len(user_input) > 10:
                        return datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
                    else:
                        date_only = datetime.strptime(user_input, "%d/%m/%Y")
                        return datetime(date_only.year, date_only.month, date_only.day, 12, 0, 0)
                except ValueError:
                    print(f"{Fore.RED}❌ Format salah! Gunakan DD/MM/YYYY HH:MM:SS{Style.RESET_ALL}")
                    continue
        
        if choice == str(skip_index):
            return None
        
        print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")

def generate_smart_suggestions(filename):
    """Generate saran cerdas berdasarkan nama file"""
    suggestions = []
    filename_without_ext = os.path.splitext(filename)[0]
    
    # Cari semua kemungkinan tanggal
    date_patterns = [
        r'(\d{2})[-._](\d{2})[-._](\d{4})',  # DD-MM-YYYY
        r'(\d{4})[-._](\d{2})[-._](\d{2})',  # YYYY-MM-DD
        r'(\d{2})(\d{2})(\d{4})',  # DDMMYYYY
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
    ]
    
    for pattern in date_patterns:
        matches = list(re.finditer(pattern, filename_without_ext))
        for match in matches:
            try:
                if pattern == r'(\d{2})[-._](\d{2})[-._](\d{4})':
                    # DD-MM-YYYY
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                elif pattern == r'(\d{4})[-._](\d{2})[-._](\d{2})':
                    # YYYY-MM-DD
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                elif pattern == r'(\d{2})(\d{2})(\d{4})':
                    # DDMMYYYY
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))
                else:
                    # YYYYMMDD
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                
                # Cek validitas
                if 1 <= month <= 12 and 1 <= day <= 31 and 2000 <= year <= 2100:
                    datetime_obj = datetime(year, month, day, 12, 0, 0)
                    if datetime_obj not in suggestions:
                        suggestions.append(datetime_obj)
                        
            except (ValueError, IndexError):
                continue
    
    # Cari dari angka yang ada di filename (misal: lv_0_20231225143045)
    digit_groups = re.findall(r'\d+', filename_without_ext)
    for digits in digit_groups:
        if len(digits) >= 8:
            # Coba sebagai YYYYMMDD
            try:
                if len(digits) >= 8:
                    year = int(digits[0:4])
                    month = int(digits[4:6])
                    day = int(digits[6:8])
                    
                    if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                        datetime_obj = datetime(year, month, day, 12, 0, 0)
                        if datetime_obj not in suggestions:
                            suggestions.append(datetime_obj)
            except ValueError:
                continue
    
    return suggestions[:3]  # Return maksimal 3 saran

def process_files(folder_path, output_folder, manual=False, is_video=True, 
                  exiftool_path=None, ffmpeg_path=None, exif_available=False, 
                  ffmpeg_available=False, tool_choice="auto"):
    """Memproses semua file dalam folder - CERDAS dan INTERAKTIF"""
    
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
    
    for idx, (filename, file_path) in enumerate(files, 1):
        print(f"\n{Fore.CYAN}[{idx}/{len(files)}] {filename}{Style.RESET_ALL}")
        
        datetime_obj = None
        
        if manual:
            # Mode manual - tanya user dengan saran cerdas
            suggestions = generate_smart_suggestions(filename)
            datetime_obj = ask_user_for_datetime(filename, suggestions=suggestions)
            if not datetime_obj:
                print(f"{Fore.YELLOW}  ⏭️  File di-skip{Style.RESET_ALL}")
                skipped_count += 1
                continue
        else:
            # Mode otomatis - coba ekstrak dengan metode cerdas
            datetime_obj, has_time = smart_extract_datetime(filename, is_video)
            
            if datetime_obj:
                if has_time:
                    print(f"{Fore.GREEN}  📅 Tanggal & Jam ditemukan: {datetime_obj.strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  📅 Hanya tanggal ditemukan: {datetime_obj.strftime('%d/%m/%Y')} (jam: 12:00){Style.RESET_ALL}")
                
                # Tanya konfirmasi ke user
                print(f"{Fore.CYAN}  Apakah tanggal ini benar?{Style.RESET_ALL}")
                print(f"  [1] Ya, gunakan tanggal ini")
                print(f"  [2] Tidak, pilih tanggal lain")
                print(f"  [3] Skip file ini")
                
                confirm = input(f"{Fore.GREEN}Pilihan (1-3): {Style.RESET_ALL}").strip()
                
                if confirm == "1":
                    # Lanjutkan dengan tanggal yang ditemukan
                    pass
                elif confirm == "2":
                    # Tanya user untuk pilih tanggal lain
                    suggestions = generate_smart_suggestions(filename)
                    suggestions.insert(0, datetime_obj)  # Tambahkan yang terdeteksi sebagai opsi pertama
                    datetime_obj = ask_user_for_datetime(filename, extracted_date=datetime_obj, suggestions=suggestions[1:])
                    
                    if not datetime_obj:
                        print(f"{Fore.YELLOW}  ⏭️  File di-skip{Style.RESET_ALL}")
                        skipped_count += 1
                        continue
                elif confirm == "3":
                    print(f"{Fore.YELLOW}  ⏭️  File di-skip{Style.RESET_ALL}")
                    skipped_count += 1
                    continue
                else:
                    print(f"{Fore.RED}  ❌ Pilihan tidak valid, skip file{Style.RESET_ALL}")
                    skipped_count += 1
                    continue
            else:
                # Tidak ditemukan tanggal sama sekali
                print(f"{Fore.YELLOW}  ⚠️  Tidak bisa menemukan pola tanggal{Style.RESET_ALL}")
                suggestions = generate_smart_suggestions(filename)
                datetime_obj = ask_user_for_datetime(filename, suggestions=suggestions)
                
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
        
        elif selected_tool == "ffmpeg" and ffmpeg_available and ffmpeg_path and is_video:
            success = update_metadata_ffmpeg(ffmpeg_path, file_path, datetime_obj, output_folder)
        
        elif selected_tool == "basic":
            success = update_timestamps_basic(file_path, datetime_obj)
        
        if success:
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
        
        print(f"\n{Fore.CYAN}=== GOOGLE PHOTOS METADATA UPDATER ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}   (Mode Cerdas - Tidak peduli prefix/suffix){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        print("[1] 📹 Update Video Files")
        print("[2] 📸 Update Photo Files")
        print("[3] 🧠 Test Smart Extraction")
        print("[4] ⚙️  Settings")
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
            test_smart_extraction()
        elif choice == "4":
            settings_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path)
        elif choice == "5":
            print(f"\n{Fore.GREEN}👋 Terima kasih! Sampai jumpa.{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

def process_videos_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Menu proses video"""
    print(f"\n{Fore.CYAN}=== PROSES FILE VIDEO (Mode Cerdas) ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🎯 Bisa handle berbagai format:{Style.RESET_ALL}")
    print("• VID_YYYYMMDD_HHMMSS.mp4")
    print("• lv_0_20231225143045.mp4")
    print("• holiday_20231225_143045(1).mp4")
    print("• YYYYMMDD_HHMMSS_backup.mp4")
    print("• video_2023-12-25_14-30-45_final.mp4")
    
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
    print("[1] Otomatis Cerdas (rekomendasi)")
    print("    - Ekstrak otomatis dari nama file")
    print("    - Konfirmasi ke user")
    print("[2] Manual Interaktif")
    print("    - Tanya setiap file dengan saran")
    
    mode = input(f"{Fore.YELLOW}Pilih mode (1-2): {Style.RESET_ALL}").strip()
    manual_mode = mode == "2"
    
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
    
    print(f"\n{Fore.YELLOW}⏳ Memproses video dengan mode cerdas...{Style.RESET_ALL}")
    process_files(folder, output, manual=manual_mode, is_video=True, 
                 exiftool_path=exiftool_path, ffmpeg_path=ffmpeg_path,
                 exif_available=exif_available, ffmpeg_available=ffmpeg_available,
                 tool_choice=selected_tool)
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def process_photos_menu(exif_available, exiftool_path):
    """Menu proses foto"""
    print(f"\n{Fore.CYAN}=== PROSES FILE FOTO (Mode Cerdas) ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🎯 Bisa handle berbagai format:{Style.RESET_ALL}")
    print("• IMG_YYYYMMDD_HHMMSS.jpg")
    print("• photo_20231225_143045_edit.jpg")
    print("• 20231225_143045_screenshot.jpg")
    print("• DSC_20231225143045.jpg")
    
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
    print("[1] Otomatis Cerdas (rekomendasi)")
    print("[2] Manual Interaktif")
    
    mode = input(f"{Fore.YELLOW}Pilih mode (1-2): {Style.RESET_ALL}").strip()
    manual_mode = mode == "2"
    
    print(f"\n{Fore.YELLOW}⏳ Memproses foto dengan mode cerdas...{Style.RESET_ALL}")
    process_files(folder, output, manual=manual_mode, is_video=False, 
                 exiftool_path=exiftool_path, ffmpeg_path=None,
                 exif_available=exif_available, ffmpeg_available=False,
                 tool_choice="exiftool" if exif_available else "basic")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

def test_smart_extraction():
    """Test smart extraction dengan contoh file"""
    print(f"\n{Fore.CYAN}=== TEST SMART EXTRACTION ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Contoh file yang bisa dihandle:{Style.RESET_ALL}")
    
    test_files = [
        "VID_20231225_143045.mp4",
        "lv_0_20231225143045.mp4",
        "holiday_20231225_143045(1).mp4",
        "YYYYMMDD_HHMMSS_backup.mp4",
        "video_2023-12-25_14-30-45_final.mp4",
        "IMG-20231225-WA143045.jpg",
        "PXL_20231225_143045.jpg",
        "Screenshot_20231225-143045.png",
        "my_photo_20231225143045_edit.jpg",
        "DSC_20231225_143045.jpg",
        "2023.12.25_14.30.45_vacation.mp4",
        "recording_2023-12-25 14-30-45.mov",
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

def settings_menu(exif_available, ffmpeg_available, exiftool_path, ffmpeg_path):
    """Menu pengaturan"""
    while True:
        print(f"\n{Fore.CYAN}=== PENGATURAN ==={Style.RESET_ALL}")
        print("[1] Test ExifTool")
        print("[2] Test FFmpeg")
        print("[3] Info Format yang Didukung")
        print("[4] Kembali ke Menu Utama")
        
        choice = input(f"{Fore.YELLOW}Pilih (1-4): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            test_exiftool(exif_available, exiftool_path)
        elif choice == "2":
            test_ffmpeg(ffmpeg_available, ffmpeg_path)
        elif choice == "3":
            show_format_info()
        elif choice == "4":
            break
        else:
            print(f"{Fore.RED}❌ Pilihan tidak valid!{Style.RESET_ALL}")

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
    print(f"\n{Fore.CYAN}=== FORMAT YANG DIDUKUNG (Mode Cerdas) ==={Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🎯 POLA UTAMA YANG DICARI:{Style.RESET_ALL}")
    print("• YYYYMMDD_HHMMSS (dengan underscore)")
    print("• YYYYMMDDHHMMSS (tanpa underscore)")
    print("• YYYY-MM-DD HH-MM-SS")
    print("• YYYY.MM.DD HH.MM.SS")
    
    print(f"\n{Fore.YELLOW}📝 CONTOH FILE YANG BISA DIHANDLE:{Style.RESET_ALL}")
    print("1. Standard:")
    print("   • VID_20231225_143045.mp4")
    print("   • IMG_20231225_143045.jpg")
    
    print("\n2. Dengan prefix/suffix:")
    print("   • lv_0_20231225143045.mp4")
    print("   • holiday_20231225_143045(1).mp4")
    print("   • YYYYMMDD_HHMMSS_backup.mp4")
    
    print("\n3. Format berbeda:")
    print("   • video_2023-12-25_14-30-45_final.mp4")
    print("   • 2023.12.25_14.30.45_vacation.mp4")
    print("   • recording_2023-12-25 14-30-45.mov")
    
    print("\n4. Format spesifik device:")
    print("   • IMG-20231225-WA143045.jpg (WhatsApp)")
    print("   • PXL_20231225_143045.jpg (Google Pixel)")
    print("   • Screenshot_20231225-143045.png (Samsung)")
    
    print(f"\n{Fore.GREEN}✅ Program akan mencari pola YYYYMMDD_HHMMSS")
    print("   di MANA SAJA dalam nama file!{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Tekan Enter...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        print(f"{Fore.CYAN}🚀 Memulai SMART Google Photos Metadata Updater...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   (Mode Cerdas - Tidak peduli prefix/suffix){Style.RESET_ALL}")
        time.sleep(1)
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Program dihentikan{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")