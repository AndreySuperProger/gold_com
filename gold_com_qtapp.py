import serial
from serial.tools import list_ports
import threading
import time
import keyboard
import sys, os
from queue import Queue

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QGridLayout, QLineEdit, QTextBrowser, QSpinBox, QLabel
from PyQt5.QtCore import pyqtSignal, QObject

commandsQueue = Queue()
controllerOutputText = object()
ser = object()


GET_VERSION = "{\"method\" : \"get version\", \"params\" : null, \"id\" : 0}"
GET_STATE = "{\"method\" : \"get state\",\"params\" : \"12345678911\",\"id\" : 1}"
SERVO_OPEN = "{\"method\" : \"servo\", \"params\" : {\"cell\" : %d, \"command\" : \"open\"}, \"id\" : 58}"
SERVO_CLOSE = "{\"method\" : \"servo\", \"params\" : {\"cell\" : %d, \"command\" : \"close\"}, \"id\" : 1}"
SERVO_CALIBRATE = "{\"method\" : \"calibrate\", \"params\" : null, \"id\" : 78}"
SERVO_SET_ANGLE = "{\"method\" : \"servo set angle\", \"params\" : {\"cell\" : %d, \"angle\" : %d}, \"id\" : 0}"
THRASH = "kcjsahfih"

class Communicate(QObject):
    controllerOutputSignal = pyqtSignal(str)

class MyTextBox(QTextBrowser):
    def __init__(self, parentWidget):
        super().__init__(parentWidget)
        self.c = Communicate()
        self.c.controllerOutputSignal.connect(lambda x: self.setText(x))

def readThread_func():
    while True:
        #print(ser.readline())
        if ser.inWaiting() > 0:
            inputStr = ser.readline()
            print(inputStr.decode())
            controllerOutputText.c.controllerOutputSignal.emit(inputStr.decode())
            
def writeThread_func():
    while True:
        command = commandsQueue.get()
        print(command)
        ser.write(command.encode())
        
def keyboardThread_func():
    while True:
        if keyboard.is_pressed('ESC'):
            print("esc\n\r")
            os._exit(1)
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        com_port = list_ports.comports()[0].device
        ser = serial.Serial('\\\\.\\{}'.format(com_port), 115200,
            serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 0.1)
        # ser.setRTS(0)
        # ser.setDTR(1)
        # time.sleep(1)
        # ser.setDTR(0)
    except: pass

    app = QApplication([])
    mainwindow = QWidget()

    layout = QGridLayout()

    get_version_btn = QPushButton(mainwindow, text = "get version")
    get_version_btn.pressed.connect(lambda: commandsQueue.put(GET_VERSION))
  
    get_state_btn = QPushButton(mainwindow, text = "get state")
    get_state_btn.pressed.connect(lambda: commandsQueue.put(GET_STATE))

    servo_open_btn = QPushButton(mainwindow, text = "servo open")
    servo_open_cell_label = QLabel(mainwindow, text = "cell:")
    servo_open_cell_label.setAlignment(Qt.AlignRight)
    servo_open_cell_box = QSpinBox(mainwindow)
    servo_open_cell_box.setRange(1, 10)
    servo_open_btn.pressed.connect(lambda: commandsQueue.put(SERVO_OPEN % (servo_open_cell_box.value() - 1)))

    servo_close_btn = QPushButton(mainwindow, text = "servo close")
    servo_close_cell_label = QLabel(mainwindow, text = "cell:")
    servo_close_cell_label.setAlignment(Qt.AlignRight)
    servo_close_cell_box = QSpinBox(mainwindow)
    servo_close_cell_box.setRange(1, 10)
    servo_close_btn.pressed.connect(lambda: commandsQueue.put(SERVO_CLOSE % (servo_close_cell_box.value() - 1)))

    calibrate_btn = QPushButton(mainwindow, text = "calibrate")
    calibrate_btn.pressed.connect(lambda: commandsQueue.put(SERVO_CALIBRATE))

    servo_set_angle_btn = QPushButton(mainwindow, text = "servo set angle")
    servo_set_angle_cell_label = QLabel(mainwindow, text = "cell:")
    servo_set_angle_cell_label.setAlignment(Qt.AlignRight)
    servo_set_angle_cell_box = QSpinBox(mainwindow)
    servo_set_angle_cell_box.setRange(1, 10)
    servo_set_angle_angle_label = QLabel(mainwindow, text = "angle:")
    servo_set_angle_angle_label.setAlignment(Qt.AlignRight)
    servo_set_angle_angle_box = QSpinBox(mainwindow)
    servo_set_angle_angle_box.setRange(0, 120)
    servo_set_angle_btn.pressed.connect(lambda: commandsQueue.put(
        SERVO_SET_ANGLE % (servo_set_angle_cell_box.value() - 1, servo_set_angle_angle_box.value())))

    thrash_btn = QPushButton(mainwindow, text = "thrash")
    thrash_btn.pressed.connect(lambda: commandsQueue.put(THRASH))

    controllerOutputText = MyTextBox(mainwindow)

    layout.addWidget(get_version_btn, 0, 0)
    layout.addWidget(get_state_btn, 1, 0)
    layout.addWidget(servo_open_btn, 2, 0)
    layout.addWidget(servo_open_cell_label, 2, 1)
    layout.addWidget(servo_open_cell_box, 2, 2)
    layout.addWidget(servo_close_btn, 3, 0)
    layout.addWidget(servo_close_cell_label, 3, 1)
    layout.addWidget(servo_close_cell_box, 3, 2)
    layout.addWidget(calibrate_btn, 4, 0)
    layout.addWidget(servo_set_angle_btn, 5, 0)
    layout.addWidget(servo_set_angle_cell_label, 5, 1)
    layout.addWidget(servo_set_angle_cell_box, 5, 2)
    layout.addWidget(servo_set_angle_angle_label, 5, 3)
    layout.addWidget(servo_set_angle_angle_box, 5, 4)
    layout.addWidget(thrash_btn, 6, 0)
    layout.addWidget(controllerOutputText, 7, 0, 1, 5)

    mainwindow.setLayout(layout)
    mainwindow.setMinimumWidth(500)
    mainwindow.show()

    readThread = threading.Thread(target=readThread_func)
    readThread.start()
    writeThread = threading.Thread(target=writeThread_func)
    writeThread.start()
    keyboardThread = threading.Thread(target=keyboardThread_func)
    keyboardThread.start()

    os._exit(app.exec_())
