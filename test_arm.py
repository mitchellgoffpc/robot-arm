import time
from xarm.wrapper import XArmAPI
arm = XArmAPI('192.168.1.170')

while True:
  _, pos = arm.get_position()
  print(pos)
  time.sleep(0.2)
