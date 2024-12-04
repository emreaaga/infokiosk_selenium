import time
import queue
import datetime
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import process_and_print_ticket
# from selenium.webdriver.chrome.service import Service
import queue


def selenium_thread_function(command_queue, keypress_queue):
    chrome_options = Options()
    chrome_options.add_argument("--kiosk")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--force-device-scale-factor=0.8")
    chrome_options.add_argument("--high-dpi-support=1")
    
    driver = webdriver.Chrome(options=chrome_options)
    # driver_path = "C:\\info_kiosk\\chromedriver.exe"
    # service = Service(driver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        redirect_urls = [
            "https://avtoticket.uz/faq",
            "https://avtoticket.uz/web-difficult-to-reservation",
            "https://avtoticket.uz/about-us",
        ]
        driver.get("https://avtoticket.uz")
        

        current_fields_state = False
        last_url = None 
        last_check_time = time.time()
        page_check_interval = 2

        while True:
            try:
                key = keypress_queue.get(timeout=0.1)
                active_element = driver.switch_to.active_element
                if key == 'Backspace':
                    active_element.send_keys(Keys.BACKSPACE)
                elif key == "Tab":
                    try:
                        next_element = driver.find_element(By.CSS_SELECTOR, "input:focus")
                        next_element.send_keys(Keys.TAB)
                    except NoSuchElementException:
                        print("No next input element available.")
                else:
                    active_element.send_keys(key)
            except queue.Empty:
                pass
            except WebDriverException as e:
                print(f"Error sending key: {e}")

            # Check the page state every 2 seconds
            if time.time() - last_check_time >= page_check_interval:
                last_check_time = time.time()
                
                current_url = driver.current_url
                if current_url != last_url:
                    last_url = current_url

                if any(current_url.startswith(url.strip("/")) for url in redirect_urls):
                    driver.get("https://avtoticket.uz")
                    continue

                if "/tickets/" in current_url:
                    try:
                        driver.find_element(By.ID, "nd-name0")
                        driver.find_element(By.ID, "nd-tel0")
                        driver.find_element(By.ID, "nd-email0")

                        modal_visible = False
                        try:
                            modal = driver.find_element(By.CLASS_NAME, "swal2-header")
                            if modal.is_displayed():
                                modal_visible = True
                        except NoSuchElementException:
                            modal_visible = False
                        
                        if modal_visible:
                            if current_fields_state:
                                command_queue.put(('close_keyboard',))
                                current_fields_state = False
                                        
                        else:
                            if not current_fields_state:
                                command_queue.put(('open_keyboard',))
                                command_queue.put(('switch_to_keyboard',))
                                current_fields_state = True
                                geometry = position_keyboard_above_button(driver)
                                if geometry:
                                    command_queue.put(('move_keyboard', geometry))

                    except NoSuchElementException:
                        print("Input fields not found.")
                        if current_fields_state:
                            command_queue.put(('close_keyboard',))
                            current_fields_state = False
                
                elif "/payment-payme/" in current_url:
                    try:
                        field_found = False
                        try:
                            driver.find_element(By.ID, "nd-name")
                            field_found = True
                            print("Found field: Card Number")
                        except NoSuchElementException:
                            pass

                        try:
                            driver.find_element(By.ID, "nd-tel")
                            field_found = True
                            print("Found field: Card Expiry Date")
                        except NoSuchElementException:
                            pass

                        try:
                            driver.find_element(By.ID, "brr")
                            field_found = True
                            print("Found field: SMS Code")
                        except NoSuchElementException:
                            pass

                        modal_visible = False
                        try:
                            modal = driver.find_element(By.CLASS_NAME, "swal2-header")
                            if modal.is_displayed():
                                modal_visible = True
                        except NoSuchElementException:
                            modal_visible = False
                        
                        if modal_visible:
                            if current_fields_state:
                                command_queue.put(('close_keyboard',))
                                current_fields_state = False
                                        
                        else:
                            if not current_fields_state:
                                command_queue.put(('open_keyboard',))
                                command_queue.put(('switch_to_numpad',))
                                current_fields_state = True
                                geometry = position_keyboard_above_button(driver)
                                if geometry:
                                    command_queue.put(('move_keyboard', geometry))

                    except Exception as e:
                        print(f"Error on /payment-payme/ page: {e}")
                        if current_fields_state:
                            command_queue.put(('close_keyboard',))
                            command_queue.put(('switch_to_keyboard',))
                            current_fields_state = False
                            
                elif "/bought-tickets/" in current_url:
                    try:
                        ticket_elements = driver.find_elements(By.CSS_SELECTOR, "div.tickets_all_child")

                        if ticket_elements:
                            print(f"Found {len(ticket_elements)} tickets.")
                        
                            for ticket_element in ticket_elements:
                                download_button = ticket_element.find_element(By.CLASS_NAME, "green_download_btn")
                                download_url = download_button.get_attribute("href")

                                process_and_print_ticket(download_url)

                            driver.get("https://avtoticket.uz")

                        else:
                            print("No tickets found.")

                    except Exception as e:
                        print(f"Error processing purchased tickets page: {e}")

                elif "/ticket-recovery" in current_url:
                    print("On the ticket recovery page.")
                    try:
                        WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.ID, "brr"))
                        )
                        print("Phone number input field found.")
                        
                        if not current_fields_state:
                            command_queue.put(('open_keyboard',))
                            command_queue.put(('move_to_bottom_center',))
                            command_queue.put(('switch_to_numpad',))
                            current_fields_state = True
                            
                    except TimeoutException:
                        if current_fields_state:
                            command_queue.put(('close_keyboard',))
                            current_fields_state = False
                        
                        ticket_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "tickets_all_child"))
                        )
                        if not ticket_elements:
                            print("No tickets found.")
                        else:
                            print(f"Found {len(ticket_elements)} tickets.")
                        
                        # Current date
                        current_time = datetime.datetime.now()
                        print(current_time)

                        # Process tickets
                        for ticket_element in ticket_elements:
                            try:
                                # Find travel date
                                travel_date_text = ticket_element.find_element(
                                    By.XPATH, ".//p[contains(text(), 'Дата поездки:')]/following-sibling::h5"
                                ).text
                                travel_date = datetime.datetime.strptime(travel_date_text, "%Y-%m-%d %H:%M")

                                # Check ticket validity
                                if travel_date >= current_time:
                                    print(f"Valid ticket: {travel_date}")
                                    # Download and print
                                    download_button = ticket_element.find_element(By.CLASS_NAME, "green_download_btn")
                                    download_url = download_button.get_attribute("href")
                                    process_and_print_ticket(download_url)
                                else:
                                    print(f"Ticket expired: {travel_date}")
                            except Exception as e:
                                print(f"Error processing ticket: {e}")
                        
                        print('Redirecting!')
                        driver.get('https://avtoticket.uz/')
                    
                    except Exception as e:
                        print(f"Error on ticket recovery page: {e}")
                        if current_fields_state:
                            command_queue.put(('close_keyboard',))
                            current_fields_state = False
                        driver.get("https://avtoticket.uz")
                
                else:
                    if current_fields_state:
                        print("Closing keyboard as the page does not require input.")
                        command_queue.put(('close_keyboard',))
                        current_fields_state = False

    except KeyboardInterrupt:
        print("Script stopped by user.")

    finally:
        if current_fields_state:
            command_queue.put(('close_keyboard',))
        driver.quit()


