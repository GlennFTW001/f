import asyncio
import aiohttp
import random
import os
import ctypes
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

def print_banner():
    print(f"{Fore.LIGHTYELLOW_EX}{'Proxy Checker'}\n     {'By Cr0mb'}{Style.RESET_ALL}")

def set_window_title(title):
    if os.name == 'posix':
        print(f'\033]0;{title}\007', end='', flush=True)
    elif os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(title)

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_totals(counter):
    print(f"\nTotal proxies checked: {counter['total']}")
    print(f"Total active proxies found: {counter['active']}")

async def test_proxy(session, proxy, proxy_type, timeout=5):
    url = 'http://httpbin.org/status/200'
    proxy_url = f"{proxy_type}://{proxy}"
    try:
        async with session.get(url, proxy=proxy_url, timeout=timeout) as response:
            if response.status == 200:
                return True
    except (aiohttp.ClientError, asyncio.TimeoutError):
        pass
    return False

async def scan_for_proxies(session, proxy_type, counter, common_ports, unlimited=False, num_proxies=0):
    while unlimited or counter['total'] < num_proxies:
        ip_address = '.'.join(str(random.randint(1, 255)) for _ in range(4))
        port = random.choice(common_ports)
        proxy = f"{ip_address}:{port}"

        if await test_proxy(session, proxy, proxy_type):
            clear_screen()
            print_banner()
            set_window_title("Proxy Checker")
            print(f"{Fore.GREEN}[+] {proxy_type.upper()} Proxy found: {proxy}{Style.RESET_ALL}")
            write_to_file(proxy)  # Write the working proxy to file
            counter['active'] += 1
        else:
            clear_screen()
            print_banner()
            set_window_title("Proxy Checker")
            print(f"{Fore.RED}[-] {proxy_type.upper()} Proxy not working: {proxy}{Style.RESET_ALL}")
        counter['total'] += 1
        print_totals(counter)

def write_to_file(proxy):
    with open('proxies.txt', 'a') as file:
        file.write(f"{proxy}\n")

async def main():
    parser = argparse.ArgumentParser(description='Proxy Checker', add_help=False)
    parser.add_argument('-t', choices=['http', 'https'], default='https', help='Type of proxies to scan (http, https)')
    parser.add_argument('-b', '--both', action='store_true', help='Scan both HTTP and HTTPS proxies')
    parser.add_argument('-u', action='store_true', help='Scan for unlimited number of proxies')
    parser.add_argument('-n', type=int, default=0, help='Number of proxies to scan (0 for unlimited)')
    parser.add_argument('-i', type=int, default=1, help='Number of instances to run concurrently')
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    args = parser.parse_args()

    if args.n == 0 and args.i == 1 and not args.u:
        # Prompt for input only if necessary arguments are missing or default
        args.n = int(input("Enter the number of proxies to scan (0 for unlimited): "))
        args.i = int(input("Enter the number of instances to run concurrently: "))

    clear_screen()
    print_banner()

    proxy_types = ['http', 'https'] if args.both else [args.t]
    print(f"{Fore.BLACK}Scanning for {', '.join([pt.upper() for pt in proxy_types])} proxies.{Style.RESET_ALL}")

    set_window_title("Proxy Checker")

    num_proxies = args.n if args.n > 0 else 0

    common_ports = [80, 8080, 3128, 8888, 8000, 1080, 1081, 8118, 9090, 9000]

    counter = {
        'total': 0,
        'active': 0
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(args.i):
            for proxy_type in proxy_types:
                tasks.append(scan_for_proxies(session, proxy_type, counter, common_ports, args.u, num_proxies))

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
