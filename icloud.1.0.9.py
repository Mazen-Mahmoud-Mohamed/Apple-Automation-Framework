import ctypes
import datetime
import os
import random
import subprocess
import sys
import time
from datetime import datetime, date, timedelta
import threading
import psutil
import requests
import uiautomator2 as u2
import wmi
from faker import Faker
from termcolor import colored
from colorama import Fore, Style, init
import configparser
from queue import Queue
import base64
from libsrp import Srp, Mode, Client
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import shutil
from uiautomator2.exceptions import UiObjectNotFoundError


from utils import (
    bytes_from_bigint,
    Hash,
    hash as hash_func,
    to_hex,
)


aging_queue = Queue()


# --- Serial Number Functions ---
def getMachine_addr():
    os_type = sys.platform.lower()
    command = "wmic bios get serialnumber"
    return os.popen(command).read().replace("\n", "").replace("    ", "").replace(" ", "")


def get_serial_number():
    try:
        computer_name = ctypes.create_unicode_buffer(256)
        size = ctypes.c_ulong(len(computer_name))
        ctypes.windll.kernel32.GetComputerNameExW(ctypes.c_int(5), computer_name, ctypes.byref(size))
        return computer_name.value
    except Exception as e:
        return f"Error: {str(e)}"


def get_motherboard_serial_number():
    try:
        c = wmi.WMI()
        for item in c.Win32_BaseBoard():
            return item.SerialNumber
    except Exception as e:
        return f"Error: {str(e)}"


def copy2clip(txt):
    cmd = 'echo ' + txt.strip() + '|clip'
    return subprocess.check_call(cmd, shell=True)


# Get Machine Serial Number
serial = getMachine_addr()[12:]
serial_number = get_serial_number()
motherAboard_serial_number = get_motherboard_serial_number()

# Create the final serial code
midpoint1 = len(serial)
midpoint2 = len(serial_number)
midpoint3 = len(motherAboard_serial_number)
serialcode = f"{serial}//{serial_number}//{motherAboard_serial_number}/"

# Check serial code on Pastebin
ser = requests.get('https://pastebin.com/raw/AdaiM8Mk')
sernum = ser.text.find(serialcode)

if sernum != -1:
    print()
else:
    print("You don't have access")
    print(f"{serialcode}")
    copy2clip(serialcode)
    inp = input('Press enter to exit ')
    if inp != "\n":
        sys.exit()
    else:
        sys.exit()

fake = Faker()

# --- Configuration ---
'''LDPLAYER_DIR = r"D:\work\LDPlayer\LDPlayer9"
ADB_PATH = os.path.join(LDPLAYER_DIR, "adb.exe")'''

def find_adb():
    # 1️⃣ حاول من PATH
    adb = shutil.which("adb")
    if adb:
        return adb

    # 2️⃣ أماكن شائعة لـ LDPlayer
    possible_paths = [
        r"C:\LDPlayer\LDPlayer9\adb.exe",
        r"C:\Program Files\LDPlayer\LDPlayer9\adb.exe",
        r"C:\Program Files (x86)\LDPlayer\LDPlayer9\adb.exe",
        r"D:\LDPlayer\LDPlayer9\adb.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


ADB_PATH = find_adb()
if not ADB_PATH:
    print(colored("Fatal: adb not found. Please add adb to PATH or install LDPlayer.", "red"))
    sys.exit(1)


# --- Key code constants ---
KEY_F2 = 131
KEY_DOWN = 20
KEY_TAB = 61
KEY_ESC = 111
KEY_ENTER = 66
KEY_UP = 19
KEY_RIGHT = 22

# Get tomorrow's date and force the year to be 2013
tomorrow = date.today() + timedelta(days=1)
forced_year = tomorrow.replace(year=2013)
if os.name == "nt":
    formatted_tomorrow = forced_year.strftime("%#m/%#d/%Y")
else:
    formatted_tomorrow = forced_year.strftime("%-m/%-d/%Y")


# --- Utility Functions ---
def generate_random_name():
    while True:
        first_name = fake.first_name()
        last_name = fake.last_name()
        if first_name != "Christopher" and last_name != "Christopher":
            return f"{first_name} {last_name}"


def generate_n_digit_number(n=3):
    return random.randint(10 ** (n - 1), 10 ** n - 1)


def display_banner():
    banner = """


███╗   ███╗           ███╗   ███╗
████╗ ████║           ████╗ ████║
██╔████╔██║           ██╔████╔██║
██║╚██╔╝██║           ██║╚██╔╝██║
██║ ╚═╝ ██║    ██╗    ██║ ╚═╝ ██║
╚═╝     ╚═╝    ╚═╝    ╚═╝     ╚═╝

_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
   Discord User:
   (1)   mazenmahmoud6550
   (2)   som3aa2001
_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-    
    """
    print(colored(banner, "red"))



def safe_click(
    d,
    worker_id,
    *,
    resource_id=None,
    text=None,
    retries=10,
    delay=0.6,
    timeout=None   # ✅ جديد
):
    if timeout:
        retries = max(retries, int(timeout / delay))

    for _ in range(retries):
        try:
            if resource_id:
                el = d(resourceId=resource_id)
            elif text:
                el = d(text=text)
            else:
                return False

            if el.exists:
                el.click()
                return True

        except Exception:
            pass

        time.sleep(delay)

    print(colored(f"{worker_id} - Element not found: {resource_id or text}", "yellow"))
    return False


def run_adb(command):
    full_cmd = [ADB_PATH] + command
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=7)
        return result.stdout.strip()
    except Exception as e:
        print(colored(f"Error executing: {' '.join(full_cmd)}", 'red'))
        print(colored(f"Details: {str(e)}", 'blue'))
        return None


def list_emulators():
    output = run_adb(["devices"])
    devices = [line.split("\t")[0] for line in output.split("\n")[1:] if "emulator" in line]
    return devices


