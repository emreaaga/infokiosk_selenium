import tkinter as tk
from tkinter import ttk
import queue

class VirtualKeyboard(tk.Tk):
    def __init__(self, command_queue, keypress_queue):
        super().__init__()
        self.title("Virtual Keyboard")
        self.geometry("800x300")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.keypress_queue = keypress_queue
        self.caps_lock_on = False
        self.setup_style()
        self.create_keyboard()
        self.command_queue = command_queue
        self.check_queue()  # Начинаем проверку очереди команд

    def setup_style(self):
        """Настраивает стили ttk для клавиатуры."""
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
        """Создает виртуальную клавиатуру с использованием ttk.Button."""
        keys = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m", ".", ",", "@"],
        ]
        extra_keys = [
            ["Смена регистра", "Пробел", "Удалить"]
        ]
        self.keyboard_frame = ttk.Frame(self)
        self.keyboard_frame.pack(expand=True, padx=5, pady=5)
        # Создаем ряды клавиш
        for row in keys:
            row_frame = ttk.Frame(self.keyboard_frame)
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
        # Добавляем дополнительные клавиши
        extra_frame = ttk.Frame(self.keyboard_frame)
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
        """Обрабатывает события нажатия клавиш."""
        if key == "Смена регистра":
            self.toggle_caps_lock()
        elif key == "Удалить":
            self.send_key("Backspace")
        elif key == "Пробел":
            self.send_key(" ")
        else:
            if self.caps_lock_on and key.isalpha():
                key = key.upper()
            self.send_key(key)
                
    def send_key(self, key):
        """Отправляет нажатую клавишу в очередь."""
        self.keypress_queue.put(key)

    def toggle_caps_lock(self):
        """Переключает состояние Caps Lock."""
        self.caps_lock_on = not self.caps_lock_on       

    def open_keyboard(self):
        """Открывает окно виртуальной клавиатуры."""
        self.deiconify()
        self.update()

    def close_keyboard(self):
        """Закрывает окно виртуальной клавиатуры."""
        self.withdraw()

    def move_keyboard(self, geometry):
        """Перемещает и изменяет размер окна клавиатуры."""
        self.geometry(geometry)
        self.update()

    def check_queue(self):
        """Проверяет очередь команд и выполняет их."""
        try:
            while True:
                command = self.command_queue.get_nowait()
                if command[0] == 'open_keyboard':
                    self.open_keyboard()
                elif command[0] == 'close_keyboard':
                    self.close_keyboard()
                elif command[0] == 'move_keyboard':
                    geometry = command[1]
                    self.move_keyboard(geometry)
        except queue.Empty:
            pass
        # Планируем следующую проверку очереди
        self.after(100, self.check_queue)
