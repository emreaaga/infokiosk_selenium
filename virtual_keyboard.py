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
        self.arrow_window = None  # Инициализируем переменную для окна стрелок
        self.check_queue()  # Начинаем проверку очереди команд

    def create_numpad(self):
        """Создает нумпад с цифрами и кнопками подтверждения."""
        if hasattr(self, 'numpad_frame'):
            self.numpad_frame.destroy()  # Удаляем старый нумпад, если он есть

        self.numpad_frame = ttk.Frame(self)
        self.numpad_frame.pack(expand=True, fill="both", padx=5, pady=5)

        keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["0", "Удалить", "Ввод"]
        ]
        
        button_width = 10
        button_height = 5

        for row in keys:
            row_frame = ttk.Frame(self.numpad_frame)
            row_frame.pack(side="top", expand=True, fill="both", pady=2)
            for key in row:
                button_style = "Space.TButton" if key in ["Удалить", "Ввод"] else "Keyboard.TButton"
                button = ttk.Button(
                    row_frame,
                    text=key,
                    style=button_style,
                    command=lambda k=key: self.numpad_key_pressed(k),
                )
                # Растягиваем кнопки
                button.pack(side="left", expand=True, fill="both", padx=3)

    def numpad_key_pressed(self, key):
        """Обрабатывает нажатия на нумпад."""
        if key == "Удалить":
            self.send_key("Backspace")
        elif key == "Ввод":
            self.send_key("Tab")
        else:
            self.send_key(key)

    def switch_to_numpad(self):
        """Переключает клавиатуру на нумпад."""
        self.keyboard_frame.pack_forget()  # Скрываем основную клавиатуру
        self.create_numpad()  # Показываем нумпад

    def switch_to_keyboard(self):
        """Переключает нумпад на основную клавиатуру."""
        if hasattr(self, 'numpad_frame'):
            self.numpad_frame.destroy()  # Удаляем нумпад
        self.keyboard_frame.pack(expand=True, fill="both")  # Показываем основную клавиатуру

    def setup_style(self):
        """Настраивает стили ttk для клавиатуры."""
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Keyboard.TButton",
            font=("Helvetica", 16),
            padding=10,
            relief="flat",
            background="#F5F5F5",
            foreground="#000",
            borderwidth=0
        )
        style.configure(
            "Special.TButton",
            font=("Helvetica", 16),
            padding=10,
            background="#0799e0",
            foreground="#000",
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Space.TButton",
            font=("Helvetica", 16),
            padding=10,
            background="#E0E0E0",
            foreground="#000",
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Arrow.TButton",
            font=("Helvetica", 16),
            padding=10,
            background="#D3D3D3",
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
        self.keyboard_frame.pack(expand=True, fill="both", padx=5, pady=5)
        # Создаем ряды клавиш
        for row in keys:
            row_frame = ttk.Frame(self.keyboard_frame)
            row_frame.pack(side="top", fill="x", pady=2)
            for key in row:
                button = ttk.Button(
                    row_frame,
                    text=key,
                    style='Keyboard.TButton',
                    width=4,
                    command=lambda k=key: self.key_pressed(k),
                )
                button.pack(side="left", expand=True, fill="both", padx=2)
        # Добавляем дополнительные клавиши
        extra_frame = ttk.Frame(self.keyboard_frame)
        extra_frame.pack(side="top", fill="x", pady=2)
        for key in extra_keys[0]:
            button_style = "Space.TButton" if key == "Пробел" else "Special.TButton"
            button_width = 10 if key == "Пробел" else 7
            button = ttk.Button(
                extra_frame,
                text=key,
                style=button_style,
                width=button_width,
                command=lambda k=key: self.key_pressed(k),
            )
            button.pack(side="left", expand=True, fill="both", padx=3)
        # Добавляем кнопку для открытия окна стрелок
        arrows_button = ttk.Button(
            extra_frame,
            text="Стрелки",
            style="Special.TButton",
            width=7,
            command=self.open_arrow_window
        )
        arrows_button.pack(side="left", expand=True, fill="both", padx=3)

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
        # Обновляем текст кнопки "Смена регистра" в зависимости от состояния Caps Lock
        for child in self.keyboard_frame.winfo_children():
            for button in child.winfo_children():
                if button['text'] == "Смена регистра" or button['text'] == "Caps ON":
                    if self.caps_lock_on:
                        button.config(text="Caps ON")
                    else:
                        button.config(text="Смена регистра")
    
    def open_arrow_window(self):
        """Создает и открывает отдельное окно с стрелками вверх и вниз."""
        if self.arrow_window and tk.Toplevel.winfo_exists(self.arrow_window):
        # Если окно уже открыто, просто фокусируемся на нем
            self.arrow_window.focus()
            return

        self.arrow_window = tk.Toplevel(self)
        self.arrow_window.title("Стрелки")
        self.arrow_window.resizable(False, False)
        self.arrow_window.attributes("-topmost", True)
        self.arrow_window.overrideredirect(True)  # Убираем окно из панели задач

        # Позиционируем окно стрелок по правому краю экрана, по центру
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 100
        window_height = 150
        x = screen_width - window_width  # Прикрепляем к правому краю
        y = (screen_height - window_height) // 2
        geometry = f"{window_width}x{window_height}+{x}+{y}"
        self.arrow_window.geometry(geometry)

        # Создаем кнопки стрелок
        up_button = ttk.Button(
            self.arrow_window,
            text="↑",
            style="Arrow.TButton",
            command=lambda: self.send_key("Up"),
            width=5
        )
        up_button.pack(side="top", expand=True, fill="both", pady=(20,5), padx=10)

        down_button = ttk.Button(
            self.arrow_window,
            text="↓",
            style="Arrow.TButton",
            command=lambda: self.send_key("Down"),
            width=5
        )
        down_button.pack(side="top", expand=True, fill="both", pady=5, padx=10)

    def close_arrow_window(self):
        """Закрывает окно стрелок, если оно открыто."""
        if self.arrow_window and tk.Toplevel.winfo_exists(self.arrow_window):
            self.arrow_window.destroy()
            self.arrow_window = None  # Сбрасываем переменную

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
    
    def move_to_bottom_center(self):
        """Перемещает клавиатуру вниз по центру экрана."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        keyboard_width = 800  # Ширина клавиатуры
        keyboard_height = 300  # Высота клавиатуры

        x = (screen_width - keyboard_width) // 2
        y = screen_height - keyboard_height - 10  # Отступ от нижнего края
        self.geometry(f"{keyboard_width}x{keyboard_height}+{x}+{y}")
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
                elif command[0] == 'move_to_bottom_center':
                    self.move_to_bottom_center()
                elif command[0] == 'switch_to_numpad':
                    self.switch_to_numpad()
                elif command[0] == 'switch_to_keyboard':
                    self.switch_to_keyboard()
                elif command[0] == 'open_arrow_window':
                    self.open_arrow_window()
                elif command[0] == 'close_arrow_window':
                    self.close_arrow_window()
                
        except queue.Empty:
            pass
        # Планируем следующую проверку очереди
        self.after(50, self.check_queue)
