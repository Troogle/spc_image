import threading
import time
import sys

from PyQt5.QtWidgets import QMessageBox

import serial
import serial.tools.list_ports

state_dict = {
    '0A': 'NOT REFERENCED',
    '0B': 'NOT REFERENCED',
    '0C': 'NOT REFERENCED',
    '0D': 'NOT REFERENCED',
    '0E': 'NOT REFERENCED',
    '0F': 'NOT REFERENCED',
    '10': 'NOT REFERENCED',
    '14': 'CONFIGURATION',
    '1E': 'HOMING',
    '28': 'MOVING',
    '32': 'READY',
    '33': 'READY',
    '34': 'READY',
    '36': 'READY T',
    '37': 'READY T',
    '38': 'READY T',
    '3C': 'DISABLE',
    '3D': 'DISABLE',
    '3E': 'DISABLE',
    '3F': 'DISABLE',
    '46': 'TRACKING',
    '47': 'TRACKING',
}


def send_command(ser, op, addr, verbose=True):
    command = str(addr) + op + '\r\n'
    if verbose:
        print(command)
    return ser.write(command.encode())


def get_state(ser, addr):
    len = send_command(ser, 'TS', addr, verbose=False)
    ret = ser.readline()
    state = ret.decode()[-4:-2]
    error = int(ret.decode()[len - 2:-4], 16)
    return state_dict[state], error


def init_port():
    x_port = ""
    y_port = ""
    for port in serial.tools.list_ports.comports():
        if not port.serial_number:
            continue
        print("find device:" + port.serial_number)
        if port.serial_number.startswith("FT0GQDTE"):
            x_port = port.device
        if port.serial_number.startswith("FT0AVGBA"):
            y_port = port.device
    if x_port == "" or y_port == "":
        print("Not connected!")
        return {}
        #sys.exit()
    return {"x": x_port, "y": y_port}


def send_and_wait(ser, command, wait=True):
    send_command(ser, command, 1, verbose=False)
    if wait:
        while get_state(ser, 1)[0] != 'READY':
            time.sleep(0.5)


def reset(ser):
    send_command(ser, "RS", 1, verbose=False)
    while get_state(ser, 1)[0] != 'NOT REFERENCED':
        time.sleep(0.5)


def move_to_default(ser):
    #reset(ser)
    send_and_wait(ser, "OR")
    send_and_wait(ser, "PA6")


def move_relative(ser, length):
    send_and_wait(ser, "PR" + str(length))


# serials={"x":ser, "y":ser}
def move_all_to_default(serials):
    x_reset_thread = threading.Thread(target=move_to_default, args=(serials["x"],))
    x_reset_thread.setDaemon(True)
    y_reset_thread = threading.Thread(target=move_to_default, args=(serials["y"],))
    y_reset_thread.setDaemon(True)
    x_reset_thread.start()
    y_reset_thread.start()
    x_reset_thread.join()
    y_reset_thread.join()


# serials={"x":ser, "y":ser}
def cycle_move(serials, width, height, delay, step_size, update_signal=None, parent=None):
    current_move = 0
    h_move=int(height / step_size)
    w_move=int(width / step_size)-1
    total_move = h_move * w_move
    pos = True
    try:
        for y in range(h_move):
            print("moving.. +x" if pos else "moving.. -x")
            for x in range(w_move):
                if not pos:
                    send_and_wait(serials["x"], "PR-" + str(step_size), False)
                else:
                    send_and_wait(serials["x"], "PR" + str(step_size), False)
                time.sleep(delay)
                current_move += 1
                update_signal.emit(current_move, total_move)
            send_and_wait(serials["y"], "PR" + str(step_size), False)
            time.sleep(delay)
            current_move += 1
            if update_signal is not None:
                update_signal.emit(current_move, total_move)
            pos = not pos
    finally:
        if parent is not None:
            QMessageBox.information(parent, "Info", "Scan completed, press ok to reset")
        print("resetting...")
        move_all_to_default(serials)