#def process_emulator(emulator, accounts, use_random, mazen):
def process_emulator(emulator, emu_name, accounts, use_random, mazen):

    """Function to handle each emulator and process its accounts"""
    #print(colored(f"Started controlling emulator: {emulator}", "green"))
    print(colored(f"Started controlling {emu_name}", "green"))
    for idx, account_data in enumerate(accounts, start=1):
        email = account_data[0]
        account_line = "\t".join(account_data)
        print(colored(f"\n===== Processing account {idx}/{len(accounts)}: {email} in {emu_name} =====", 'green'))
        _, success = automate_account_creation(emulator, emu_name, account_data, use_random, mazen )

        if success:
            with open("done.txt", "a", encoding="utf-8") as f:
                f.write(account_line + "\n")
            print(colored(f"Processed account {email} and moved to done.txt", "green"))

        # Update Email&Password&CVV.txt file
        with open("Email&Password&CVV.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open("Email&Password&CVV.txt", "w", encoding="utf-8") as f:
            f.writelines([line for line in lines if line.strip() != account_line])

        time.sleep(2)
    print(colored(f"Finished controlling emulator: {emu_name}", "green"))


crash_count = 0

def safe_process_emulator(*args):
    global crash_count
    worker_name = args[1]
    while True:
        try:
            process_emulator(*args)
            break
        except Exception as e:
            crash_count += 1
            print(colored(
                f"[THREAD CRASH #{crash_count}] {worker_name} → restarting | {e}",
                "red"
            ))
            time.sleep(3)




def press_key(emulator, key_code):
    adb_command = [ADB_PATH, "-s", emulator, "shell", "input", "keyevent", str(key_code)]
    subprocess.run(adb_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def connect_uiautomator2(emulator):
    try:
        d = u2.connect(emulator)
        d.implicitly_wait(3.0)
        return d
    except Exception as e:
        print(colored(f"UIAutomator2 connection failed: {e}", 'red'))
        return None


def optimized_tap(d, resource_id=None, text=None, coordinates=None):
    if coordinates:
        d.click(coordinates[0], coordinates[1])
        return True
    if resource_id:
        elem = d(resourceId=resource_id)
    elif text:
        elem = d(text=text)
    else:
        return False
    if elem.exists:
        elem.click()
        return True
    return False


def optimized_tap2(d, worker_id, resource_id=None, text=None, coordinates=None):
    try:
        if coordinates:
            d.click(*coordinates)
            return True
        elem = None
        if resource_id and d(resourceId=resource_id).exists():
            elem = d(resourceId=resource_id)
        elif text and d(textContains=text).exists():
            elem = d(textContains=text)
        elif text and d(descriptionContains=text).exists():
            elem = d(descriptionContains=text)
        time.sleep(1)
        if elem and elem.exists():
            elem.click()
            return True
    except Exception as e:
        print(colored(f"{worker_id} -Error in optimized_tap: {e}", 'red'))
    print(colored(f"{worker_id} -Element '{text or resource_id}' not found.", 'red'))
    return False


def fast_tap_element(d,worker_id, text=None, resource_id=None, coordinates=None, retries=10, delay=0.3 ):

    for attempt in range(retries):
        if optimized_tap(d, resource_id, text, coordinates):
            return True
        time.sleep(delay)
    print(colored(f"{worker_id} -Element not found after {retries} attempts", 'red'))
    return False


def get_all_email_password_cvv(filename="Email&Password&CVV.txt"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split("\t")
                    if len(parts) == 3:
                        accounts.append(tuple(parts))
                    else:
                        print(colored(f"Invalid format for line: {line}, moving to fail.txt", 'red'))
                        with open("fail.txt", "a", encoding="utf-8") as f:
                            f.write(line + "\n")
        return accounts
    except Exception as e:
        print(colored(f"Error reading {filename}: {e}", 'red'))
        return []



def get_Pass():
    try:
        config = configparser.ConfigParser()
        loaded = config.read("config.ini", encoding="utf-8")

        if not loaded:
            print(colored("Error: config.ini not found or unreadable.", "red"))
            return None

        if not config.has_section("CHILD_ACCOUNT"):
            print(colored("Error: [CHILD_ACCOUNT] section missing in config.ini.", "red"))
            return None

        if not config.has_option("CHILD_ACCOUNT", "password"):
            print(colored("Error: password key missing in [CHILD_ACCOUNT].", "red"))
            return None

        password = config.get("CHILD_ACCOUNT", "password").strip()

        if not password:
            print(colored("Error: CHILD_ACCOUNT.password is empty.", "red"))
            return None

        return password

    except Exception as e:
        print(colored(f"Error reading password from config.ini: {e}", "red"))
        return None





def read_answers():
    try:
        config = configparser.ConfigParser()
        loaded = config.read("config.ini", encoding="utf-8")

        if not loaded:
            print(colored("Error: config.ini not found or unreadable.", "red"))
            return {}

        if not config.has_section("CHILD_ACCOUNT"):
            print(colored("Error: [CHILD_ACCOUNT] section missing in config.ini.", "red"))
            return {}

        answers = {
            "q1": config.get("CHILD_ACCOUNT", "answer1", fallback="").strip(),
            "q2": config.get("CHILD_ACCOUNT", "answer2", fallback="").strip(),
            "q3": config.get("CHILD_ACCOUNT", "answer3", fallback="").strip(),
        }

        # Validate answers like the old version
        for k, v in answers.items():
            if not v:
                print(colored(f"Warning: {k} is empty in config.ini.", "yellow"))

        return answers

    except Exception as e:
        print(colored(f"Error reading answers from config.ini: {e}", "red"))
        return {}




answers_dict = read_answers()


# --- Main Automation Workflow ---
'''def wait_for_element(d, text=None, resource_id=None, timeout=60):
    if text:
        return d(text=text).wait(timeout=timeout)
    if resource_id:
        return d(resourceId=resource_id).wait(timeout=timeout)
    return False'''


def update_account_date(email, new_date):
    try:
        with open("accounts.txt", "r") as f:
            lines = f.readlines()

        updated = False
        new_lines = []

        for line in lines:
            if line.startswith(email + ","):
                parts = line.strip().split(",")
                parts[2] = new_date  # ⬅️ التاريخ
                line = ",".join(parts) + "\n"
                updated = True
            new_lines.append(line)

        if updated:
            with open("accounts.txt", "w") as f:
                f.writelines(new_lines)
            print(colored(f"[✓] Updated date for {email} → {new_date}", "green"))

    except Exception as e:
        print(colored(f"[!] Failed to update account {email}: {e}", "red"))


def wait_for_element(d, text=None, resource_id=None, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if text and d(text=text).exists:
                return True
            if resource_id and d(resourceId=resource_id).exists:
                return True
        except:
            pass
        time.sleep(0.4)
    return False



# Define the characters to exclude
EXCLUDED_CHARS = '&*$#@!`~^%?<>.,_-+=)(";:\''

EXCLUDED_CHARS2 = '+=\''  # for password


def is_valid_password(word):
    return len(word) >= 3 and not any(char in EXCLUDED_CHARS2 for char in word)


# Helper function to validate words

def build_single_password(size=50):
    passwords = set()
    while len(passwords) < size:
        password = fake.password().split()[0]
        if is_valid_password(password):
            passwords.add(password)
    return list(passwords)[:size]


SINGLE_WORD_password = build_single_password(50)


def is_valid_word(word):
    return len(word) >= 3 and not any(char in EXCLUDED_CHARS for char in word)


# Precompute single-word pools at script start
def build_single_word_pools(size=50):
    jobs = set()
    cities = set()
    while len(jobs) < size or len(cities) < size:
        job = fake.job().split()[0]
        city = fake.city().split()[0]
        if is_valid_word(job):
            jobs.add(job)
        if is_valid_word(city):
            cities.add(city)
    return list(jobs)[:size], list(cities)[:size]


SINGLE_WORD_JOBS, SINGLE_WORD_CITIES = build_single_word_pools(50)


def append_to_fail_file(account_data):
    email, pwd, cvv = account_data
    with open("fail.txt", "a", encoding="utf-8") as file:
        file.write(f"{email}\t{pwd}\t{cvv}\n")


def append_to_locked_file(account_data):
    email, pwd, cvv = account_data
    with open("locked.txt", "a", encoding="utf-8") as file:
        file.write(f"{email}\t{pwd}\t{cvv}\n")







def enter_cvv(d, cvv, worker_id):
    if d(resourceId="com.apple.android.music:id/cvv_edittext").wait(timeout=5.0):
        d(resourceId="com.apple.android.music:id/cvv_edittext").click()
        time.sleep(0.3)
        d.clear_text()
        time.sleep(0.3)
        d.send_keys(cvv)
        print(colored(f"{worker_id} -Entered CVV: {cvv}", "blue"))
        time.sleep(0.3)
    else:
        print(colored(f"{worker_id} -Error: CVV field not found", "red"))
    if d(text="Next").wait(timeout=5.0):
        fast_tap_element(d,worker_id, text="Next")
        print(colored(f"{worker_id} -Tapped 'Next'", "green"))
        time.sleep(0.5)
    else:
        print(colored(f"{worker_id} -Error: 'Next' not found", "red"))




def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")

    # ---- PROXY ----
    use_proxy = config.getboolean("Settings", "use_proxy", fallback=False)
    proxy_string = config.get("Settings", "proxy", fallback="")

    # ---- FIXED CHILD DATA ----
    child_password = config.get("CHILD_ACCOUNT", "password", fallback="")
    ans1 = config.get("CHILD_ACCOUNT", "answer1", fallback="")
    ans2 = config.get("CHILD_ACCOUNT", "answer2", fallback="")
    ans3 = config.get("CHILD_ACCOUNT", "answer3", fallback="")

    return child_password, ans1, ans2, ans3, use_proxy, proxy_string







def parse_proxy(proxy_string):
    """Parse proxy string and return formatted proxy dict."""
    if not proxy_string or proxy_string.strip() == '':
        return None

    proxy_string = proxy_string.strip()

    if '://' in proxy_string:
        protocol = proxy_string.split('://')[0].lower()
        rest = proxy_string.split('://')[1]

        if '@' in rest:
            auth_part = rest.split('@')[0]
            server_part = rest.split('@')[1]
            user, password = auth_part.split(':')

            if protocol in ['socks5', 'socks5h']:
                return {
                    'http': f'socks5://{user}:{password}@{server_part}',
                    'https': f'socks5://{user}:{password}@{server_part}'
                }
            elif protocol == 'socks4':
                return {
                    'http': f'socks4://{user}:{password}@{server_part}',
                    'https': f'socks4://{user}:{password}@{server_part}'
                }
            else:
                return {
                    'http': f'http://{user}:{password}@{server_part}',
                    'https': f'http://{user}:{password}@{server_part}'
                }
        else:
            if protocol in ['socks5', 'socks5h']:
                return {
                    'http': f'socks5://{rest}',
                    'https': f'socks5://{rest}'
                }
            elif protocol == 'socks4':
                return {
                    'http': f'socks4://{rest}',
                    'https': f'socks4://{rest}'
                }
            else:
                return {
                    'http': f'http://{rest}',
                    'https': f'http://{rest}'
                }

    parts = proxy_string.split(':')

    if len(parts) == 2:
        return {
            'http': f'http://{proxy_string}',
            'https': f'http://{proxy_string}'
        }
    elif len(parts) == 4:
        ip, port, user, password = parts
        return {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'http://{user}:{password}@{ip}:{port}'
        }
    elif '@' in proxy_string:
        auth_part = proxy_string.split('@')[0]
        server_part = proxy_string.split('@')[1]
        user, password = auth_part.split(':')
        return {
            'http': f'http://{user}:{password}@{server_part}',
            'https': f'http://{user}:{password}@{server_part}'
        }
    else:
        return {
            'http': f'http://{proxy_string}',
            'https': f'http://{proxy_string}'
        }



def aging_worker():
    while True:
        data = aging_queue.get()
        if data is None:
            break

        try:
            worker_id, proxy_dict, child_email, child_password, ans1, ans2, ans3 = data

            success = age_child_with_retry(
                worker_id,
                proxy_dict,
                child_email,
                child_password,
                ans1,
                ans2,
                ans3
            )

            if success:
                # ✅ aging نجح فعلاً → عدّل التاريخ
                update_account_date(child_email, "01/01/1990")
            else:
                with open("age_fail.txt", "a") as f:
                    f.write(child_email + "\n")


        except Exception as e:
            print(f"[AGING][{worker_id}] CRASH: {e}")

        finally:
            aging_queue.task_done()

class iCloudCrypto:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.srp = Srp(Mode.GSA, Hash.SHA256, 2048)
        self.srp_client: Client = self.srp.new_client(I=bytes(username, encoding='utf-8'), p=bytes("", encoding='utf-8'))

    def get_client_ephemeral(self):
        return base64.b64encode(bytes_from_bigint(self.srp_client.A)).decode('utf-8')

    def derive_password(self, protocol, salt, iterations):
        pass_hash = hash_func(self.srp.h, self.password.encode())

        if protocol == 's2k_fo':
            pass_hash = to_hex(pass_hash)

        salt_bytes = base64.b64decode(salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=iterations,
            backend=default_backend()
        )
        derived_key = kdf.derive(pass_hash)
        return derived_key

    def get_proof_values(self, derived_password, server_public_value, salt):
        salt_bytes = base64.b64decode(salt)
        server_public_value_bytes = base64.b64decode(server_public_value)

        self.srp_client.p = derived_password
        M1 = bytes.fromhex(self.srp_client.generate(salt_bytes, server_public_value_bytes))
        M2 = self.srp_client.generate_m2()

        m1_base64 = base64.b64encode(M1).decode('utf-8')
        m2_base64 = base64.b64encode(M2).decode('utf-8')

        return m1_base64, m2_base64


def age_child( worker_id, proxy_dict,child_email,child_password,ans1, ans2, ans3):
    try:
        child_email_norm = child_email.strip().lower()
        print(f"{Fore.CYAN}[→] {worker_id} - Changing birthday for: {child_email}{Style.RESET_ALL}")
        authenticator = iCloudCrypto(username=child_email_norm, password=child_password)
        s = requests.Session()

        # Setup proxy if provided
        if proxy_dict:
            s.proxies.update(proxy_dict)
            print(f"{Fore.CYAN}[→] {worker_id} - Using proxy:")
        headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'Origin': 'https://idmsa.apple.com',
                'Referer': 'https://idmsa.apple.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
                'X-Apple-Auth-Attributes': 'Pj3te/Xq79OI7j0k7dMRjdjlseyBdgNjmLnR2LRcOmSuZl0agcCuddMrtdbV/EvoT3E5ztGXIKeiIqtvuPI4Sit8edBolHL6qHyr7i+N0/ty0P8gh08bzvtqnjTl7/FPMEeDuK3oTOxJBN6YAXcarM1MfwEvJdeYiyp4uFS646xP4QKaX8ZAMErIM6Dd9BkZ3tArO33g54ky2Bv+9L3JaN4IMQdxvxLriqpn2TZz0DpVg59HerWIAQi2dG+8HIwQytKRLQufDGrhcL+0+xj6ocUAFdXCvQmAjg==',
                'X-Apple-Domain-Id': '11',
                'X-Apple-Frame-Id': 'auth-66cbb9e9-spb3-vppo-yn2e-6vpkemfx',
                'X-Apple-I-FD-Client-Info': '{"U":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36","L":"en-US","Z":"GMT+02:00","V":"1.1","F":"sla44j1e3NlY5BNlY5BSs5uQ084akLJ6N38.7Fx_MKR0odm_dhrxbuJjkWxv55BPfs1eNk4ug4DKpDK1c5vmjoaUW2vqBBNlY5BPY25BNnOVgw24uy.2Wf"}',
                'X-Apple-ID-Session-Id': '920F016D116BE3AE42169EAC8539257D0B496E18A606863FD3E0A6DCA213C38FDBA68D16A830BE4BAFF09E1E07DD6040829B227B9446A615B0E80DE1D3EB8C2874EAA5E9DFAE98033910CB972B385F3991679060ADAB718B82D799C1D4CC6D176CFA196C2BA315D2DE615C9998C861E9B86004FB13414A8B',
                'X-Apple-OAuth-Client-Id': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
                'X-Apple-OAuth-Client-Type': 'firstPartyAuth',
                'X-Apple-OAuth-Redirect-URI': 'https://account.apple.com',
                'X-Apple-OAuth-Response-Mode': 'web_message',
                'X-Apple-OAuth-Response-Type': 'code',
                'X-Apple-OAuth-State': 'auth-66cbb9e9-spb3-vppo-yn2e-6vpkemfx',
                'X-Apple-Privacy-Consent': 'true',
                'X-Apple-Privacy-Consent-Accepted': 'true',
                'X-Apple-Widget-Key': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
                'X-Requested-With': 'XMLHttpRequest',
            }
        json_data = {
                'a': authenticator.get_client_ephemeral(),
                'accountName': child_email,
                'protocols': ['s2k', 's2k_fo'],
            }
        
        response = s.post('https://idmsa.apple.com/appleauth/auth/signin/init', headers=headers, json=json_data)
        init_data = response.json()
        derived_password = authenticator.derive_password(
                init_data["protocol"],
                init_data["salt"],
                init_data["iteration"]
            )
        m1_proof, m2_proof = authenticator.get_proof_values(
                derived_password,
                init_data["b"],
                init_data["salt"]
            )
        
        
        
        
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://idmsa.apple.com',
            'Referer': 'https://idmsa.apple.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'X-APPLE-HC': '1:10:20260112121003:66b28f8b48a455fa8d90de906bf54310::181',
            'X-Apple-Auth-Attributes': 'BH75VSlOAN9jLxPKVmxJyDdV6wqPZcxnKYWHMTB2iqoe+SVBNQczVSjZ1H2+jmQ6hVpGFWiiL3xmpGwQW83eJjt06KJgp5GystoQnHxJmQG002LxdgBkWOFAelMLey2okeL+X7oeoXq/8hXbeeIvWREG27DxBPXyhjN3EFET3xRCDyl1vIVKMSBBmBdsMrXGdyiKtW5KNxTmPhv0HaPWgqCeQwSS2Zf0EgGw8NoNmM8m142wnwCKnz+xmfAcWLGKEZZE12Wh/HMe7RdkKzVDNfIAFqHIVG9q4g==',
            'X-Apple-Domain-Id': '11',
            'X-Apple-Frame-Id': 'auth-yp4r1txm-002y-st2l-0bdx-m3mu2ehh',
            'X-Apple-I-FD-Client-Info': '{"U":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36","L":"en-US","Z":"GMT+02:00","V":"1.1","F":"sla44j1e3NlY5BNlY5BSs5uQ084akLJ6KGTrKMGpKSKk6Hb9LarUqUdHz16rgNNl_jV9dY.MekJseY_Fe0ixIwgAxHUTlWY5BNlYJNNlY5QB4bVNjMk.8Ty"}',
            'X-Apple-ID-Session-Id': 'FA7C676E3B6D330F7D5B0218402825111A4A577CF150E129E5620233EEE2AFC14E229A50696833A89BBD4A4FCE9C9269843BA3AAB8CEA109CD117A2FD6CC3A03B29042AB0B9EFB0FB84E5908E1F0FBAC86058F31491051454493D1067FEE43668E302FC205ED8F5F0E65BD87CFA89DA9A4B153E479919FF0',
            'X-Apple-OAuth-Client-Id': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
            'X-Apple-OAuth-Client-Type': 'firstPartyAuth',
            'X-Apple-OAuth-Redirect-URI': 'https://account.apple.com',
            'X-Apple-OAuth-Response-Mode': 'web_message',
            'X-Apple-OAuth-Response-Type': 'code',
            'X-Apple-OAuth-State': 'auth-yp4r1txm-002y-st2l-0bdx-m3mu2ehh',
            'X-Apple-Privacy-Consent': 'true',
            'X-Apple-Privacy-Consent-Accepted': 'true',
            'X-Apple-Widget-Key': 'af1139274f266b22b68c2a3e7ad932cb3c0bbe854e13a79af78dcc73136882c3',
            'X-Requested-With': 'XMLHttpRequest',
        }

        params = {'isRememberMeEnabled': 'true'}



        json_data = {
                'accountName': child_email_norm,
                'password': child_password,
                'rememberMe': True,
                'm1': m1_proof,
                'c': init_data["c"],
                'm2': m2_proof,
            }

        response = s.post(
            'https://idmsa.apple.com/appleauth/auth/signin/complete',
            params=params,
            headers=headers,
            json=json_data,
        )

        scnt = response.headers.get('scnt')
        if not scnt:
            print(f"{Fore.RED}[-] {worker_id} - Failed to get scnt for {child_email}{Style.RESET_ALL}")
            return False

        headers.update({'scnt': scnt})

        response = s.get('https://idmsa.apple.com/appleauth/auth', headers=headers)
        print(response.status_code)
        if response.status_code == 401:
            print(f"{Fore.RED}[-] {worker_id} - 401 Unauthorized for {child_email}{Style.RESET_ALL}")
            return "RELOGIN"

        try:
            boot_data = response.json()

        except Exception as e:
            print(f"{Fore.RED}[-] {worker_id} - boot_args not found for {child_email}{Style.RESET_ALL}")
            return "RELOGIN"


        questions = boot_data["securityQuestions"]["questions"]

        # Match answers to questions
        if questions[0]['id'] in range(130, 136):
            v1 = ans1
        elif questions[0]['id'] in range(136, 142):
            v1 = ans2
        elif questions[0]['id'] in range(142, 148):
            v1 = ans3
        else:
            v1 = ans1

        if questions[1]['id'] in range(130, 136):
            v2 = ans1
        elif questions[1]['id'] in range(136, 142):
            v2 = ans2
        elif questions[1]['id'] in range(142, 148):
            v2 = ans3
        else:
            v2 = ans2



        json_data = {
            'questions': [
                {
                    'question': questions[0]['question'],
                    'answer': v1,
                    'id': questions[0]['id'],
                    'number': questions[0]['number']
                },
                {
                    'question': questions[1]['question'],
                    'answer': v2,
                    'id': questions[1]['id'],
                    'number': questions[1]['number']
                }
            ]
        }

        response = s.post(
            'https://idmsa.apple.com/appleauth/auth/verify/questions',
            headers=headers,
            json=json_data,
        )

        token = response.headers.get("x-apple-repair-session-token")
        if not token:
            print(f"{Fore.RED}[-] {worker_id} - Failed to get repair token for {child_email}{Style.RESET_ALL}")
            return False

        headers.update({'x-apple-repair-session-token': token})
        response = s.post('https://idmsa.apple.com/appleauth/auth/repair/complete', headers=headers)

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://account.apple.com',
            'Referer': 'https://account.apple.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'X-Apple-I-Request-Context': 'ca',
            'X-Apple-I-TimeZone': 'Africa/Cairo',
        }

        response = s.get('https://appleid.apple.com/account/manage', headers=headers)
        scnt1 = response.headers.get('scnt')

        if not scnt1:
            print(f"{Fore.RED}[-] {worker_id} - Failed to get scnt1 for {child_email}{Style.RESET_ALL}")
            return False

        headers.update({'scnt': scnt1})
        headers.update({'X-Apple-Api-Key': 'cbf64fd6843ee630b463f358ea0b707b'})

        json_data = {
            'dayOfMonth': '01',
            'monthOfYear': '01',
            'year': '1990',
        }

        response = s.post(
            'https://appleid.apple.com/account/manage/security/birthday/verify',
            headers=headers,
            json=json_data,
        )

        response = s.put(
            'https://appleid.apple.com/account/manage/security/birthday',
            headers=headers,
            json=json_data,
        )

        if response.status_code == 200:
            print(f"{Fore.GREEN}[✓] {worker_id} - Birthday changed for: {child_email}{Style.RESET_ALL}")
            return True
        else:
            print(
                f"{Fore.RED}[-] {worker_id} - Failed to change birthday for {child_email} (Status: {response.status_code}){Style.RESET_ALL}")
            return False

    except Exception as e:
        print(f"{Fore.RED}[-] {worker_id} - Error changing birthday for {child_email}: {e}{Style.RESET_ALL}")
        return False





def age_child_with_retry(worker_id, proxy_dict, child_email, child_password, ans1, ans2, ans3, max_retries=10, delay=3):
    for attempt in range(1, max_retries + 1):
        print(colored(
            f"[→] Aging attempt {attempt}/{max_retries} for {child_email}",
            "cyan"
        ))

        result = age_child(
            worker_id,
            proxy_dict,
            child_email,
            child_password,
            ans1,
            ans2,
            ans3
        )

        # ✅ نجاح
        if result is True:
            print(colored(
                f"[✓] Aging success for {child_email}",
                "green"
            ))
            return True

        # 🔄 Session اتحرقت (401 / boot_args)
        if result == "RELOGIN":
            print(colored(
                f"[!] {child_email} session burned → retrying fresh session",
                "yellow"
            ))
            time.sleep(delay + 2)
            continue  # ⬅️ يعيد من الأول Session جديدة

        # ❌ فشل عادي
        print(colored(
            f"[!] Aging failed (attempt {attempt}), retrying...",
            "yellow"
        ))
        time.sleep(delay)

    print(colored(
        f"[✗] Aging permanently failed for {child_email}",
        "red"
    ))
    return False





def remove_children(d, worker_id):
    try:
        print(f"{Fore.YELLOW}[*] {worker_id} - Removing adults directly{Style.RESET_ALL}")

        removed_count = 0
        max_cycles = 30  # حماية من infinite loop

        for _ in range(max_cycles):
            time.sleep(2)

            # هل فيه Adult ظاهر؟
            adults = d(text="Adult")
            if not adults.exists:
                print(f"{Fore.GREEN}[✓] {worker_id} - No more adults found ({removed_count} removed){Style.RESET_ALL}")
                return True

            clicked = False

            # حاول تضغط على أول Adult
            try:
                adults[0].click()
                clicked = True
                time.sleep(1.5)
            except:
                pass

            if not clicked:
                print(f"{Fore.YELLOW}[!] {worker_id} - Couldn't click Adult, retrying{Style.RESET_ALL}")
                continue

            # استنى زر Remove
            for _ in range(20):
                if d(text="Remove From Family…").exists:
                    try:
                        d(text="Remove From Family…").click()
                        time.sleep(0.7)

                        if d(text="REMOVE").exists:
                            d(text="REMOVE").click()
                            wait_for_element(d, text="Adult") or wait_for_element(d, text="Organizer")
                            time.sleep(2)
                            removed_count += 1
                            print(f"{Fore.GREEN}[✓] {worker_id} - Adult removed ({removed_count}){Style.RESET_ALL}")
                            break
                        else:
                            d.press("back")
                            break
                    except:
                        d.press("back")
                        break
                time.sleep(0.2)

            # رجوع للقائمة
            '''try:
                d.press("back")
                time.sleep(1)
            except:
                pass'''

        print(f"{Fore.YELLOW}[!] {worker_id} - Stopped after max cycles ({removed_count} removed){Style.RESET_ALL}")
        return True

    except Exception as e:
        print(f"{Fore.RED}[-] {worker_id} - Error removing adults: {e}{Style.RESET_ALL}")
        return False



'''def reset_family_sharing(d, worker_id ):
    """
    Reset family sharing (Optimized based on Test):
    Organizer -> Stop Family Sharing -> Confirm -> Wait 3s -> Continue -> Wait 4s.
    """

    try:
        print(f"{Fore.CYAN}[→] {worker_id} - Invoking Family Sharing Reset...{Style.RESET_ALL}")

        # 1. CLICK ORGANIZER
        # بندوس لو احنا برا، لو احنا جوه أصلا مش هيلاقيها وهيكمل
        if d(text="Organizer").exists:
            d(text="Organizer").click()
            time.sleep(2.0)
        elif d(textContains="(Me)").exists:
            d(textContains="(Me)").click()
            time.sleep(2.0)

        # 2. CLICK STOP FAMILY SHARING (RED LINK)
        if d(textContains="Stop Family Sharing").wait(timeout=5):
            d(textContains="Stop Family Sharing").click()
        else:
            print(f"{Fore.RED}[!] {worker_id} - 'Stop Family Sharing' button not found.{Style.RESET_ALL}")
            return False

        # 3. CONFIRMATION (STOP SHARING)
        # بنستنى ثانية عشان الأنيميشن
        time.sleep(1.0)

        if d(text="Stop Sharing").wait(timeout=5):
            d(text="Stop Sharing").click()
        elif d(text="STOP SHARING").exists:
            d(text="STOP SHARING").click()
        elif d(resourceId="android:id/button1").exists:
            d(resourceId="android:id/button1").click()
        else:
            print(
                f"{Fore.YELLOW}[!] {worker_id} - Confirmation button didn't appear, checking next step...{Style.RESET_ALL}")

        # 4. WAIT 3 SECONDS (As requested)
        print(f"{Fore.MAGENTA}[Wait] {worker_id} - Waiting 3s before Continue...{Style.RESET_ALL}")
        time.sleep(1.5)

        # 5. CLICK CONTINUE
        if d(text="Continue").wait(timeout=10):
            d(text="Continue").click()
            print(f"{Fore.GREEN}[✓] {worker_id} - Reset Confirmed (Continue Clicked).{Style.RESET_ALL}")

        else:
            print(f"{Fore.RED}[!] {worker_id} - 'Continue' button did not appear.{Style.RESET_ALL}")
            # هنكمل عادي لأنه ممكن يكون خلص خلاص

        # 6. WAIT 4 SECONDS (Finalizing)
        print(f"{Fore.MAGENTA}[Wait] {worker_id} - Waiting 4s to return to Family screen...{Style.RESET_ALL}")
        time.sleep(4.0)


        family_reached = False
        account_limit_reached = False
        for t in range(3):
            if family_reached: break

            # Send ADB Command (Inject)
            # os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')

            # Wait and Check UI
            for check in range(4):

                if d(textContains="cannot Start Family Sharing").exists:
                    time.sleep(1)
                    wait_for_element(d, text="OK")
                    time.sleep(1.5)
                    fast_tap_element(d, worker_id, text="OK")
                    time.sleep(1)
                    error_type = "Error 1 maximum"
                    account_limit_reached = True
                    print(colored(f"{email}\ncannot Start Family Sharing.", "red"))
                    family_reached = True
                    break

                time.sleep(1)

                # A. Success Check
                if d(text="Organizer").exists or d(textContains="Add Family Member").exists:
                    print(colored(f"{worker_id} -Family Screen Reached! {emu_name}", "green"))
                    family_reached = True
                    break

                # B. Handle "Continue"
                if d(text="Continue").exists:
                    print(colored(f"{worker_id} -Clicking Continue... {emu_name}", "green"))
                    d(text="Continue").click()
                    time.sleep(2)
                    continue

                # C. Handle Password Popup
                if d(text="Sign In").exists or d(textContains="password").exists:
                    if d(className="android.widget.EditText").exists:
                        print(colored(f"{worker_id} -Handling Re-Auth Popup... {emu_name}", "yellow"))
                        try:
                            d(className="android.widget.EditText").set_text(pwd_from_file)
                            time.sleep(0.5)
                            if d(text="SIGN IN").exists:
                                d(text="SIGN IN").click()
                            elif d(text="Sign In").exists:
                                d(text="Sign In").click()
                            print(colored(f"{worker_id} -Waiting 5s after popup... {emu_name}", "yellow"))
                            time.sleep(5)
                        except:
                            pass
                        continue

                time.sleep(1.5)

            if family_reached: break

        if not family_reached:
            print(colored(f"{worker_id} -Force checking 'Continue' one last time...{emu_name}", "yellow"))
            if d(text="Continue").exists: d(text="Continue").click()


        max_check = 30
        check = 0
        while   check < max_check:
            check += 1

            if d(textContains="cannot Start Family Sharing").exists:
                print(colored(f"{worker_id} -  cannot Start Family Sharing.", "red"))
                time.sleep(1)
                wait_for_element(d, text="OK")
                time.sleep(1.5)
                fast_tap_element(d,worker_id, text="OK")
                time.sleep(1)
                account_limit_reached = True
                return i, True
                #break


        return True

    except Exception as e:
        print(f"{Fore.RED}[-] {worker_id} - Error during family sharing reset: {e}{Style.RESET_ALL}")
        try:
            d.press("back"); time.sleep(1)
        except:
            pass
        return False'''


def tap(d, worker_id, *, text=None, resource_id=None, retries=6, delay=0.5, optional=True):
    for _ in range(retries):
        try:
            if text:
                el = d(text=text)
            elif resource_id:
                el = d(resourceId=resource_id)
            else:
                return False

            if el.exists:
                el.click()
                return True

        except Exception:
            pass

        time.sleep(delay)

    if not optional:
        print(colored(f"{worker_id} - REQUIRED element not found: {text or resource_id}", "red"))
    else:
        print(colored(f"{worker_id} - Optional element skipped: {text or resource_id}", "yellow"))

    return False


def Try_Another_Apple_ID(d, account_name, emulator, worker_id):
    max_attempts = 10
    attempt_count = 0
    if d(text="@icloud.com").wait(timeout=20):
        print(colored(f"{worker_id} -account", "yellow"))
    else:
        print(colored(f"{worker_id} -Error: @icloud.com not found, moving to next step...", "red"))
        return account_name

    while attempt_count < max_attempts:
        if d(text="Try Another Apple ID").wait(timeout=4):
            attempt_count += 1
            print(colored(f"{worker_id} -Attempt {attempt_count}/{max_attempts}: Found 'Try Another Apple ID', attempting to tap OK...","yellow"))
            time.sleep(1.0)
            if d(text="OK").wait(timeout=20):
                time.sleep(1.0)
                fast_tap_element(d,worker_id, text="OK")
                print(colored(f"{worker_id} -Tapped 'OK'", "green"))
                time.sleep(1.0)
            else:
                print(colored(f"{worker_id} -Error: 'OK' not found after waiting, moving to next step...", "red"))
                break

            if d(resourceId="com.apple.android.music:id/child_account_email").wait(timeout=20):
                d(resourceId="com.apple.android.music:id/child_account_email").click()
                time.sleep(0.5)
                d(resourceId="com.apple.android.music:id/child_account_email").clear_text()
                time.sleep(0.5)
                if d(resourceId="com.apple.android.music:id/child_account_email").get_text() == "":
                    print(colored(f"{worker_id} -Field cleared successfully", "green"))
                else:
                    print(colored(f"{worker_id} -Warning: Failed to clear text, forcing clear with backspace", "yellow"))
                    for _ in range(20):
                        press_key(emulator, "KEYCODE_DEL")
                        time.sleep(0.1)

                new_account_name = f"{fake.first_name()}s{fake.last_name()}Z{generate_n_digit_number(3)}"
                print(colored(f"{worker_id} -Generated new name: {new_account_name}", "blue"))
                time.sleep(0.5)
                d.send_keys(new_account_name)
                time.sleep(0.5)

                if d(text="Next").wait(timeout=20.0):
                    time.sleep(0.5)
                    fast_tap_element(d,worker_id, text="Next")
                    time.sleep(1.0)
                    if not d(textContains="Try Another").wait(timeout=2.0):
                        print(colored(f"{worker_id} -New Apple ID accepted", "green"))
                        return new_account_name
                    else:
                        print(colored(f"{worker_id} -Attempt {attempt_count}/{max_attempts}: New Apple ID not accepted, trying again...","yellow"))
                else:
                    print(colored(f"{worker_id} -Error: 'Next' not found, moving to next step...", "red"))
                    break
            else:
                print(colored(f"{worker_id} -Error: Email field not found, moving to next step...", "red"))
                break
        else:
            print(colored(f"{worker_id} -No 'Try Another Apple ID' found, proceeding to next step...", "green"))
            break

    if attempt_count >= max_attempts:
        print(colored(f"{worker_id} -Reached maximum attempts ({max_attempts}) to find a new Apple ID, moving to next step with original account: {account_name}","red"))
    return account_name



def Try_Another_Apple_ID_2(d, account_name,  emulator,worker_id):
    if d(text="@icloud.com").wait(timeout=20):
        print(colored(f"{worker_id} -account", "yellow"))
    else:
        print(colored(f"{worker_id} -Error: @icloud.com not found, moving to next step...", "red"))
        return account_name

    if d(resourceId="com.apple.android.music:id/child_account_email").wait(timeout=20):
        d(resourceId="com.apple.android.music:id/child_account_email").click()
        time.sleep(0.5)
        d(resourceId="com.apple.android.music:id/child_account_email").clear_text()
        time.sleep(0.5)
        if d(resourceId="com.apple.android.music:id/child_account_email").get_text() == "":
            print(colored(f"{worker_id} -Field cleared successfully", "green"))
        else:
            print(colored(f"{worker_id} -Warning: Failed to clear text, forcing clear with backspace", "yellow"))
            for _ in range(20):
                press_key(emulator, "KEYCODE_DEL")
                time.sleep(0.1)

        new_account_name = f"{fake.first_name()}{fake.last_name()}Z{generate_n_digit_number(3)}"
        print(colored(f"{worker_id} -Generated new name: {new_account_name}", "blue"))
        time.sleep(0.5)
        d.send_keys(new_account_name)
        time.sleep(0.5)

        if d(text="Next").wait(timeout=20.0):
            time.sleep(0.5)
            fast_tap_element(d,worker_id, text="Next")
            time.sleep(1.0)
    return account_name

mazen = 14

def automate_account_creation(emulator, emu_name, account_data, use_random, mazen ):
#def automate_account_creation(emulator, account_data, use_random, mazen):
    email, pwd_from_file, cvv = account_data
    d = connect_uiautomator2(emulator)




    #worker_id = emulator
    worker_id = emu_name
    account_limit_reached = False

    if not d:
        append_to_fail_file(account_data)
        print(colored(f"{worker_id} -Failed to connect to emulator for {email}", "red"))
        return 0, False


    #d.set_fastinput_ime(True)# test al cope


    def reset_family_sharing(d, worker_id):
        """
        Reset family sharing (Optimized based on Test):
        Organizer -> Stop Family Sharing -> Confirm -> Wait 3s -> Continue -> Wait 4s.
        """

        try:
            print(f"{Fore.CYAN}[→] {worker_id} - Invoking Family Sharing Reset...{Style.RESET_ALL}")

            # 1. CLICK ORGANIZER
            # بندوس لو احنا برا، لو احنا جوه أصلا مش هيلاقيها وهيكمل
            if d(text="Organizer").exists:
                d(text="Organizer").click()
                time.sleep(2.0)
            elif d(textContains="(Me)").exists:
                d(textContains="(Me)").click()
                time.sleep(2.0)

            # 2. CLICK STOP FAMILY SHARING (RED LINK)
            if d(textContains="Stop Family Sharing").wait(timeout=5):
                d(textContains="Stop Family Sharing").click()
            else:
                print(f"{Fore.RED}[!] {worker_id} - 'Stop Family Sharing' button not found.{Style.RESET_ALL}")
                return False

            # 3. CONFIRMATION (STOP SHARING)
            # بنستنى ثانية عشان الأنيميشن
            time.sleep(1.0)

            if d(text="Stop Sharing").wait(timeout=5):
                d(text="Stop Sharing").click()
            elif d(text="STOP SHARING").exists:
                d(text="STOP SHARING").click()
            elif d(resourceId="android:id/button1").exists:
                d(resourceId="android:id/button1").click()
            else:
                print(
                    f"{Fore.YELLOW}[!] {worker_id} - Confirmation button didn't appear, checking next step...{Style.RESET_ALL}")

            # 4. WAIT 3 SECONDS (As requested)
            print(f"{Fore.MAGENTA}[Wait] {worker_id} - Waiting 3s before Continue...{Style.RESET_ALL}")
            time.sleep(1.5)

            # 5. CLICK CONTINUE
            '''if d(text="Continue").wait(timeout=10):
                d(text="Continue").click()
                print(f"{Fore.GREEN}[✓] {worker_id} - Reset Confirmed (Continue Clicked).{Style.RESET_ALL}")

            else:
                print(f"{Fore.RED}[!] {worker_id} - 'Continue' button did not appear.{Style.RESET_ALL}")
                # هنكمل عادي لأنه ممكن يكون خلص خلاص'''
            safe_click(d, worker_id, text="Continue")
            print(f"{Fore.GREEN}[✓] {worker_id} - Reset Confirmed (Continue Clicked).{Style.RESET_ALL}")

            # 6. WAIT 4 SECONDS (Finalizing)
            print(f"{Fore.MAGENTA}[Wait] {worker_id} - Waiting 4s to return to Family screen...{Style.RESET_ALL}")
            time.sleep(4.0)

            max_check = 30
            check = 0
            while   check < max_check:
                check += 1

                '''if d(textContains="cannot Start Family Sharing").exists:
                    print(colored(f"{worker_id} -  cannot Start Family Sharing.", "red"))
                    time.sleep(1)
                    wait_for_element(d, text="OK")
                    time.sleep(1.5)
                    fast_tap_element(d,worker_id, text="OK")
                    time.sleep(1)
                    account_limit_reached = True
                    #return i, True
                    break'''
                if d(textContains="cannot Start Family Sharing").exists:
                    print(colored(f"{worker_id} - cannot Start Family Sharing.", "red"))
                    time.sleep(1)
                    wait_for_element(d, text="OK")
                    time.sleep(1.5)
                    fast_tap_element(d, worker_id, text="OK")
                    time.sleep(1)
                    return "ACCOUNT_LIMIT"

            return "OK"

            #return True

        except Exception as e:
            print(f"{Fore.RED}[-] {worker_id} - Error during family sharing reset: {e}{Style.RESET_ALL}")
            try:
                #d.press("back");
                press_key(emulator, KEY_ESC)
                time.sleep(1)
            except:
                pass
            return False




    child_password, ans1, ans2, ans3, use_proxy, proxy_string = load_config()

    # Parse proxy if enabled
    proxy_dict = None
    if use_proxy and proxy_string:
        proxy_dict = parse_proxy(proxy_string)
        if proxy_dict:
            print(f"{Fore.GREEN}[+] W{worker_id} - Proxy loaded")
        else:
            print(f"{Fore.YELLOW}[!] W{worker_id} - Invalid proxy format, running without proxy")

    def test():
        print(colored(f'{worker_id} -cannot be completed', 'red'))
        time.sleep(3)
        wait_for_element(d, text="OK")
        time.sleep(1)

        child_email = account_name + "@icloud.com"
        child_password = password
        ans1 = answer1
        ans2 = answer2
        ans3 = answer3

        aging_queue.put((worker_id, proxy_dict, child_email, child_password, ans1, ans2, ans3))

        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Ask to Buy").wait(timeout=30.0):
            print(
                colored(f"{worker_id} -Timeout: 'Ask to Buy' not found after 30 seconds, proceeding to next step",
                        'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")
        # wait_for_element(d, text="Ask to Buy")
        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Terms & Conditions").wait(timeout=30.0):
            print(colored(
                f"{worker_id} -Timeout: 'Terms & Conditions' not found after 30 seconds, proceeding to next step",
                'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")
        # wait_for_element(d, text="Terms & Conditions")
        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Terms & Conditions").wait(timeout=30.0):
            print(colored(
                f"{worker_id} -Timeout: 'Terms & Conditions' not found after 30 seconds, proceeding to next step",
                'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")
        # wait_for_element(d, text="Terms & Conditions")
        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Question").wait(timeout=30.0):
            print(colored(f"{worker_id} -Timeout: 'Question' not found after 30 seconds, proceeding to next step",
                          'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")
        # wait_for_element(d, text="Question")
        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Child's Name").wait(timeout=30.0):
            print(colored(
                f"{worker_id} -Timeout: 'Child's Name' not found after 30 seconds, proceeding to next step",
                'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")
        # wait_for_element(d, text="Child's Name")
        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Create Apple ID").wait(timeout=30.0):
            print(colored(
                f"{worker_id} -Timeout: 'Create Apple ID' not found after 30 seconds, proceeding to next step",
                'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")
        # wait_for_element(d, text="Create Apple ID")
        os.system(f"adb -s {emulator} shell input keyevent 4")
        time.sleep(0.3)
        if not d(text="Child's Name").wait(timeout=30.0):
            print(colored(
                f"{worker_id} -Timeout: 'Child's Name' not found after 30 seconds, proceeding to next step",
                'yellow'))
            os.system(f"adb -s {emulator} shell input keyevent 4")

        time.sleep(1)
        error_type = "Error  cannot"


    def lag(d):
        os.system(f"adb -s {emulator} shell input keyevent 4")
        #os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')
        d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').wait()
        time.sleep(0.5)
        d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
        wait_for_element(d, text="Cancel Apple ID Creation?")
        time.sleep(0.5)
        fast_tap_element(d,worker_id, text="OK")
        time.sleep(0.5)
        wait_for_element(d, text="Organizer")
        first_of_acc()

    # Define lag() and lag_1() functions outside the loop

    def lag_1(d):
        if not d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').exists:
            os.system(f"adb -s {emulator} shell am force-stop {package_name}") #test
            time.sleep(2)
            os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')
            d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').wait()
            time.sleep(0.5)
            d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
        else:
            d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').wait()
            time.sleep(0.5)
            d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()

        '''d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()'''
        if d(text="Organizer").wait(timeout=3.0):
            print(colored(f"{worker_id} -child  {i + 1}/{mazen}", "blue"))

        scrollable_element = d(scrollable=True)
        if scrollable_element.exists:
            time.sleep(1)
            scrollable_element.scroll.backward(steps=15)


    def lag_2(d):
        press_key(emulator, KEY_ESC)
        os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')
        '''d.xpath('//android.widget.ImageButton[@content-desc="Navigate up"]').click()
        wait_for_element(d, text="Cancel Apple ID Creation?")
        time.sleep(0.5)
        fast_tap_element(d, text="OK")
        time.sleep(0.5)'''
        wait_for_element(d, text="Organizer")



    def lag_3(d):
        os.system(f"adb -s {emulator} shell am force-stop {package_name}")
        time.sleep(1)
        d.app_start("com.apple.android.music", stop=True)
        time.sleep(2)
        os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')
        wait_for_element(d, text="Organizer")




    package_name = "com.apple.android.music"
    faker_package = "com.android1500.androidfaker"

    os.system(f'"{ADB_PATH}" -s {emulator} shell pm clear {package_name}')
    print(colored(f"Done clearing storage for {emu_name}.", "green"))

    time.sleep(1)

    print(colored(f"Launching Android Faker on {emu_name}...", "blue"))  # Android Faker
    d.app_start("com.android1500.androidfaker", stop=True)
    d.app_start("com.android1500.androidfaker", stop=True)
    #os.system(f"adb -s {emulator} shell monkey -p {faker_package} -c android.intent.category.LAUNCHER 1 >nul 2>&1")
    #time.sleep(random.uniform(2.5, 4.0))

    if wait_for_element(d, text="Android Faker") or wait_for_element(d, text="Edit"):
        time.sleep(0.3)
        if not safe_click(
                d,
                worker_id,
                resource_id="com.android1500.androidfaker:id/rnd_all",timeout=15
        ):
            print(colored(f"{worker_id} - Android Faker rnd_all not available, skipping faker step", "yellow"))

        print(colored(f"Done changing data by Android Faker on {emu_name}...", "green"))
    else:
        print(colored(f"Timeout: 'Edit' not found, proceeding to next step", 'yellow'))

    time.sleep(1)
    os.system(f"adb -s {emulator} shell am force-stop {faker_package}")
    time.sleep(1)

    time.sleep(1)
    d.app_start("com.apple.android.music", stop=True)
    time.sleep(2)
    os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')




    wait_for_element(d, text="Sign In")
    time.sleep(0.3)
    press_key(emulator, KEY_TAB)
    press_key(emulator, KEY_TAB)
    d.send_keys(email)
    press_key(emulator, KEY_TAB)
    d.send_keys(pwd_from_file)
    fast_tap_element(d,worker_id, text="Sign In")

    #print(colored(f"{email}\ncannot Start Family Sharing.", "red"))

    # Check login status
    login_timeout = time.time() + 30
    login_failed = False
    while d.xpath('//*[@resource-id="com.apple.android.music:id/signin_title_tv"]').exists:
        if time.time() > login_timeout:
            print(colored(f"{worker_id} -Login timeout for {email}", "red"))
            append_to_fail_file(account_data)
            login_failed = True
            break

        if d.xpath(
                '//*[@text="You entered the account information incorrectly. Check the account and try again."]').exists or \
                d(textContains="You entered the account information incorrectly").exists:
            error_text = d.xpath(
                '//[@text="You entered the account information incorrectly. Check the account and try again."]').get_text().strip() if d.xpath(
                '//[@text="You entered the account information incorrectly. Check the account and try again."]').exists else d(
                textContains="You entered the account information incorrectly").get_text().strip()
            print(colored(f"{worker_id} -Account {email} failed: {error_text}", "red"))
            append_to_fail_file(account_data)
            press_key(emulator, KEY_ESC)
            login_failed = True
            break

        if d.xpath('//*[@resource-id="com.apple.android.music:id/title"]').exists:
            error_text = d.xpath('//*[@resource-id="com.apple.android.music:id/title"]').get_text().strip()
            print(colored(f"{worker_id} -Account {email} failed: {error_text}", "red"))
            if "This Apple Account has been disabled for security reasons" in error_text:
                print(colored(f"{worker_id} -Account {email} is disabled, saving to locked.txt", "red"))
                append_to_locked_file(account_data)
            else:
                print(colored(f"{worker_id} -Account {email} failed for other reasons, moving to fail.txt", "red"))
                append_to_fail_file(account_data)
            press_key(emulator, KEY_ESC)
            login_failed = True
            break

    if login_failed:
        return 0, False




    family_reached = False

    for t in range(3):
        if family_reached: break

        # Send ADB Command (Inject)
        # os.system(f'adb -s {emulator} shell "su -c am start -n com.apple.android.music/.icloud.activities.FamilyInfoActivity"')

        # Wait and Check UI
        for check in range(4):

            if d(textContains="cannot Start Family Sharing").exists:
                time.sleep(1)
                wait_for_element(d, text="OK")
                time.sleep(1.5)
                fast_tap_element(d,worker_id, text="OK")
                time.sleep(1)
                error_type = "Error 1 maximum"
                account_limit_reached = True
                print(colored(f"{email}\ncannot Start Family Sharing.", "red"))
                family_reached = True
                break

            time.sleep(1)


            # A. Success Check
            if d(text="Organizer").exists or d(textContains="Add Family Member").exists:
                print(colored(f"{worker_id} -Family Screen Reached! {emu_name}", "green"))
                family_reached = True
                break

            # B. Handle "Continue"
            if d(text="Continue").exists:
                print(colored(f"{worker_id} -Clicking Continue... {emu_name}", "green"))
                #d(text="Continue").click()
                safe_click(d, worker_id, text="Continue")
                time.sleep(2)
                continue

            # C. Handle Password Popup
            if d(text="Sign In").exists or d(textContains="password").exists:
                if d(className="android.widget.EditText").exists:
                    print(colored(f"{worker_id} -Handling Re-Auth Popup... {emu_name}", "yellow"))
                    try:
                        d(className="android.widget.EditText").set_text(pwd_from_file)
                        time.sleep(0.5)
                        if d(text="SIGN IN").exists:
                            d(text="SIGN IN").click()
                        elif d(text="Sign In").exists:
                            d(text="Sign In").click()
                        print(colored(f"{worker_id} -Waiting 5s after popup... {emu_name}", "yellow"))
                        time.sleep(5)
                    except:
                        pass
                    continue

            time.sleep(1.5)

        if family_reached: break

    if not family_reached:
        print(colored(f"{worker_id} -Force checking 'Continue' one last time...{emu_name}", "yellow"))
        if d(text="Continue").exists:
            #d(text="Continue").click()
            safe_click(d, worker_id, text="Continue")




    TOTAL_BATCHES = 4  # 14 × 4 = 56

    for batch in range(TOTAL_BATCHES):
        print(colored(f"\n{worker_id} - Starting batch {batch + 1}/{TOTAL_BATCHES}\n", "cyan"))

        # Initialize flag and counter
        i = 0
        #account_limit_reached = False

        while i < mazen and not account_limit_reached:



            def first_of_acc ():
                while i < mazen and not account_limit_reached:
                    if wait_for_element(d, text="Organizer") or wait_for_element(d, text="Create an Apple ID"):
                        print(colored(f"{worker_id} - start ", "blue"))
                    else:
                        print(colored(f"{worker_id} -Timeout: 'Organizer' not found, proceeding to next step", 'yellow'))

                    scrollable_element = d(scrollable=True)
                    if scrollable_element.exists:
                        time.sleep(1)
                        scrollable_element.scroll.forward(steps=15)
                    else:
                        print(f"{worker_id} -No scrollable element found")
                    time.sleep(1)
                    if d(textContains="Add Family Member").exists:
                        time.sleep(2)
                        optimized_tap2(d,worker_id, text="Add Family Member")
                    else:
                        remove_children(d, worker_id)

                        scrollable_element = d(scrollable=True)
                        if scrollable_element.exists:
                            time.sleep(1)
                            scrollable_element.scroll.forward(steps=15)
                        else:
                            print(f"{worker_id} -No scrollable element found")

                        time.sleep(2)
                        optimized_tap2(d,worker_id, text="Add Family Member")

                    if not d(text="Security code").wait(timeout=30.0):
                        print(colored(f"{worker_id} - Timeout: 'Security code' not found after 30 seconds Trying again", 'red'))
                        lag_1(d)  # Reset the state
                        continue  # Retry this iteration from the start

                    if wait_for_element(d, text="Security code"):
                        optimized_tap2(d,worker_id, text="Security code")
                        d.send_keys(cvv)
                        time.sleep(0.2)
                        fast_tap_element(d,worker_id, text="Next")
                        print(colored(f"{worker_id} -Trying to pass CVV", "yellow"))
                    else:
                        print(colored(f"{worker_id} -Timeout: 'Security code' not found, proceeding to next step", 'yellow'))

                    max_attempts = 10
                    attempt = 0
                    while attempt < max_attempts:
                        if d(text="Verification Required").wait(timeout=5.0):
                            if d(textContains="Invalid Security code").wait(timeout=5.0):
                                print(colored(f"{worker_id} -Attempt {attempt + 1}:'Invalid Security Code'", "yellow"))
                                if d(text="OK").wait(timeout=5.0):
                                    time.sleep(0.5)
                                    fast_tap_element(d,worker_id, text="OK")
                                    time.sleep(0.5)
                                else:
                                    print(colored(f"{worker_id} -Error: 'OK' not found, proceeding to next step", "yellow"))
                                    break
                                enter_cvv(d, cvv , worker_id)
                                attempt += 1
                            else:
                                print(colored(f"{worker_id} -No 'Invalid Security Code' found, proceeding...", "green"))
                                break
                        else:
                            print(colored(f"{worker_id} -No 'Verification Required' found, proceeding...", "green"))
                            break

                    if attempt >= max_attempts:
                        print(colored(f"{worker_id} -Failed to pass CVV after 10 attempts, moving to next account", "red"))
                        lag(d)
                        continue
                    else:
                        print(colored(f"{worker_id} -CVV success", "green"))
                        start_time = time.time()
                        timeout = 20.0
                        found_element = False
                        while time.time() - start_time < timeout:
                            create_element = d(text="Create an Apple ID for a Child")
                            if create_element.wait(timeout=5.0):
                                print(colored(f"{worker_id} -waiting 2 seconds for 'ALLOW'...", "yellow"))
                                time.sleep(2.0)
                                if d(text="ALLOW").exists:
                                    time.sleep(0.2)
                                    fast_tap_element(d,worker_id, text="ALLOW")

                                time.sleep(0.2)
                                create_element.click()

                                found_element = True
                                break
                            elif d(text="ALLOW").exists:
                                time.sleep(0.2)
                                fast_tap_element(d,worker_id, text="ALLOW")

                                create_element = d(text="Create an Apple ID for a Child")
                                if create_element.wait(timeout=5.0):
                                    time.sleep(2.0)
                                    create_element.click()

                                    found_element = True
                                    break
                                else:
                                    break

                    element = d(text="Next")
                    if not d(text="Next").wait(timeout=30.0):
                        print(colored(f"{worker_id} - Timeout: 'Next' not found after 30 seconds Trying again", 'red'))
                        lag(d)  # Reset the state
                        continue  # Retry this iteration from the start
                    if element.wait(timeout=20.0):
                        time.sleep(0.2)
                        element.click()

                    else:
                        print(colored(f"{worker_id} -Error: 'Next' not found, checking for 'Birthday'...", "yellow"))
                        if d(text="Birthday").wait(timeout=20):
                            print(colored(f"{worker_id} -'Birthday' ", "green"))
                        else:
                            print(colored(f"{worker_id} -Neither 'Next' nor 'Birthday' found, proceeding to next step...", "yellow"))

                    try:
                        element = d(text="Birthday")
                        if not element.wait(timeout=30.0):
                            print(colored(f"{worker_id} -Timeout: 'Birthday' not found after 30 seconds, proceeding to next step",
                                          "yellow"))
                            lag(d)  # Reset the state
                            continue  # Retry this iteration from the start
                        else:
                            element.click()
                    except Exception as e:
                        print(colored(f"{worker_id} -Script crashed with error: {str(e)}", "red"))

                    if not d(text="2026").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: '2026' not found after 30 seconds, proceeding to next step", 'yellow'))
                        lag_2(d)  # Reset the state
                        continue  # Retry this iteration from the start
                    else:
                        fast_tap_element(d,worker_id, text="2026")
                        d(scrollable=True).scroll.to(text="2022")
                        d(scrollable=True).scroll.to(text="2018")
                        d(scrollable=True).scroll.to(text="2013")
                        if not d(text="2013").wait(timeout=30.0):
                            print(colored(f"{worker_id} -Timeout: '2013' not found after 30 seconds, proceeding to next step",
                                          'yellow'))
                            lag_2(d)  # Reset the state
                            continue  # Retry this iteration from the start
                        else:
                            optimized_tap2(d,worker_id, text="2013")

                    today = datetime.today().day
                    fast_tap_element(d,worker_id, text=str(today + 1))
                    if not d(text="OK").wait(timeout=25.0):
                        print(colored(f"{worker_id} -Timeout: 'OK' not found after 25 seconds, proceeding to next step", 'yellow'))
                        lag_2(d)  # Reset the state
                        continue  # Retry this iteration from the start
                    else:
                        fast_tap_element(d,worker_id, text="OK")

                    if not d(text="Confirm").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: 'Confirm' not found after 30 seconds, proceeding to next step", 'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        fast_tap_element(d,worker_id, text="Confirm")

                    if not d(text="Agree").wait(timeout=30.0):
                        print(
                            colored(f"{worker_id} -Timeout: ' Agree' not found after 30 seconds, proceeding to next step", 'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        wait_for_element(d, text="Agree")
                        time.sleep(0.8)
                        fast_tap_element(d,worker_id, text="Agree")

                    if not d(text="First name").wait(timeout=30.0):
                        print(
                            colored(f"{worker_id} -Timeout: 'First name' not found after 30 seconds, proceeding to next step",
                                    'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        wait_for_element(d, text="First name")
                        fast_tap_element(d,worker_id, text="First name")
                        first_name = fake.first_name()
                        while first_name == "Christopher":
                            first_name = fake.first_name()
                        d.send_keys(first_name)

                    if not d(text="Last name").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: 'Last name' not found after 30 seconds, proceeding to next step",
                                      'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        fast_tap_element(d,worker_id, text="Last name")
                        last_name = fake.last_name()
                        while last_name == "Christopher":
                            last_name = fake.last_name()
                        d.send_keys(last_name)
                    break

            first_of_acc()

            MAX_ACCOUNTS = [5, 10, 14]
            stage = 0
            counts = [5, 5, 4]

            while stage < len(counts):
                counter = 0

                while counter < counts[stage]:

                    if i >= 14:
                        print(colored(f"{worker_id} -Global account limit reached ({i}) → stopping before new attempt", "red"))
                        goto_exit = True
                        break

                    print(colored(f"{worker_id} -child  {i + 1}/{mazen}", "blue"))

                    first_name = fake.first_name()
                    while first_name == "Christopher":
                        first_name = fake.first_name()

                    last_name = fake.last_name()
                    while last_name == "Christopher":
                        last_name = fake.last_name()

                    if not d(text="Next").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: 'Next' not found after 30 seconds, proceeding to next step",'yellow'))
                        lag(d)  # Reset the state
                        continue

                    else:
                        fast_tap_element(d,worker_id, text="Next")

                    if not d(text="Create Apple ID").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: 'Create Apple ID' not found after 30 seconds, proceeding to next step","yellow"))
                        lag(d)  # Reset the state
                        continue
                    else:
                        if not d(text="Create Apple ID").wait(timeout=20.0):
                            print(colored(f"{worker_id} -Error: 'Create Apple ID' not found after 5 seconds, proceeding to next step","yellow"))
                        else:
                            press_key(emulator, KEY_TAB)

                            if i % 2 == 0:
                                x = "."
                            else:
                                x = "_"
                            # {x}
                            account_name = f"{first_name}M{last_name}X{generate_n_digit_number(3)}"
                            d.send_keys(account_name)

                            if not d(text="Next").wait(timeout=30.0):
                                print(colored(f"{worker_id} -Timeout: 'Next' not found after 30 seconds, proceeding to next step","yellow"))
                                lag(d)  # Reset the state
                                continue
                            else:
                                time.sleep(0.5)
                                fast_tap_element(d,worker_id, text="Next")

                            account_name = Try_Another_Apple_ID(d, account_name, emulator,worker_id)
                            child_email = account_name + "@icloud.com"

                    if use_random:
                        password = random.choice(SINGLE_WORD_password)
                        answer1 = fake.first_name()
                        answer2 = random.choice(SINGLE_WORD_JOBS)
                        answer3 = random.choice(SINGLE_WORD_CITIES)
                    else:
                        password = get_Pass()
                        answer1 = answers_dict.get("q1", "No Answer")
                        answer2 = answers_dict.get("q2", "No Answer")
                        answer3 = answers_dict.get("q3", "No Answer")

                    if use_random:
                        print(colored(f"{worker_id} -random password and answers  {i + 1}", "blue"))
                    else:
                        print(colored(f"{worker_id} -password and answers from files {i + 1}", "blue"))

                    if not d(text="Password").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: 'Password' not found after 30 seconds, proceeding to next step",
                                      'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        wait_for_element(d, text="Password", timeout=5)
                        fast_tap_element(d,worker_id, text="Password")
                        d.send_keys(password)
                        time.sleep(0.5)
                        fast_tap_element(d,worker_id, text="Confirm password")
                        d.send_keys(password)
                        fast_tap_element(d,worker_id, text="Next")

                    if not d(text="Question").wait(timeout=30.0):
                        print(colored(f"{worker_id} -Timeout: 'Question' not found after 30 seconds, proceeding to next step",
                                      'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        wait_for_element(d, text="Question")
                        press_key(emulator, KEY_TAB)
                        press_key(emulator, KEY_ENTER)
                        press_key(emulator, KEY_ENTER)
                        press_key(emulator, KEY_TAB)
                        d.send_keys(answer1)
                        press_key(emulator, KEY_TAB)
                        press_key(emulator, KEY_ENTER)
                        press_key(emulator, KEY_ENTER)
                        press_key(emulator, KEY_TAB)
                        d.send_keys(answer2)
                        press_key(emulator, KEY_TAB)
                        press_key(emulator, KEY_ENTER)
                        press_key(emulator, KEY_ENTER)
                        press_key(emulator, KEY_TAB)
                        d.send_keys(answer3)
                        error_type = ""
                        fast_tap_element(d,worker_id, text="Next")

                    if not d(text="Agree").wait(timeout=30.0):
                        print(
                            colored(f"{worker_id} -Timeout: ' Agree' not found after 30 seconds, proceeding to next step", 'yellow'))
                        lag(d)  # Reset the state
                        continue
                    else:
                        wait_for_element(d, text="Agree")
                        time.sleep(1.5)
                        fast_tap_element(d,worker_id, text="Agree")

                    if not d(text="Terms & Conditions").wait(timeout=40.0):
                        print(
                            colored(f"{worker_id} -Timeout: 'Terms & Conditions' not found after 15 seconds, proceeding to next step",
                                    'yellow'))
                    else:
                        wait_for_element(d, text="Terms & Conditions")
                        fast_tap_element(d,worker_id, text="AGREE")
                        time.sleep(1)
                        wait_for_element(d, text="Agree")
                        time.sleep(1.5)
                        fast_tap_element(d,worker_id, text="Agree")
                        time.sleep(1)
                        if not d(text="Terms & Conditions").wait(timeout=40.0):
                            print(colored(f"{worker_id} -Timeout: 'Terms & Conditions' not found after 15 seconds, proceeding to next step",'yellow'))
                        else:
                            wait_for_element(d, text="Terms & Conditions")
                            fast_tap_element(d,worker_id, text="AGREE")

                    if not d(text="Next").wait(timeout=40.0):
                        print(colored(f"{worker_id} -Timeout: 'Next' not found after 10 seconds, proceeding to next step", 'yellow'))
                    else:
                        wait_for_element(d, text="Next")
                        fast_tap_element(d,worker_id, text="Next")

                    # Check for "Ask to Buy" and handle errors
                    if not d(text="Ask to Buy").wait(timeout=40.0):
                        print(colored(f"{worker_id} -Timeout: 'Ask to Buy' not found after 15 seconds, proceeding to next step",'yellow'))
                        continue  # Skip to next iteration if "Ask to Buy" isn't found
                    else:
                        error_occurred = False

                        def test():
                            print(colored(f'{worker_id} -cannot be completed', 'red'))
                            time.sleep(3)
                            wait_for_element(d, text="OK")
                            time.sleep(1)

                            child_email = account_name + "@icloud.com"
                            child_password = password
                            ans1 = answer1
                            ans2 = answer2
                            ans3 = answer3



                            aging_queue.put((worker_id, proxy_dict, child_email, child_password, ans1, ans2, ans3))

                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Ask to Buy").wait(timeout=30.0):
                                print(
                                    colored(f"{worker_id} -Timeout: 'Ask to Buy' not found after 30 seconds, proceeding to next step",
                                            'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")
                            # wait_for_element(d, text="Ask to Buy")
                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Terms & Conditions").wait(timeout=30.0):
                                print(colored(
                                    f"{worker_id} -Timeout: 'Terms & Conditions' not found after 30 seconds, proceeding to next step",
                                    'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")
                            # wait_for_element(d, text="Terms & Conditions")
                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Terms & Conditions").wait(timeout=30.0):
                                print(colored(
                                    f"{worker_id} -Timeout: 'Terms & Conditions' not found after 30 seconds, proceeding to next step",
                                    'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")
                            # wait_for_element(d, text="Terms & Conditions")
                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Question").wait(timeout=30.0):
                                print(colored(f"{worker_id} -Timeout: 'Question' not found after 30 seconds, proceeding to next step",
                                              'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")
                            # wait_for_element(d, text="Question")
                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Child's Name").wait(timeout=30.0):
                                print(colored(
                                    f"{worker_id} -Timeout: 'Child's Name' not found after 30 seconds, proceeding to next step",
                                    'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")
                            # wait_for_element(d, text="Child's Name")
                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Create Apple ID").wait(timeout=30.0):
                                print(colored(
                                    f"{worker_id} -Timeout: 'Create Apple ID' not found after 30 seconds, proceeding to next step",
                                    'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")
                            # wait_for_element(d, text="Create Apple ID")
                            os.system(f"adb -s {emulator} shell input keyevent 4")
                            time.sleep(0.3)
                            if not d(text="Child's Name").wait(timeout=30.0):
                                print(colored(
                                    f"{worker_id} -Timeout: 'Child's Name' not found after 30 seconds, proceeding to next step",
                                    'yellow'))
                                os.system(f"adb -s {emulator} shell input keyevent 4")


                            time.sleep(1)
                            error_type = "Error  cannot"

                        error_occurred = False
                        max_checks = 60
                        checks = 0

                        while checks < max_checks:
                            checks += 1
                            time.sleep(0.7)  # مهم جدًا عشان UI يلحق يظهر

                            # ❌ Cannot start family sharing
                            if d(textContains="cannot Start Family Sharing").exists:
                                print(colored(f"{worker_id} - {email} cannot Start Family Sharing.", "red"))
                                time.sleep(1)
                                wait_for_element(d, text="OK")
                                time.sleep(1.5)
                                fast_tap_element(d, worker_id, text="OK")
                                time.sleep(1)
                                account_limit_reached = True
                                return i, True

                            # ❌ Maximum of fifteen people
                            if d(textContains="maximum of fifteen").exists:
                                print(colored(f'{worker_id} -maximum of fifteen', 'red'))
                                time.sleep(1)
                                wait_for_element(d, text="OK")
                                time.sleep(1.5)
                                fast_tap_element(d, worker_id, text="OK")
                                time.sleep(1)
                                error_type = "Error 1 maximum"
                                error_occurred = True
                                time.sleep(1)
                                remove_children(d, worker_id)
                                time.sleep(1)
                                # reset_family_sharing(d, worker_id)
                                result = reset_family_sharing(d, worker_id)

                                i = 0  # test

                                if result == "ACCOUNT_LIMIT":
                                    print(colored(f"{worker_id} - Account limit reached → moving to next MAIN account","red"))
                                    return i, True  # ⬅️ دي اللي بتخلّي process_emulator يروح للإيميل اللي بعده

                                time.sleep(5)

                                first_of_acc()

                                break

                            # ⚠️ Cannot be completed (Retry)
                            if d(textContains="cannot be completed").exists or \
                                    d(textContains="This action cannot").exists:
                                print(colored(f"{worker_id} - Temporary error, retrying...", "yellow"))
                                test()
                                time.sleep(1)
                                continue

                            # ✅ لو مفيش Ask to Buy → نخرج
                            if not d(text="Ask to Buy").exists:
                                break

                            time.sleep(1)

                        '''error_occurred = False
                        max_checks = 60
                        checks = 0
                        #not error_occurred and
                        while  checks < max_checks:
                            checks += 1


                            if d(textContains="cannot Start Family Sharing").exists:
                                print(colored(f"{worker_id} - {email} cannot Start Family Sharing.", "red"))
                                time.sleep(1)
                                wait_for_element(d, text="OK")
                                time.sleep(1.5)
                                fast_tap_element(d,worker_id, text="OK")
                                time.sleep(1)
                                account_limit_reached = True
                                return i, True
                                #break


                            if d(text='You can invite a maximum of fifteen people to Family Sharing in a year.').exists:
                                print(colored(f'{worker_id} -maximum of fifteen', 'red'))
                                time.sleep(1)
                                wait_for_element(d, text="OK")
                                time.sleep(1.5)
                                fast_tap_element(d,worker_id, text="OK")
                                time.sleep(1)
                                error_type = "Error 1 maximum"
                                error_occurred = True
                                time.sleep(1)
                                remove_children(d, worker_id)
                                time.sleep(1)
                                #reset_family_sharing(d, worker_id)
                                result = reset_family_sharing(d, worker_id)

                                i=0 #test

                                if result == "ACCOUNT_LIMIT":
                                    print(colored(f"{worker_id} - Account limit reached → moving to next MAIN account",
                                                  "red"))
                                    return i, True  # ⬅️ دي اللي بتخلّي process_emulator يروح للإيميل اللي بعده

                                time.sleep(5)

                                first_of_acc()

                                break

                            #️ Error cannot be completed
                            if d(textContains="cannot be completed").exists or \
                                    d(text="This action cannot be completed at this time.").exists:
                                test()
                                time.sleep(1)
                                continue

                            # ️ Error cannot be completed
                            if d(text="This action cannot be completed at this time.").exists:
                                test()
                                time.sleep(1)
                                continue

                            # ️ Error cannot be completed
                            if d(textContains="cannot be completed").exists:
                                test()
                                time.sleep(1)
                                continue

                            if d(textContains="This action cannot").exists:
                                test()
                                time.sleep(1)
                                continue


                            if not d(text="Ask to Buy").exists:
                                break

                            time.sleep(1)'''

                        AGED_DATE = "01/01/1990"
                        def Save_account():

                            finished_time = datetime.now().strftime('%H:%M')
                            with open("accounts.txt", "a") as file:
                                file.write(
                                    account_name + "@icloud.com," +
                                    password + ',' +
                                    formatted_tomorrow + ',' +
                                    answer1 + ',' +
                                    answer2 + ',' +
                                    answer3 + ',' +
                                    finished_time + ',' +
                                    error_type + "\n"
                                )

                        if not error_occurred:


                            # Only save account if no error occurred
                            Save_account()
                            print(colored(f"{worker_id} -Finished child  {i + 1}/{mazen}", "green"))
                            i += 1
                            counter += 1
                            # total_created += 1

                            print(colored(f"{worker_id} -Finished account {i}", "green"))

                            # age_child(worker_id, proxy_dict, child_email, child_password, ans1, ans2, ans3)
                            # aged = age_child_with_retry(worker_id, proxy_dict, child_email, child_password, ans1, ans2,ans3)

                            if i in MAX_ACCOUNTS:
                                print(colored(f"{worker_id} -Reached account limit ({i}) → exiting all loops", "red"))
                                goto_exit = True
                                break



                        elif account_limit_reached:
                            # If max limit reached, stop loop and notify
                            print(colored(
                                f"{worker_id} -Maximum invitation limit reached for {email}. Stopping child account creation.",
                                "red"))
                        else:
                            # Other errors: skip this account but continue
                            print(colored(f"{worker_id} -Error occurred for child account {i + 1}, skipping.", "yellow"))
                            counter += 1

                if 'goto_exit' in locals() and goto_exit:
                    break

                print(f"{worker_id} - finsh stage {stage + 1}")
                stage += 1

            lag_3(d)
            wait_for_element(d, text="Organizer")


        # Cleanup and final steps
        print(colored(f"{worker_id} -Account creation completed for {email}", "green"))
        if account_limit_reached :
            return i, True
        else:
            remove_children(d, worker_id)
            #reset_family_sharing(d, worker_id )
            result = reset_family_sharing(d, worker_id)

            if result == "ACCOUNT_LIMIT":
                print(colored(f"{worker_id} - Account limit reached → moving to next MAIN account", "red"))
                return i, True  # ⬅️ دي اللي بتخلّي process_emulator يروح للإيميل اللي بعده

            time.sleep(5)

    return i, True


def main():
    display_banner()

    # Ask the user how many emulators they want to control
    num_emulators = int(input(colored("How many emulators do you want to control? ", "blue")))

    # Ask about the number of child accounts per main account
    #mazen = int(input(colored("Enter the number of child accounts you want to create for each account: ", "blue")))

    # Ask about using random password and answers
    print(colored("Do you want to use random passwords and answers for child accounts? (y/n)", "blue"))
    choice = input().lower()
    use_random = choice == 'y'

    if not use_random:
        if not get_Pass():
            print(colored("Fatal: password required but missing.", "red"))
            input(colored("Press Enter to exit...", "yellow"))
            sys.exit(1)

    # Get the list of running emulators
    emulators = list_emulators()
    if not emulators:
        print(colored("No running emulators found!", "red"))
        return

    # If the number of available emulators is less than requested, use only what's available
    if len(emulators) < num_emulators:
        print(colored(f"Number of available emulators ({len(emulators)}) is less than requested, using only available ones.", "yellow"))
        num_emulators = len(emulators)

    selected_emulators = emulators[:num_emulators]

    emulator_map = {}
    for idx, emu in enumerate(selected_emulators, start=1):
        emulator_map[emu] = f"EMULATOR-{idx}"

    print(colored(f"Will control {len(selected_emulators)} emulators: {selected_emulators}", "green"))

    # Fetch accounts from the file
    accounts = get_all_email_password_cvv()
    if not accounts:
        print(colored("No valid accounts found in Email&Password&CVV.txt.", "red"))
        return


    # Divide accounts among emulators
    accounts_per_emulator = len(accounts) // len(selected_emulators)
    threads = []

    aging_workers = []

    for emulator in selected_emulators:
        t = threading.Thread(target=aging_worker, daemon=True)
        #t = threading.Thread(target=aging_worker,args=(emulator,),daemon=True)
        t.start()
        aging_workers.append(t)

    for i, emulator in enumerate(selected_emulators):
        start_idx = i * accounts_per_emulator
        end_idx = start_idx + accounts_per_emulator if i < len(selected_emulators) - 1 else len(accounts)
        emulator_accounts = accounts[start_idx:end_idx]

        # Run each emulator in a separate thread
        #thread = threading.Thread(target=process_emulator, args=(emulator, emulator_accounts, use_random, mazen))
        #thread = threading.Thread(target=process_emulator,args=( emulator, emulator_map[emulator],emulator_accounts,use_random,mazen))
        thread = threading.Thread(target=safe_process_emulator,args=(emulator, emulator_map[emulator], emulator_accounts, use_random, mazen),daemon=True)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(colored("Finished running all emulators!", "green"))
    try:
        input(colored("Press Enter to exit...", 'blue'))
    except:
        pass

    #input(colored("Press Enter to exit...", 'blue'))


if __name__ == "__main__":
    main()