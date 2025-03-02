import os
import re
import subprocess
import sys
import time
from datetime import datetime

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

# Header ASCII dengan warna kuning solid
header_ascii = (
    f"{Fore.YELLOW}███╗░░░███╗███████╗████████╗░█████╗░\n"
    f"{Fore.YELLOW}████╗░████║██╔════╝╚══██╔══╝██╔══██╗\n"
    f"{Fore.YELLOW}██╔████╔██║█████╗░░░░░██║░░░███████║\n"
    f"{Fore.YELLOW}██║╚██╔╝██║██╔══╝░░░░░██║░░░██╔══██║\n"
    f"{Fore.YELLOW}██║░╚═╝░██║███████╗░░░██║░░░██║░░██║\n"
    f"{Fore.YELLOW}╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░╚═╝{Style.RESET_ALL}\n"
)

def update_timestamps(file_path, new_date, output_folder, filename, move_files=True):
    """Mengubah date modified dan date created sesuai dengan format"""
    new_timestamp = time.mktime(new_date.timetuple())
    os.utime(file_path, (new_timestamp, new_timestamp))
    print(f"Timestamps updated for {file_path} -> {new_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Pindahkan file ke folder output jika diperlukan
    if move_files:
        new_file_path = os.path.join(output_folder, filename)
        import shutil
        shutil.copy2(file_path, new_file_path)
        print(f"File moved to {new_file_path}")

def process_files(folder_path, output_folder, manual=False, is_video=True, move_files=True):
    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        print("Folder kosong atau tidak ditemukan! Pastikan path sudah benar dan ada file di dalamnya.")
        return
    """Memproses semua file dalam folder dengan metode otomatis atau manual, meminta input user satu per satu dalam mode manual"""
    """Memproses semua file dalam folder dengan metode otomatis atau manual"""
    video_pattern = re.compile(r"VID_(\d{8})_\d{6}\.mp4")
    image_pattern = re.compile(r"IMG_(\d{8})_\d{6}\.(jpg|jpeg|png)")
    pattern = video_pattern if is_video else image_pattern
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        
        if manual:
            while True:
                print(f"{filename} > DD/MM/YYYY")
                date_input = input("Masukkan tanggal baru (DD/MM/YYYY): ")
                try:
                    new_date = datetime.strptime(date_input, "%d/%m/%Y")
                    break
                except ValueError:
                    print("Format tanggal salah! Harap masukkan dalam format DD/MM/YYYY.")
        else:
            match = pattern.match(filename)
            if match:
                date_str = match.group(1)
                new_date = datetime.strptime(date_str, "%Y%m%d")
            else:
                continue
        match = pattern.match(filename)
        if match and not manual:
            date_str = match.group(1)
            new_date = datetime.strptime(date_str, "%Y%m%d")
        else:
            while True:
                print(f"{filename} > DD/MM/YYYY")
                date_input = input("Masukkan tanggal baru (YYYY/MM/DD): ")
                try:
                    new_date = datetime.strptime(date_input, "%Y/%m/%d")
                    break
                except ValueError:
                    print("Format tanggal salah! Harap masukkan dalam format YYYY/MM/DD.")

        file_path = os.path.join(folder_path, filename)
        update_timestamps(file_path, new_date, output_folder, filename, move_files)

def main_menu():
    while True:
        print(header_ascii)
        print("[1] Change Date Metadata Videos")
        print("[2] Change Date Metadata Images")
        print("[3] Exit\n")
        print("Pilih angka untuk melanjutkan:\n")
        choice = input(">>> ")
        
        if choice in ["1", "2"]:
            folder_path = input("Masukkan path folder input: ")
            output_folder = input("Masukkan path folder output: ")
            is_video = choice == "1"
            
            while True:
                print("\n[1] Automatic Based On Format")
                print("[2] Manual Formatting")
                print("[3] Back")
                sub_choice = input(">>> ")
                
                if sub_choice == "1":
                    process_files(folder_path, output_folder, manual=False, is_video=is_video)
                    break
                elif sub_choice == "2":
                    process_files(folder_path, output_folder, manual=True, is_video=is_video)
                    break
                elif sub_choice == "3":
                    break
                else:
                    print("Pilihan tidak valid! Coba lagi.")
        elif choice == "3":
            print("Terima kasih! Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid! Coba lagi.")

if __name__ == "__main__":
    main_menu()
