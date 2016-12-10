import subprocess
import sys

import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg
import tkinter
import tkinter.filedialog
import os
import spc


def open_folder(location):
    if sys.platform.startswith('linux'):
        subprocess.call(["xdg-open", location])
    else:
        os.startfile(location)


def convert(filename, width, height, grid_size, omit_data, start_freq, end_freq, freq_step, update_signal=None):
    os.chdir(os.path.dirname(os.path.abspath(filename)))
    if not os.path.exists("output"):
        os.mkdir("output")
    width = int(width / grid_size)  # number of grids
    height = int(height / grid_size)
    matrix = {}
    data = {}
    for i in range(start_freq, end_freq, freq_step):
        matrix[i] = []
        data[i] = []
        for j in range(height):
            matrix[i].append([])
            data[i].append([])
            for k in range(width):
                matrix[i][j].append(0)
                data[i][j].append([])

    f = spc.File(filename)
    fdata = f.data_txt().split("\n")
    for samples in fdata:
        dat = samples.split("\t")
        if len(dat) == 1:
            continue
        wavelength = dat[0]
        col = 0
        row = 0
        reverse = False
        for j in range(omit_data + 1, omit_data + width * height + 1):
            if j >= len(dat):
                amp = 0
            else:
                amp = dat[j]
            idx = round(float(wavelength) / freq_step) * freq_step
            if idx < start_freq or idx >= end_freq:
                continue
            data[idx][row][col].append(float(amp))
            if reverse:
                col -= 1
            else:
                col += 1
            if (reverse and col == -1) or (not reverse and col % width == 0):
                reverse = not reverse
                row += 1
                col = width - 1 if reverse else 0

    # calculate avg
    for i in range(start_freq, end_freq, freq_step):
        for j in range(height):
            for k in range(width):
                if len(data[i][j][k]) == 0:
                    continue
                matrix[i][j][k] = sum(data[i][j][k]) / float(len(data[i][j][k]))

    # output
    total = len(matrix)
    current = 0
    for i in matrix.keys():
        name = str(i)
        fig, ax = plt.subplots()
        cax = ax.imshow(matrix[i], interpolation='nearest')
        ax.set_title(name)
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['bottom'].set_position(('outward', 10))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')
        fig.colorbar(cax)
        plt.savefig("output/" + name + ".png")
        plt.close()
        current += 1
        if update_signal is not None:
            update_signal.emit(current, total)

    open_folder(os.path.join(os.curdir, "output"))
