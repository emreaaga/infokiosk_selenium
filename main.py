import threading
import tkinter as tk
from virtual_keyboard import start_keyboard
from selenium_controller import selenium_thread_function, send_key_callback

def main():
    # Start the virtual keyboard
    start_keyboard(send_key_callback)
    # Start the Selenium thread
    selenium_thread = threading.Thread(target=selenium_thread_function, daemon=True)
    selenium_thread.start()
    # Start the Tkinter event loop
    tk.mainloop()

if __name__ == "__main__":
    main()
