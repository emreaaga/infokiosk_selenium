import os
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service

# Импортируем функции из utils.py
from utils import (
    manage_virtual_keyboard,
    print_receipt
)

# Настройка браузера
chrome_options = Options()
chrome_options.add_argument("--kiosk")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-infobars")

#Создание веб-драйвера (предполагаем, что chromedriver установлен в PATH)
driver = webdriver.Chrome(options=chrome_options)

# Укажи путь к chromedriver.exe
# driver_path = "C:\\info_kiosk\\chromedriver.exe"  # Замени на реальный путь
# Создание службы для ChromeDriver
# service = Service(driver_path)
# Создание веб-драйвера
# driver = webdriver.Chrome(service=service, options=chrome_options)


try:
    # Список маршрутов, которые перенаправляем на домашнюю страницу
    redirect_urls = [
        "https://avtoticket.uz/faq",
        "https://avtoticket.uz/web-difficult-to-reservation",
        "https://avtoticket.uz/about-us",
    ]
    
    # Создаем драйвер
    driver.get("https://avtoticket.uz")
    print("Ожидание действий пользователя...")

    virtual_keyboard_open = False  # Состояние виртуальной клавиатуры
    last_url = None  # Последний URL для отслеживания изменений страницы

    while True:
        current_url = driver.current_url
        
        if current_url != last_url:
            last_url = current_url
            print(f"Перешли на новую страницу: {current_url}")
        
        # Перенаправление для страниц из списка redirect_urls
        if any(current_url.startswith(url.strip("/")) for url in redirect_urls):
            print(f"Страница {current_url} не разрешена. Перенаправляем на главную страницу.")
            driver.get("https://avtoticket.uz")
            continue

        
        # На странице "/tickets/"
        if "/tickets/" in current_url:
            try:
                # Проверяем наличие всех необходимых полей
                name_input = driver.find_element(By.ID, "nd-name0")  # Поле для имени пассажира
                tel_input = driver.find_element(By.ID, "nd-tel0")  # Поле для номера телефона
                email_input = driver.find_element(By.ID, "nd-email0")  # Поле для эл. почты
                print("Найдены поля для имени, телефона и email")

                # Если клавиатура не включена, включаем
                if not virtual_keyboard_open:
                    manage_virtual_keyboard(True)
                    virtual_keyboard_open = True

            except NoSuchElementException:
                # Если полей нет, выключаем клавиатуру (если она включена)
                print("Поля ввода не найдены.")
                if virtual_keyboard_open:
                    manage_virtual_keyboard(False)
                    virtual_keyboard_open = False

        # На странице "/payment-payme/"
        elif "/payment-payme/" in current_url:
            try:
                # Проверяем наличие хотя бы одного из полей
                field_found = False
                try:
                    card_number_input = driver.find_element(By.ID, "nd-name")
                    field_found = True
                    print("Найдено поле: Номер карты")
                except NoSuchElementException:
                    pass

                try:
                    ex_date_input = driver.find_element(By.ID, "nd-tel")
                    field_found = True
                    print("Найдено поле: Срок действия карты")
                except NoSuchElementException:
                    pass

                try:
                    code_input = driver.find_element(By.ID, "brr")
                    field_found = True
                    print("Найдено поле: Код из SMS")
                except NoSuchElementException:
                    pass

                # Если состояние полей изменилось, включаем/выключаем клавиатуру
                if field_found and not current_fields_state:
                    manage_virtual_keyboard(True)
                    virtual_keyboard_open = True
                    current_fields_state = True
                elif not field_found and current_fields_state:
                    manage_virtual_keyboard(False)
                    virtual_keyboard_open = False
                    current_fields_state = False

            except Exception as e:
                print(f"Ошибка на странице /payment-payme/: {e}")
                if current_fields_state:
                    manage_virtual_keyboard(False)
                    virtual_keyboard_open = False
                    current_fields_state = False


        elif "/bought-tickets/" in current_url:
            print("Находимся на странице с купленными билетами.")
            try:
                ticket_elements = driver.find_elements(By.CSS_SELECTOR, "div.tickets_all_child")  # Все билеты

                if ticket_elements:
                    print(f"Найдено {len(ticket_elements)} билетов.")

                    for i, ticket_element in enumerate(ticket_elements, start=1):
                        # Собираем данные о билете
                        labels = ticket_element.find_elements(By.CSS_SELECTOR, "p.tickets_all_body_1pp")
                        values = ticket_element.find_elements(By.CSS_SELECTOR, "h5.tickets_all_body_1_h5")
                        qr_element = ticket_element.find_element(By.CSS_SELECTOR, "img[src*='qr.png']")
                        qr_url = qr_element.get_attribute("src")

                        # Формируем словарь с данными билета
                        receipt_data = {
                            label.text.strip().replace(":", ""): value.text.strip()
                            for label, value in zip(labels, values)
                        }

                        # Печатаем билет
                        print(f"Печать билета №{i}...")
                        print_receipt(receipt_data, qr_url, output_path=f"ticket_{i}.pdf")

                    # После печати перенаправляем на главную страницу
                    driver.get("https://avtoticket.uz")
                    print("Перенаправляем на главную страницу.")

                else:
                    print("Билеты не найдены.")

            except Exception as e:
                print(f"Ошибка при обработке страницы с купленными билетами: {e}")

        
        # На странице восстановления билета "/ticket-recovery/"
        elif "/ticket-recovery" in current_url:
            print("Находимся на странице восстановления билета.")
            try:
                # Проверяем наличие поля ввода номера телефона
                while True:
                    try:
                        # Проверяем, существует ли поле ввода
                        phone_input = driver.find_element(By.ID, "brr")
                        print("Найдено поле ввода номера телефона.")

                        # Если клавиатура не включена, включаем
                        if not virtual_keyboard_open:
                            manage_virtual_keyboard(True)
                            virtual_keyboard_open = True

                        # Задержка перед повторной проверкой
                        time.sleep(2)

                    except NoSuchElementException:
                        # Поле ввода номера телефона исчезло
                        print("Поле ввода номера телефона больше не найдено. Переходим к поиску QR-кода.")

                        # Если клавиатура включена, выключаем
                        if virtual_keyboard_open:
                            manage_virtual_keyboard(False)
                            virtual_keyboard_open = False

                        # Переходим к поиску QR-кода
                        try:
                            qr_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='qr.png']"))
                            )
                            qr_url = qr_element.get_attribute("src")

                            labels = driver.find_elements(By.CSS_SELECTOR, "p.tickets_all_body_1pp, p.tickets_all_child_body_footerpp_2")
                            values = driver.find_elements(By.CSS_SELECTOR, "h5.tickets_all_body_1_h5, h5.tickets_all_child_body_footerh5_2")

                            if labels and values and qr_url:
                                print("Данные чека найдены!")
                                receipt_data = {label.text.strip().replace(":", ""): value.text.strip() for label, value in zip(labels, values)}
                                print_receipt(receipt_data, qr_url, width_mm=58, height_mm=100)

                                # Перенаправляем на главную страницу
                                driver.get("https://avtoticket.uz")
                                print("Перенаправляем на главную страницу.")
                                break

                        except TimeoutException:
                            print("Не удалось найти чек или QR-код.")
                        except Exception as e:
                            print(f"Ошибка при поиске данных чека: {e}")
                        break

            except Exception as e:
                print(f"Ошибка на странице восстановления билета: {e}")

        # Если URL не соответствуеkт ожидаемым, выключаем клавиатуру
        else:
            if virtual_keyboard_open:
                print("Выключаем клавиатуру, так как страница не требует ввода.")
                manage_virtual_keyboard(False)
                virtual_keyboard_open = False
                current_fields_state = False

        # Короткая пауза перед следующей итерацией
        time.sleep(2)

except KeyboardInterrupt:
    print("Остановка скрипта пользователем.")
    
finally:
    # Закрываем виртуальную клавиатуру при завершении работы
    if virtual_keyboard_open:
        manage_virtual_keyboard(False)
    driver.quit()
