from kb import start_keyboard, open_keyboard, close_keyboard, stop_keyboard

def test_key_pressed(key):
    print(f"Key pressed during test: {key}")

if __name__ == "__main__":
    # Инициализация клавиатуры
    print("Starting keyboard test...")
    start_keyboard(test_key_pressed)

    # Открытие клавиатуры
    open_keyboard()

    # Держим приложение активным для теста
    try:
        input("Нажмите Enter для завершения теста...\n")
    except KeyboardInterrupt:
        print("Тест завершён.")

    # Закрытие и остановка клавиатуры
    close_keyboard()
    stop_keyboard()
