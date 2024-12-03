import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from utils import process_and_print_ticket
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import datetime


class VirtualKeyboard(tk.Tk):
    def __init__(self, send_key_callback):
        super().__init__()
        self.title("Virtual Keyboard")
        self.geometry("800x300")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.send_key_callback = send_key_callback
        self.caps_lock_on = False
        self.setup_style()
        self.create_keyboard()

    def setup_style(self):
        """Sets up ttk styles for the keyboard."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Keyboard.TButton",
            font=("Helvetica", 12),
            padding=10,
            relief="flat",
            background="#F5F5F5",
            foreground="#000",
            borderwidth=0
        )

        style.configure(
            "Special.TButton",
            font=("Helvetica", 12),
            padding=10,
            background="#0799e0",
            foreground="#000",
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Space.TButton",
            font=("Helvetica", 12),
            padding=10,
            background="#E0E0E0",
            foreground="#000",
            borderwidth=0,
            relief="flat"
        )
    
    def create_keyboard(self):
        """Creates the virtual keyboard using ttk.Button."""
        keys = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m", ".", ",", "@"],
        ]
        extra_keys = [
            ["Смена регистра", "Пробел", "Удалить"]
        ]


        keyboard_frame = ttk.Frame(self)
        keyboard_frame.pack(expand=True, padx=5, pady=5)

        # Создаем ряды клавиш
        for row_idx, row in enumerate(keys):
            row_frame = ttk.Frame(keyboard_frame)
            row_frame.pack(side="top", pady=2)
            for key in row:
                button = ttk.Button(
                    row_frame,
                    text=key,
                    style='Keyboard.TButton',
                    width=5,
                    command=lambda k=key: self.key_pressed(k),
                )
                button.pack(side="left", padx=2)

        # Добавляем дополнительные клавиши (Caps Lock и Пробел, Удалить)
        extra_frame = ttk.Frame(keyboard_frame)
        extra_frame.pack(side="top", pady=2)
        for key in extra_keys[0]:
            button_style = "Space.TButton" if key == "Пробел" else "Special.TButton"
            button_width = 35 if key == "Пробел" else 14
            button = ttk.Button(
                extra_frame,
                text=key,
                style=button_style,
                width=button_width,
                command=lambda k=key: self.key_pressed(k),
            )
            button.pack(side="left", padx=3)

    def key_pressed(self, key):
        """Handles key press events."""
        if key == "Смена регистра":
            self.toggle_caps_lock()
        elif key == "Удалить":
            if self.send_key_callback:
                self.send_key_callback("Backspace")
        elif key == "Пробел":
            if self.send_key_callback:
                self.send_key_callback(" ")
        elif self.send_key_callback:
            if self.caps_lock_on and key.isalpha():
                key = key.upper()
            self.send_key_callback(key)
            
    def toggle_caps_lock(self):
        """Toggles Caps Lock state."""
        self.caps_lock_on = not self.caps_lock_on       

    def open(self):
        """Opens the virtual keyboard window."""
        self.deiconify()

    def close(self):
        """Closes the virtual keyboard window."""
        self.withdraw()

# Virtual Keyboard Management Functions
_keyboard_instance = None

def position_keyboard_above_button(driver):
        """Позиционирует клавиатуру относительно кнопки 'Оплата' с использованием процентов."""
        try:
            # Найти div с инпутами
            input_div = driver.find_element(By.CLASS_NAME, "nd_checkout")

            # Найти div с кнопкой
            button_div = driver.find_element(By.CLASS_NAME, "next_blue_btn")

            # Получить размеры и координаты div с инпутами
            input_rect = driver.execute_script("""
                const rect = arguments[0].getBoundingClientRect();
                return {top: rect.top, left: rect.left, width: rect.width, height: rect.height};
            """, input_div)

            # Получить размеры и координаты div с кнопкой
            button_rect = driver.execute_script("""
                const rect = arguments[0].getBoundingClientRect();
                return {top: rect.top, left: rect.left, width: rect.width, height: rect.height};
            """, button_div)

            # Получить текущий масштаб страницы
            scale_factor = driver.execute_script("return window.devicePixelRatio;")

            # Параметры клавиатуры
            keyboard_width = input_rect['width'] * scale_factor  # Ширина совпадает с шириной div с инпутами
            available_space = (button_rect['top'] - (input_rect['top'] + input_rect['height'])) * scale_factor  # Свободное пространство
            keyboard_height = min(300, max(50, available_space - 10))  # Высота клавиатуры с учетом ограничений

            # Позиционировать клавиатуру
            x = input_rect['left'] * scale_factor  # Учитываем масштаб для позиции x
            y = (input_rect['top'] + input_rect['height'] + 5) * scale_factor  # Позиция y с отступом

            # Проверить, хватает ли места
            if available_space <= 0:
                print("Недостаточно места для отображения клавиатуры между div с инпутами и кнопкой.")
                return

            # Убедиться, что клавиатура не выходит за пределы экрана
            window_width = driver.execute_script("return window.innerWidth;") * scale_factor
            window_height = driver.execute_script("return window.innerHeight;") * scale_factor
            x = max(0, min(x, window_width - keyboard_width))
            y = max(0, min(y, window_height - keyboard_height))

            # Установить размер и положение клавиатуры
            _keyboard_instance.geometry(f"{int(keyboard_width)}x{int(keyboard_height)}+{int(x)}+{int(y)}")
            print(f"Клавиатура перемещена: ширина={keyboard_width}, высота={keyboard_height}, x={x}, y={y}")
        except NoSuchElementException:
            print("Не найден div с инпутами или кнопкой 'Оплата'.")
        except Exception as e:
            print(f"Ошибка при размещении клавиатуры: {e}")


def start_keyboard(send_key_callback):
    """Starts the virtual keyboard."""
    global _keyboard_instance
    if _keyboard_instance is None:
        _keyboard_instance = VirtualKeyboard(send_key_callback)
        _keyboard_instance.protocol("WM_DELETE_WINDOW", _keyboard_instance.close)

def open_keyboard():
    """Opens the virtual keyboard."""
    if _keyboard_instance:
        _keyboard_instance.open()
        print("Keyboard opened.")
    else:
        print("Keyboard instance not found.")

def close_keyboard():
    """Closes the virtual keyboard."""
    if _keyboard_instance:
        _keyboard_instance.close()
        print("Keyboard closed.")
    else:
        print("Keyboard instance not found.")

def stop_keyboard():
    """Stops the virtual keyboard."""
    global _keyboard_instance
    if _keyboard_instance:
        _keyboard_instance.destroy()
        _keyboard_instance = None
        print("Keyboard stopped.")
    else:
        print("Keyboard instance not found.")

_keyboard_started = False

def manage_virtual_keyboard(open_kb, send_key_callback=None):
    """Manages the virtual keyboard."""
    global _keyboard_started
    if open_kb:
        print("Opening virtual keyboard")
        if not _keyboard_started:
            if send_key_callback is None:
                print("Error: send_key_callback is required to start the keyboard.")
                return
            start_keyboard(send_key_callback)
            _keyboard_started = True
        open_keyboard()
    else:
        print("Closing virtual keyboard")
        if _keyboard_started:
            close_keyboard()

keypress_queue = queue.Queue()

def send_key_callback(key):
    keypress_queue.put(key)

def selenium_thread_function():
    chrome_options = Options()
    chrome_options.add_argument("--kiosk")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-infobars")
    
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
                elif key == 'Space':
                    active_element.send_keys(' ')
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
                        name_input = driver.find_element(By.ID, "nd-name0")
                        tel_input = driver.find_element(By.ID, "nd-tel0")
                        email_input = driver.find_element(By.ID, "nd-email0")
                        print("Found fields for name, phone, and email")

                        if not current_fields_state:
                            manage_virtual_keyboard(True, send_key_callback)
                            current_fields_state = True
                            position_keyboard_above_button(driver)

                    except NoSuchElementException:
                        print("Input fields not found.")
                        if current_fields_state:
                            manage_virtual_keyboard(False)
                            current_fields_state = False

                elif "/payment-payme/" in current_url:
                    try:
                        field_found = False
                        try:
                            card_number_input = driver.find_element(By.ID, "nd-name")
                            field_found = True
                            print("Found field: Card Number")
                        except NoSuchElementException:
                            pass

                        try:
                            ex_date_input = driver.find_element(By.ID, "nd-tel")
                            field_found = True
                            print("Found field: Card Expiry Date")
                        except NoSuchElementException:
                            pass

                        try:
                            code_input = driver.find_element(By.ID, "brr")
                            field_found = True
                            print("Found field: SMS Code")
                        except NoSuchElementException:
                            pass

                        if field_found and not current_fields_state:
                            manage_virtual_keyboard(True, send_key_callback)
                            current_fields_state = True
                        elif not field_found and current_fields_state:
                            manage_virtual_keyboard(False)
                            current_fields_state = False

                    except Exception as e:
                        print(f"Error on /payment-payme/ page: {e}")
                        if current_fields_state:
                            manage_virtual_keyboard(False)
                            current_fields_state = False
                            
                elif "/bought-tickets/" in current_url:
                    try:
                        ticket_elements = driver.find_elements(By.CSS_SELECTOR, "div.tickets_all_child")

                        if ticket_elements:
                            print(f"Найдено {len(ticket_elements)} билетов.")
                        
                            for i, ticket_element in enumerate(ticket_elements, start=1):
                                download_button = ticket_element.find_element(By.CLASS_NAME, "green_download_btn")
                                download_url = download_button.get_attribute("href")

                                process_and_print_ticket(download_url)

                            driver.get("https://avtoticket.uz")

                        else:
                            print("Билеты не найдены.")

                    except Exception as e:
                        print(f"Ошибка при обработке страницы с купленными билетами: {e}")

                elif "/ticket-recovery" in current_url:
                    print("Находимся на странице восстановления билета.")
                    try:
                        phone_input = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.ID, "brr"))
                        )
                        print("Найдено поле ввода номера телефона.")
                        
                        if not current_fields_state:
                            manage_virtual_keyboard(True, send_key_callback)
                            current_fields_state = True
                            
                    except TimeoutException:
                        if current_fields_state:
                            manage_virtual_keyboard(False)
                            current_fields_state = False
                        
                        ticket_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "tickets_all_child"))
                        )
                        if not ticket_elements:
                            print("Билеты не найдены.")
                        else:
                            print(f"Найдено {len(ticket_elements)} билетов.")
                        
                        # Текущая дата
                        current_time = datetime.datetime.now()

                        # Обрабатываем билеты
                        for ticket_element in ticket_elements:
                            try:
                                # Находим дату поездки
                                travel_date_text = ticket_element.find_element(
                                    By.XPATH, ".//p[contains(text(), 'Дата поездки:')]/following-sibling::h5"
                                ).text
                                travel_date = datetime.datetime.strptime(travel_date_text, "%Y-%m-%d %H:%M")

                                # Проверяем актуальность билета
                                if travel_date >= current_time:
                                    print(f"Билет актуален: {travel_date}")
                                    # Скачиваем и печатаем
                                    download_button = ticket_element.find_element(By.CLASS_NAME, "green_download_btn")
                                    download_url = download_button.get_attribute("href")
                                    process_and_print_ticket(download_url)
                                else:
                                    print(f"Билет не актуален: {travel_date}")
                            except Exception as e:
                                print(f"Ошибка при обработке билета: {e}")
                        
                        print('Перенапрвление!')
                        driver.get('https://avtoticket.uz/')
                    
                    except Exception as e:
                        print(f"Ошибка на странице восстановления билета: {e}")
                        if current_fields_state:
                            manage_virtual_keyboard(False)
                            current_fields_state = False
                        driver.get("https://avtoticket.uz")
                
                else:
                    if current_fields_state:
                        print("Closing keyboard as the page does not require input.")
                        manage_virtual_keyboard(False)
                        current_fields_state = False

    except KeyboardInterrupt:
        print("Script stopped by user.")

    finally:
        if current_fields_state:
            manage_virtual_keyboard(False)
        driver.quit()

start_keyboard(send_key_callback)
selenium_thread = threading.Thread(target=selenium_thread_function, daemon=True)
selenium_thread.start()
tk.mainloop()