def position_keyboard_above_button(driver):
    """Вычисляет геометрию для позиционирования клавиатуры относительно кнопки 'Оплата'."""
    try:
        input_div = driver.find_element(By.CLASS_NAME, "nd_checkout")
        button_div = driver.find_element(By.CLASS_NAME, "next_blue_btn")
        input_rect = driver.execute_script("""
            const rect = arguments[0].getBoundingClientRect();
            return {top: rect.top, left: rect.left, width: rect.width, height: rect.height};
        """, input_div)
        button_rect = driver.execute_script("""
            const rect = arguments[0].getBoundingClientRect();
            return {top: rect.top, left: rect.left, width: rect.width, height: rect.height};
        """, button_div)
        scale_factor = driver.execute_script("return window.devicePixelRatio;")
        keyboard_width = input_rect['width'] * scale_factor
        available_space = (button_rect['top'] - (input_rect['top'] + input_rect['height'])) * scale_factor
        keyboard_height = min(300, max(50, available_space - 10))
        x = input_rect['left'] * scale_factor
        y = (input_rect['top'] + input_rect['height'] + 5) * scale_factor
        if available_space <= 0:
            print("Not enough space to display the keyboard between inputs and the 'Payment' button.")
            return None
        window_width = driver.execute_script("return window.innerWidth;") * scale_factor
        window_height = driver.execute_script("return window.innerHeight;") * scale_factor
        x = max(0, min(x, window_width - keyboard_width))
        y = max(0, min(y, window_height - keyboard_height))
        geometry = f"{int(keyboard_width)}x{int(keyboard_height)}+{int(x)}+{int(y)}"
        print(f"Calculated keyboard geometry: {geometry}")
        return geometry
    except NoSuchElementException:
        print("Input div or 'Payment' button not found.")
        return None
    except Exception as e:
        print(f"Error positioning keyboard: {e}")
        return None