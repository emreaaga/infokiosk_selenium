import os
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
# import win32print
# import win32api
import requests

pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

def manage_virtual_keyboard(open_keyboard):
    '''
    Управляет виртуальной клавиатурой на Linux.
    '''
    if open_keyboard:
        print('Открываем клаву')
        os.system("osk") 
    else:
        print('Закрываем клаву')
        os.system("taskkill /IM osk.exe /F")

def fetch_qr_image(qr_url):
    '''
    Загружает изображение QR-кода по указанному URL и возвращает его в виде байтового потока для дальнейшего использования.
    '''
    try:
        response = requests.get(qr_url)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        print(f"Ошибка загрузки QR-кода: {e}")
        return None

def print_receipt(receipt_data, qr_url, output_path="receipt.pdf", width_mm=58, height_mm=100):
    """
    Создает и сохраняет PDF для одного билета, отправляет его на печать, а затем удаляет файл.
    """
    qr_image_buffer = fetch_qr_image(qr_url)
    if not qr_image_buffer:
        print("Ошибка: QR-код не удалось загрузить.")
        return
    
    try:
        # Создаем PDF
        c = canvas.Canvas(output_path, pagesize=(width_mm * mm, height_mm * mm))
        c.setFont("DejaVu", 9)

        # Заголовок
        c.setFont("DejaVu", 7)
        c.drawCentredString((width_mm / 2) * mm, (height_mm - 10) * mm, f"Рейс: {receipt_data['Рейс']}")

        # Вставляем QR-код из байтов
        qr_reader = ImageReader(qr_image_buffer)
        c.drawImage(qr_reader, x=14 * mm, y=(height_mm - 42) * mm, width=30 * mm, height=30 * mm)

        # Основная информация
        c.setFont("DejaVu", 6)
        y_position = height_mm - 46
        for key, value in receipt_data.items():
            if key not in ["Рейс"]:
                c.drawString(2 mm, y_position * mm, f"{key}:")
                c.drawRightString((width_mm - 2) * mm, y_position * mm, f"{value}")
                y_position -= 4

        # Завершаем PDF
        c.save()

        print(f"PDF для билета сохранен: {output_path}")

        # Отправляем PDF на печать
        # win32api.ShellExecute(
        #     0,
        #     "print",
        #     output_path,
        #     None,
        #     ".",
        #     0
        # )
        print(f"Билет отправлен на печать: {output_path}")

    except Exception as e:
        print(f"Ошибка при создании и печати PDF: {e}")

    finally:
        # Удаляем файл после печати
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"PDF-файл удален: {output_path}")
        else:
            print(f"Файл {output_path} не найден для удаления.")