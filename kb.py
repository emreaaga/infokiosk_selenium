import tkinter as tk
from selenium.webdriver.common.keys import Keys
import threading

class VirtualKeyboard(tk.Tk):
    def __init__(self, send_key_callback):
        """
        Инициализация виртуальной клавиатуры.
        :param send_key_callback: Функция для отправки нажатых клавиш.
        """
        super().__init__()
        self.title("Виртуальная клавиатура")
        self.geometry("800x300")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.place_at_bottom()
        self.send_key_callback = send_key_callback
        self.create_keyboard()

    def place_at_bottom(self):
        """Размещает окно в нижней части экрана."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 800
        window_height = 300

        x = (screen_width - window_width) // 2
        y = screen_height - window_height
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_keyboard(self):
        """Создает кнопки виртуальной клавиатуры."""
        keys = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M", "Space"]
        ]

        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                button = tk.Button(self, text=key, width=5, height=2, command=lambda k=key: self.key_pressed(k))
                button.grid(row=row_idx, column=col_idx, padx=5, pady=5)

    def key_pressed(self, key):
        """Обработка нажатия клавиши."""
        print(f"Нажата клавиша: {key}")
        if self.send_key_callback:
            self.send_key_callback(key)

    def open(self):
        """Открывает окно виртуальной клавиатуры."""
        self.deiconify()

    def close(self):
        """Закрывает окно виртуальной клавиатуры."""
        self.withdraw()


# Управляющие функции
_keyboard_instance = None

def start_keyboard(send_key_callback):
    """
    Запускает виртуальную клавиатуру.
    :param send_key_callback: Функция для отправки нажатых клавиш.
    """
    global _keyboard_instance
    if _keyboard_instance is None:
        _keyboard_instance = VirtualKeyboard(send_key_callback)
        _keyboard_instance.protocol("WM_DELETE_WINDOW", _keyboard_instance.close)


def open_keyboard():
    """Открывает виртуальную клавиатуру."""
    if _keyboard_instance:
        _keyboard_instance.open()
        print("Keyboard opened.")
    else:
        print("Keyboard instance not found.")

def close_keyboard():
    """Закрывает виртуальную клавиатуру."""
    if _keyboard_instance:
        _keyboard_instance.close()
        print("Keyboard closed.")
    else:
        print("Keyboard instance not found.")

def stop_keyboard():
    """Останавливает виртуальную клавиатуру и освобождает ресурсы."""
    global _keyboard_instance
    if _keyboard_instance:
        _keyboard_instance.destroy()
        _keyboard_instance = None
        print("Keyboard stopped.")
    else:
        print("Keyboard instance not found.")