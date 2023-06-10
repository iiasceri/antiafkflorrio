import os
import platform
import threading
import time
import pyautogui
import pytesseract
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QCheckBox
from screeninfo import get_monitors
import sys


class TmpFlags:
    def __init__(self):
        self.hold_space = True


def isWindowsOS():
    return platform.system() == "Windows"


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


def space_key():
    pyautogui.keyUp('space')
    pyautogui.keyDown('space')

def scan_and_click(resized_image, searched_word, scale_factor_h, scale_factor_v):
    result = pytesseract.image_to_data(resized_image, output_type=pytesseract.Output.DICT)
    text = result['text']
    word_boxes = list(zip(result['left'], result['top'], result['width'], result['height']))
    for word, box in zip(text, word_boxes):
        searched_word_lower_case = str(searched_word).lower()
        word_lower_case = str(word).lower()
        if searched_word_lower_case in word_lower_case:
            center0 = box[0] / scale_factor_h + (box[2] / 2) / scale_factor_h
            center1 = box[1] / scale_factor_v + (box[3] / 2) / scale_factor_v
            if "?" in word_lower_case:
                for i in range(15):
                    center1 += 3
                    pyautogui.moveTo(center0, center1)
                    pyautogui.doubleClick(center0, center1)
            pyautogui.moveTo(center0, center1)
            pyautogui.doubleClick(center0, center1)

def anti_afk_florrio(searched_word):
    if isWindowsOS():
        image = pyautogui.screenshot()
        scale_factor_h = 1
        scale_factor_v = 1
        resized_image = image
    else:
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
    scan_and_click(resized_image, searched_word, scale_factor_h=scale_factor_h, scale_factor_v=scale_factor_v)


class Timer(threading.Thread):
    def __init__(self):
        self.interval = 4
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
        pyautogui.keyUp('space')
        tmp_flags.hold_space = False


class HelloWorldTimer(Timer):
    def __init__(self):
        super().__init__()
        self.is_running = False

    def timer(self):
        if self.is_running:
            if tmp_flags.hold_space:
                space_key()
            anti_afk_florrio("here")


hello_world_timer = HelloWorldTimer()


class SignalEmitter(QObject):
    update_next_click_label = Signal(str)
    update_next_click_label_to_idle = Signal()


def start_afk():
    global hello_world_timer
    if hello_world_timer is None or not hello_world_timer.is_alive():
        hello_world_timer = HelloWorldTimer()
        hello_world_timer.is_running = True
        hello_world_timer.start()


def stop_afk():
    global hello_world_timer
    if hello_world_timer is not None and hello_world_timer.is_alive():
        hello_world_timer.is_running = False
        hello_world_timer.stop()
        hello_world_timer = None  # Resetting the timer variable


tmp_flags = TmpFlags()
if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('macos')
    window = QWidget()
    window.setWindowTitle("afk auto clicker")  # Set the window title

    v_layout = QVBoxLayout()

    start_afk_btn = QPushButton('start afk auto click')
    stop_afk_btn = QPushButton('stop afk auto click')

    v_layout.addWidget(start_afk_btn)
    v_layout.addWidget(stop_afk_btn)
    v_layout.addWidget(QLabel('clicks every 4s on word ->here<-'))

    start_afk_btn.clicked.connect(start_afk)
    stop_afk_btn.clicked.connect(stop_afk)

    window.setLayout(v_layout)
    window.show()
    sys.exit(app.exec())
