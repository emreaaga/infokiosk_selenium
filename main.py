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
from utils import print_receipt


class VirtualKeyboard(tk.Tk):
    def __init__(self, send_key_callback):
        super().__init__()
        self.title("Virtual Keyboard")
        self.geometry("800x300")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.place_at_bottom()
        self.send_key_callback = send_key_callback
        self.setup_style()
        self.create_keyboard()

    def setup_style(self):
        """Sets up ttk styles for the keyboard."""
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Keyboard.TButton",
            font=("Helvetica", 14),
            padding=10,
            relief="flat",
            background="#F5F5F5",
            foreground="#000",
            borderwidth=0
        )

        style.configure(
            "Special.TButton",
            font=("Helvetica", 14, "bold"),
            padding=10,
            background="#FFDDC1",
            foreground="#000",
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Space.TButton",
            font=("Helvetica", 14),
            padding=10,
            background="#E0E0E0",
            foreground="#000",
            borderwidth=0,
            relief="flat"
        )

    def place_at_bottom(self):
        """Places the keyboard window at the bottom of the screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 950
        window_height = 300

        x = (screen_width - window_width) // 2
        y = screen_height - window_height
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    
    def create_keyboard(self):
        """Creates the virtual keyboard using ttk.Button."""
        keys = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"]
        ]
        extra_keys = [
            ["Space"]
        ]

        keyboard_frame = ttk.Frame(self)
        keyboard_frame.pack(expand=True, padx=10, pady=10)

        # Создаем ряды клавиш
        for row_idx, row in enumerate(keys):
            row_frame = ttk.Frame(keyboard_frame)
            row_frame.pack(side="top", pady=5)
            for key in row:
                button_style = (
                    "Special.TButton" if key in {"Backspace", "Shift"} else
                    "Space.TButton" if key == "Space" else
                    "Keyboard.TButton"
                )
                button_width = 12 if key == "Space" else 5
                button = ttk.Button(
                    row_frame,
                    text=key,
                    style=button_style,
                    width=button_width,
                    command=lambda k=key: self.key_pressed(k),
                )
                button.pack(side="left", padx=5)

        extra_frame = ttk.Frame(keyboard_frame)
        extra_frame.pack(side="top", pady=5)
        for key in extra_keys[0]:
            button_style = "Space.TButton" if key == "Space" else "Keyboard.TButton"
            button = ttk.Button(
                extra_frame,
                text=key,
                style=button_style,
                width=6 if key == "Space" else 3,
                command=lambda k=key: self.key_pressed(k),
            )
            button.pack(side="left", padx=5)

    def key_pressed(self, key):
        """Handles key press events."""
        if self.send_key_callback:
            self.send_key_callback(key)

    def open(self):
        """Opens the virtual keyboard window."""
        self.deiconify()

    def close(self):
        """Closes the virtual keyboard window."""
        self.withdraw()

# Virtual Keyboard Management Functions
_keyboard_instance = None

def position_keyboard_above_button(driver):
        """Позиционирует клавиатуру выше кнопки 'Оплата'."""
        try:
            # Найти кнопку "Оплата"
            button = driver.find_element(By.CLASS_NAME, "next_blue_btn")

            # Получить координаты кнопки
            button_location = button.location  # {'x': ..., 'y': ...}
            button_y = button_location['y']  # Верхняя граница кнопки

            # Параметры окна
            screen_width = driver.execute_script("return window.innerWidth;")  # Ширина экрана
            keyboard_width = 950
            keyboard_height = 300

            # Расчёт положения клавиатуры
            x = (screen_width - keyboard_width) // 2  # Центрируем по горизонтали
            y = max(0, button_y - keyboard_height - 20)  # Устанавливаем чуть выше кнопки

            # Устанавливаем новое положение клавиатуры
            _keyboard_instance.geometry(f"{keyboard_width}x{keyboard_height}+{x}+{y}")
            print(f"Клавиатура перемещена выше кнопки: x={x}, y={y}")
        except NoSuchElementException:
            print("Кнопка 'Оплата' не найдена. Клавиатура остаётся в стандартном положении.")
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

    # driver = webdriver.Chrome(options=chrome_options)
    driver_path = "C:\\info_kiosk\\chromedriver.exe"  # Замени на реальный путь
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        redirect_urls = [
            "https://avtoticket.uz/faq",
            "https://avtoticket.uz/web-difficult-to-reservation",
            "https://avtoticket.uz/about-us",
            "https://avtoticket.uz/ticket-recovery",
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
                pass  # No key press in the last 0.1 seconds
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