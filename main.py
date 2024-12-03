import threading
import tkinter as tk
from virtual_keyboard import VirtualKeyboard
from selenium_controller import selenium_thread_function
import queue

def main():
    # Создаем очереди для команд и нажатий клавиш
    command_queue = queue.Queue()
    keypress_queue = queue.Queue()

    # Создаем экземпляр виртуальной клавиатуры
    virtual_keyboard = VirtualKeyboard(command_queue, keypress_queue)
    
    # Запускаем поток Selenium
    selenium_thread = threading.Thread(
        target=selenium_thread_function,
        args=(command_queue, keypress_queue),
        daemon=True
    )
    selenium_thread.start()
    
    # Запускаем главный цикл Tkinter
    virtual_keyboard.mainloop()

if __name__ == "__main__":
    main()
