import cv2
import threading
import datetime
import torch
from ultralytics import YOLO
import easyocr
from PyQt5 import QtWidgets, QtGui
import sys

# Функция для сохранения номеров в файл
def save_to_file(plate, output_file):
    with open(output_file, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - {plate}\n")

# Функция для проверки формата узбекского номера
def is_uzbek_plate(plate):
    import re
    pattern = r"^[0-9]{2}[A-Z]{2}[0-9]{3}[A-Z]?$"
    return re.match(pattern, plate)

# Функция для обработки каждого кадра
def process_frame(frame, model, reader, output_file):
    results = model(frame)
    for result in results.xyxy[0]:  # Результаты детекции
        x1, y1, x2, y2, conf, cls = map(int, result[:6])
        if conf > 0.5:  # Уверенность в детекции
            roi = frame[y1:y2, x1:x2]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            text_results = reader.readtext(gray, detail=0)

            for text in text_results:
                if is_uzbek_plate(text):
                    print(f"Найден номер: {text}")
                    save_to_file(text, output_file)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Поток камеры
def camera_thread(camera_index, output_file, region, app):
    cap = cv2.VideoCapture(camera_index)
    model = YOLO("yolov8n.pt")  # Лёгкая версия YOLOv8
    reader = easyocr.Reader(["en"], gpu=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Разделение экрана на регионы
        height, width, _ = frame.shape
        if region == "left":
            frame = frame[:, :width // 2]
        else:
            frame = frame[:, width // 2:]

        process_frame(frame, model, reader, output_file)

        # Обновление интерфейса
        app.update_frame(region, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

# Класс интерфейса на PyQt
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Распознавание номеров")
        self.setGeometry(100, 100, 1200, 600)

        self.left_label = QtWidgets.QLabel(self)
        self.left_label.setGeometry(50, 50, 500, 500)

        self.right_label = QtWidgets.QLabel(self)
        self.right_label.setGeometry(600, 50, 500, 500)

    def update_frame(self, region, frame):
        """Обновление кадра в интерфейсе."""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = frame.shape
        qt_image = QtGui.QImage(frame.data, width, height, width * channels, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)

        if region == "left":
            self.left_label.setPixmap(pixmap)
        else:
            self.right_label.setPixmap(pixmap)

# Главная программа
if __name__ == "__main__":
    output_file = "plates.txt"

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Потоки для левого и правого региона
    threading.Thread(target=camera_thread, args=(0, output_file, "left", window)).start()
    threading.Thread(target=camera_thread, args=(0, output_file, "right", window)).start()

    sys.exit(app.exec_())
