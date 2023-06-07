import os
import threading
import time

import pyautogui
import pytesseract
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
from screeninfo import get_monitors

import sys

def get_mac_screen_hw(w_or_h):
    with os.popen("system_profiler SPDisplaysDataType | grep Resolution") as f:
        string_l = f.readlines()
        string = string_l[0]
        string = string.strip()
        resolution = string.split(':')[1]
        width, height = resolution.split('x')
        if str(w_or_h).lower() == "w":
            return int(width.strip().replace('Retina', '').replace(' ', ''))
        elif str(w_or_h).lower() == "h":
            return int(height.strip().replace('Retina', '').replace(' ', ''))


def anti_afk_florrio(searched_word):
    monitor = get_monitors()[0]  # Assuming a single monitor setup
    new_width = monitor.width
    new_height = monitor.height
    # resizing
    image = pyautogui.screenshot()
    original_width, original_height = image.size

    if new_width and new_height:
        width_ratio = new_width / original_width
        height_ratio = new_height / original_height
        ratio = min(width_ratio, height_ratio)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
    elif new_width:
        ratio = new_width / original_width
        new_height = int(original_height * ratio)
    elif new_height:
        ratio = new_height / original_height
        new_width = int(original_width * ratio)
    else:
        raise ValueError("At least one of new_width or new_height should be provided")

    # searching
    mac_h = get_mac_screen_hw("h")
    mac_w = get_mac_screen_hw("w")
    scale_factor_h = mac_h / new_width
    scale_factor_v = mac_w / new_height
    resized_image = image.resize((mac_h, mac_w))

    result = pytesseract.image_to_data(resized_image, output_type=pytesseract.Output.DICT)
    text = result['text']
    word_boxes = list(zip(result['left'], result['top'], result['width'], result['height']))
    for word, box in zip(text, word_boxes):
        # print(f"Word: {word}, Bounding Box: {box}")
        searched_word_lower_case = str(searched_word).lower()
        word_lower_case = str(word).lower()
        if searched_word_lower_case in word_lower_case:
            print(f"Word: {word}, Bounding Box: {box}")
            center0 = box[0] / scale_factor_h + (box[2] / 2) / scale_factor_h
            center1 = box[1] / scale_factor_v + (box[3] / 2) / scale_factor_v
            if "?" in word_lower_case:
                for i in range(15):
                    center1 += 3
                    pyautogui.moveTo(center0, center1)
                    pyautogui.doubleClick(center0, center1)
            pyautogui.moveTo(center0, center1)
            pyautogui.doubleClick(center0, center1)


class Timer(threading.Thread):
    def __init__(self):
        self.interval = 60
        self._timer_runs = threading.Event()
        self._timer_runs.set()
        super().__init__()

    def set_interval(self, interval):
        self.interval = interval

    def run(self):
        while self._timer_runs.is_set():
            self.timer()
            time.sleep(self.interval)

    def stop(self):
        self._timer_runs.clear()


class HelloWorldTimer(Timer):
    def __init__(self):
        super().__init__()

    def timer(self):
        anti_afk_florrio("here")
        next_loop = time.time() + self.interval
        while time.time() < next_loop:
            remaining_time = next_loop - time.time()
            remaining_time_str = f"Next check to click in: {remaining_time:.1f} seconds"
            update_next_click_label.emit(remaining_time_str)
            time.sleep(1)
            if not self._timer_runs.is_set():
                break


hello_world_timer = HelloWorldTimer()

class SignalEmitter(QObject):
    update_next_click_label = Signal(str)
    update_next_click_label_to_idle = Signal()


signal_emitter = SignalEmitter()
update_next_click_label = signal_emitter.update_next_click_label
update_next_click_label_to_idle = signal_emitter.update_next_click_label_to_idle


def start_afk():
    global hello_world_timer
    if hello_world_timer is None or not hello_world_timer.is_alive():
        hello_world_timer = HelloWorldTimer()
        hello_world_timer.start()


def stop_afk():
    global hello_world_timer
    if hello_world_timer is not None and hello_world_timer.is_alive():
        hello_world_timer.stop()
        update_next_click_label_to_idle.emit()
        hello_world_timer = None  # Resetting the timer variable


def update_timer_value(new_interval):
    if new_interval != '':
        new_interval_int = int(new_interval)
        hello_world_timer.set_interval(new_interval_int)
    else:
        hello_world_timer.set_interval(60)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('macos')
    window = QWidget()
    window.setWindowTitle("AFK Auto Clicker")

    v_layout = QVBoxLayout()

    input_field = QLineEdit('60')

    startAfkBtn = QPushButton('Start afk auto click')
    stopAfkBtn = QPushButton('Stop afk auto click')

    next_click_label = QLabel('Doing nothing now')

    v_layout.addWidget(QLabel('FLORR IO ANTI ANTI AFK:'))
    v_layout.addWidget(QLabel('afk text: \'here\''))
    v_layout.addWidget(startAfkBtn)
    v_layout.addWidget(stopAfkBtn)
    v_layout.addWidget(QLabel('check for afk dialog every (seconds):'))
    v_layout.addWidget(input_field)
    v_layout.addWidget(next_click_label)

    startAfkBtn.clicked.connect(start_afk)
    stopAfkBtn.clicked.connect(stop_afk)
    input_field.textChanged.connect(update_timer_value)

    update_next_click_label.connect(next_click_label.setText)
    update_next_click_label_to_idle.connect(lambda: next_click_label.setText('Doing nothing now'))

    window.setLayout(v_layout)
    window.show()
    sys.exit(app.exec())
