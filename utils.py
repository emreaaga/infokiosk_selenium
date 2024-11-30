import requests
from PIL import Image, ImageWin
# import win32print
# import win32ui
import os

def download_ticket(url, output_path="ticket.png"):
    """
    Скачивает чек по указанному URL и сохраняет его локально.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as file:
            file.write(response.content)
        print(f"Чек успешно скачан: {output_path}")
        return output_path
    except Exception as e:
        print(f"Ошибка при скачивании чека: {e}")
        return None

# def print_image(file_path):
#     """
#     Отправляет изображение на печать через термопринтер.
#     """
#     try:
#         # Указываем принтер
#         printer_name = win32print.GetDefaultPrinter()  # Или явно укажи имя принтера

#         # Загружаем изображение
#         image = Image.open(file_path)

#         # Подготовка к печати
#         hprinter = win32print.OpenPrinter(printer_name)
#         hdc = win32ui.CreateDC()
#         hdc.CreatePrinterDC(printer_name)
#         hdc.StartDoc("Печать билета")
#         hdc.StartPage()

#         # Подгоняем изображение под ширину термопринтера
#         printer_width = 576  # Ширина термопринтера (зависит от модели, например, 384px)
#         image = image.resize((printer_width, int(printer_width * image.size[1] / image.size[0])))

#         # Печать изображения
#         dib = ImageWin.Dib(image)
#         dib.draw(hdc.GetHandleOutput(), (0, 0, image.width, image.height))

#         hdc.EndPage()
#         hdc.EndDoc()
#         hdc.DeleteDC()
#         win32print.ClosePrinter(hprinter)

#         print(f"Файл {file_path} успешно отправлен на печать.")
#     except Exception as e:
#         print(f"Ошибка при печати: {e}")

def process_and_print_ticket(download_url):
    """
    Основная функция для скачивания и печати чека.
    """
    file_path = download_ticket(download_url)

    # if file_path:
    #     # Печатаем файл
    #     print_image(file_path)

    #     # Удаляем файл после печати
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #         print(f"Временный файл {file_path} удален.")
