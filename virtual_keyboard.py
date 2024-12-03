import tkinter as tk
from tkinter import ttk

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

def get_keyboard_instance():
    """Returns the current keyboard instance."""
    return _keyboard_instance