import serial
import time,os

def send_code(ser,op,addr,verbose=True):
  command=str(addr)+op+'\r\n'
  if (verbose):
    print(command)
  return ser.write(command.encode())

state_dict={
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

def get_state(ser,addr):
  len=send_code(ser,'TS',addr,verbose=False)
  ret=ser.readline()
  state=ret.decode()[-4:-2]
  error=int(ret.decode()[len-2:-4],16)
  return (state_dict[state],error)

def display_commands():
  os.system('cls' if os.name == 'nt' else 'clear')
  print("press 1 to move x manually")
  print("Press 2 to move y manually")
  print("Press 3 to auto scan-move")
  print("Press other to quit")

x_port=""
y_port=""

def send_and_wait(port,command):
  with serial.Serial(port,921600,timeout=1) as ser:
    send_code(ser,command,1,verbose=False)
    while get_state(ser,1)[0]!='READY':
      time.sleep(0.5)

def reset(port):
  with serial.Serial(port,921600,timeout=1) as ser:
    send_code(ser,"RS",1,verbose=False)
    while get_state(ser,1)[0]!='NOT REFERENCED':
      time.sleep(0.5)

def initialize():
  send_and_wait(x_port,"OR")
  send_and_wait(y_port,"OR")
  send_and_wait(x_port,"PA6")
  send_and_wait(y_port,"PA6")
  
def main_menu():
  initialize()
  while True:
    display_commands()
    receive=input(">")
    if receive=="1":
      pos=input("Input relative position for x-axis in mm; Press enter to move absolutely\n>")
      if pos=="":
        pos=input("Input new absolute position for x-axis in mm; Press enter to cancel\n>")
        send_and_wait(x_port,"PA"+pos)
      else:
        send_and_wait(x_port,"PR"+pos)
    elif receive=="2":
      pos=input("Input relative position for y-axis in mm; Press enter to move absolutely\n>")
      if pos=="":
        pos=input("Input new absolute position for y-axis in mm; Press enter to cancel\n>")
        send_and_wait(y_port,"PA"+pos)
      else:
        send_and_wait(y_port,"PR"+pos)
    elif receive=="3":
      xwidth=float(input("Input length in x side in mm\n>"))
      ywidth=float(input("Input length in y side in mm\n>"))
      inverval=int(input("Input wait time, in second\n>"))
      length=float(input("Input grid width, in micrometer\n>"))
      length=length/1000
      print("Start moving now, press ctrl+c to stop\n")
      try:
        pos=True
        for y in range(int(ywidth/length)):
            print("moving.. +x" if pos else "moving.. -x")
            for x in range(int(xwidth/length)):
              if not pos:
                send_and_wait(x_port,"PR-"+str(length))
              else:
                send_and_wait(x_port,"PR"+str(length))
              time.sleep(inverval)
            send_and_wait(y_port,"PR"+str(length))
            time.sleep(inverval)
            pos=not pos
      except:
        pass
      finally:
        print("resetting...")
        reset(x_port)
        reset(y_port)
        initialize()
    else:
      break

import serial.tools.list_ports
for port in serial.tools.list_ports.comports():
  if not port.serial_number:
    continue
  print("find device:" + port.serial_number)
  if port.serial_number.startswith("FT0GQDTE"):
    x_port=port.device
  if port.serial_number.startswith("FT0AVGBA"):
    y_port=port.device
if x_port=="" or y_port=="":
  print("Not connected!")
  exit()
main_menu()
