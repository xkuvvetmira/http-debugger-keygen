# by kuvvetmira
# for > www.darkcrack.com
import winreg
import re
import os
import ctypes
import sys
from colorama import Fore, init

init()

r = Fore.RED
g = Fore.GREEN
y = Fore.YELLOW
rst = Fore.LIGHTBLACK_EX
rs = Fore.RESET

REG_PATH = r"SOFTWARE\MadeForNet\HTTPDebuggerPro"

def get_app_version() -> str:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
            version, _ = winreg.QueryValueEx(key, "AppVer")
            match = re.search(r"(\d+.*)", version)
            if not match:
                raise ValueError("> Registry'de geçerli bir sürüm numarası bulunamadı.")
            parsed_version = match.group(1)
            return parsed_version.replace(".", "")
    except FileNotFoundError:
        print(f"> Hata: Registry anahtarı bulunamadı: HKCU\\{REG_PATH}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"> Registry'den sürüm okunurken bir hata oluştu: {e}", file=sys.stderr)
        sys.exit(1)

def get_serial_number(app_version: str) -> str:
    kernel32 = ctypes.windll.kernel32
    volume_serial_number = ctypes.c_ulong(0)
    
    result = kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p("C:\\"),
        None,
        0,
        ctypes.byref(volume_serial_number),
        None, 0, None, 0
    )

    if result == 0:
        error_code = ctypes.get_last_error()
        print(f"> Hata: C sürücüsünün seri numarası alınamadı. Hata Kodu: {error_code}", file=sys.stderr)
        sys.exit(1)
        
    volume_info = volume_serial_number.value

    try:
        version_as_int = int(app_version)
    except ValueError:
        print(f"> Hata: Geçersiz sürüm numarası formatı: {app_version}", file=sys.stderr)
        sys.exit(1)

    serial_number = version_as_int ^ (((volume_info ^ 0xFFFFFFFF) >> 1) + 0x2E0) ^ 0x590D4
    
    return str(serial_number)

def create_key() -> str:
    v1, v2, v3 = os.urandom(3)
    
    key = (
        f"{v1:02X}"
        f"{v2 ^ 0x7C:02X}"
        f"{0xFF ^ v1:02X}"
        f"7C"
        f"{v2:02X}"
        f"{v3 % 255:02X}"
        f"{(v3 % 255) ^ 7:02X}"
        f"{v1 ^ (0xFF ^ (v3 % 255)):02X}"
    )
    return key

def write_key(sn: str, key: str) -> None:
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as reg_key:
            value_name = "SN" + sn
            winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, key)
            print(f"\n> {g}Crack Başarılı:{rst} Anahtar '{value_name}' registry'ye yazıldı.")
    except Exception as e:
        print(f"> Registry'ye yazılırken bir hata oluştu: {e}", file=sys.stderr)
        print("> Betiği yönetici olarak çalıştırmayı deneyin.", file=sys.stderr)
        sys.exit(1)
        
def crack():
    print(rf"""{r}
 _                           _             _           
| | ___   ___   ____   _____| |_ _ __ ___ (_)_ __ __ _ 
| |/ / | | \ \ / /\ \ / / _ \ __| '_ ` _ \| | '__/ _` |
|   <| |_| |\ V /  \ V /  __/ |_| | | | | | | | | (_| |
|_|\_\\__,_| \_/    \_/ \___|\__|_| |_| |_|_|_|  \__,_|
                    {rs}darkcrack.com{rst}
    """)
    
    app_version = get_app_version()
    print(f">{y} Uygulama Sürümü: {rst}{app_version}")
    
    serial_number = get_serial_number(app_version)
    print(f">{y} Seri Numarası: {rst}{serial_number}")
    
    key = create_key()
    print(f">{y} Oluşturulan Key: {rst}{key}")
    
    write_key(serial_number, key)

if __name__ == "__main__":
    crack()
