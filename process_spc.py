step=1
start=520
stop=540
name="110 data Laser Imaging.SPC"
width=10
height=10
omit_data=10
matrix={}
data={}
for i in range(start,stop,step):
    matrix[i]=[]
    data[i]=[]
    for j in range(height):
        matrix[i].append([])
        data[i].append([])
        for k in range(width):
            matrix[i][j].append(0)
            data[i][j].append([])
def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
import spc
f=spc.File(name)
fdata=f.data_txt().split("\n")
for samples in fdata:
    dat=samples.split("\t")
    if len(dat)==1:
        continue
    wavelength=dat[0]
    col=0
    row=0
    reverse=False
    for j in range(omit_data+1,omit_data+width*height+1):
        if j>=len(dat):
            amp=0
        else:
            amp=dat[j]
        idx=round(float(wavelength)/step)*step
        if idx<start or idx>=stop:
            continue
        data[idx][row][col].append(float(amp))
        if reverse:
            col-=1
        else:
            col+=1
        if (reverse and col==-1) or (not reverse and col%width==0):
            reverse=not reverse
            row+=1
            col=width-1 if reverse else 0

for i in range(start,stop,step):
    for j in range(height):
        for k in range(width):
            if len(data[i][j][k])==0:
                continue
            matrix[i][j][k]=sum(data[i][j][k]) / float(len(data[i][j][k]))
import os
import matplotlib.pyplot as plt
if not os.path.exists("output"):
    os.mkdir("output")
for i in matrix.keys():
    name=str(i)
    fig, ax = plt.subplots()
    cax=ax.imshow(matrix[i], interpolation='nearest')
    ax.set_title(name)
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['bottom'].set_position(('outward', 10))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    fig.colorbar(cax)
    plt.savefig("output/"+name+".png")
    plt.close()