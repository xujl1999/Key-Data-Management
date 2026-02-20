
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def login_and_save_cookies():
    print("Launching browser for WeRead login...")
    print("Please scan the QR code to log in.")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1200,800")
    
    # Initialize WebDriver (Assumes Chrome is installed)
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Error launching Chrome: {e}")
        print("Please ensure Google Chrome is installed.")
        return

    try:
        driver.get("https://weread.qq.com/")
        
        # Wait for login
        print("Waiting for login... (Timeout: 120 seconds)")
        logged_in = False
        for _ in range(60):  # Check every 2 seconds for 2 minutes
            time.sleep(2)
            cookies = driver.get_cookies()
            # Check for specific WeRead login cookies
            vid = next((c for c in cookies if c['name'] == 'wr_vid'), None)
            skey = next((c for c in cookies if c['name'] == 'wr_skey'), None)
            
            if vid and skey:
                logged_in = True
                print("Login detected!")
                break
        
        if not logged_in:
            print("Login timed out.")
            return

        # Format cookies for cookies.txt (name=value; name2=value2)
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        # Save to file
        save_path = os.path.join("weread", "cookies.txt")
        os.makedirs("weread", exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(cookie_str)
            
        print(f"\nSUCCESS! Cookies saved to: {save_path}")
        print("You can now refresh the dashboard.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    login_and_save_cookies()
