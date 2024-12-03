from tkinter import *
from customtkinter import *
import sys


class PopupKeyboard(CTkToplevel):
    def __init__(self, attach, x=None, y=None, key_color=None,
                 text_color=None, hover_color=None, fg_color=None,
                 keywidth: int = 5, keyheight: int = 2, command=None,
                 alpha: float = 0.85, corner=20, **kwargs):

        super().__init__(takefocus=0)
        self.attach = attach  # Ожидаем объект queue.Queue
        self.corner = corner
        self.disable = True

        if sys.platform.startswith("win"):
            self.overrideredirect(True)
            self.transparent_color = self._apply_appearance_mode(self._fg_color)
            self.attributes("-transparentcolor", self.transparent_color)
        elif sys.platform.startswith("darwin"):
            self.overrideredirect(True)
            self.transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
            if not text_color:
                text_color = "black"
        else:
            self.attributes("-type", "splash")
            self.transparent_color = '#000001'
            self.corner = 0
            self.withdraw()

        self.disable = False
        self.fg_color = ThemeManager.theme["CTkFrame"]["fg_color"] if fg_color is None else fg_color
        self.frame = CTkFrame(self, bg_color=self.transparent_color, fg_color=self.fg_color, corner_radius=self.corner, border_width=2)
        self.frame.pack(expand=True, fill="both")

        self.keywidth = keywidth
        self.keyheight = keyheight
        self.keycolor = self._apply_appearance_mode(ThemeManager.theme["CTkFrame"]["top_fg_color"]) if key_color is None else key_color
        self.textcolor = self._apply_appearance_mode(ThemeManager.theme["CTkLabel"]["text_color"]) if text_color is None else text_color
        self.hovercolor = self._apply_appearance_mode(ThemeManager.theme["CTkButton"]["hover_color"]) if hover_color is None else hover_color
        self.command = command
        self.resizable(width=False, height=False)

        self.row1 = CTkFrame(self.frame)
        self.row2 = CTkFrame(self.frame)
        self.row3 = CTkFrame(self.frame)
        self.row4 = CTkFrame(self.frame)
        self.row5 = CTkFrame(self.frame)

        self.row1.grid(row=1, column=0, pady=(5, 0))
        self.row2.grid(row=2, column=0, padx=5)
        self.row3.grid(row=3, column=0, padx=5)
        self.row4.grid(row=4, column=0)
        self.row5.grid(row=5, column=0, pady=(0, 5))

        self._init_keys(**kwargs)
        self.update_idletasks()
        self.x = x
        self.y = y
        self._iconify()
        self.attributes('-alpha', alpha)

    def _init_keys(self, **kwargs):
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '◀'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '?'],
            [' space ']
        ]

        for row_index, row in enumerate(self.keys):
            frame = getattr(self, f"row{row_index + 1}")
            for col_index, key in enumerate(row):
                Button(
                    frame,
                    text=key,
                    width=self.keywidth * (3 if key == ' space ' else 1),
                    height=self.keyheight,
                    bg=self.keycolor,
                    fg=self.textcolor,
                    highlightthickness=0,
                    borderwidth=1,
                    activebackground=self.hovercolor,
                    command=lambda k=key: self._attach_key_press(k),
                    **kwargs
                ).grid(row=0, column=col_index, padx=2, pady=2)

    def _iconify(self):
        """Показывает или скрывает клавиатуру."""
        if self.disable:
            return
        if self.attach:
            self.deiconify()
            self.focus()
            self.geometry(f"{self.frame.winfo_reqwidth()}x{self.frame.winfo_reqheight()}+{self.x}+{self.y}")

    def _attach_key_press(self, k):
        """Отправляет символ в очередь."""
        if k == ' space ':
            self.attach.put(' ')
        elif k == '◀':
            self.attach.put('Backspace')
        else:
            self.attach.put(k)

    def destroy_popup(self):
        self.destroy()
        self.disable = True
