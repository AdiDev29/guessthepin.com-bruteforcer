import threading
import requests
import random
import sys
from time import sleep

print("\033[31m")
print("""
  GuessThePin.com Bruteforcer starting...
""")

# Shared flag for stopping all threads when PIN is found
found = threading.Event()

# Shared counter for progress tracking
progress_lock = threading.Lock()
progress = 0

# List to store skipped PINs and track last skipped
skipped_pins = []
last_skipped_pin = "None"
skipped_lock = threading.Lock()


def brute_force(guess: str, total_attempts=10000, display_output=True):
    global progress, last_skipped_pin

    if found.is_set():
        return True  # Stop guessing if PIN is already found

    try:
        payload = {'guess': guess}
        response = requests.post('https://www.guessthepin.com/prg.php', data=payload, timeout=5)

        with progress_lock:
            progress += 1
            print_status(last_skipped_pin, progress, total_attempts)

        if "is not the PIN" not in response.text:
            if display_output:
                print(f"\n✅ The PIN is: {guess}")
            found.set()  # Notify all threads to stop
            return True
        else:
            return False

    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
        with skipped_lock:
            skipped_pins.append(guess)
            last_skipped_pin = guess  # Update last skipped PIN
            print_status(last_skipped_pin, progress, total_attempts)  # Update the status
        return False


def guess_pins():
    while not found.is_set():
        pin = str(random.randint(0, 9999)).zfill(4)
        brute_force(pin, total_attempts=10000)


def print_status(last_pin, current, total):
    percent = (current / total) * 100
    bar_length = 40
    bar = '#' * int(bar_length * percent / 100)
    spaces = ' ' * (bar_length - len(bar))

    sys.stdout.write(f'\rLast skipped PIN: {last_pin:<6} | Progress: [{bar}{spaces}] {percent:.2f}%')
    sys.stdout.flush()


# Main Program
try:
    speed = int(input("Enter speed (number of threads, 1 being slowest, more is faster but may cause instability): "))
    if speed < 1:
        speed = 1
    print(
        f"Running with {speed} threads. Note: Increasing threads improves speed but may cause skipped numbers due to network or server issues.\n")
except ValueError:
    print("Invalid input. Defaulting to 10 threads.")
    speed = 10

threads = []

for _ in range(speed):
    t = threading.Thread(target=guess_pins)
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

print("\n\nProgram finished.")
if skipped_pins:
    print("\n⚠️ Skipped PINs due to errors during execution:")
    print(", ".join(skipped_pins))

if progress == 10000:
    retry_skipped = input("\nAll 10000 combinations tried. Would you like to retry the skipped PINs? (y/n): ")
    if retry_skipped.lower() == 'y':
        print("Retrying skipped PINs with 5 threads...")
        threads = []


        def retry_pins():
            while skipped_pins:
                with skipped_lock:
                    if not skipped_pins:
                        break
                    pin = skipped_pins.pop(0)
                brute_force(pin, total_attempts=len(skipped_pins) + progress)


        for _ in range(5):  # Always retry with 5 threads
            t = threading.Thread(target=retry_pins)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print("\nRetry of skipped PINs complete.")
else:
    print("\nSkipped retry as not all combinations were exhausted.")