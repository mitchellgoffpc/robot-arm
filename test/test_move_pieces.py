import time
import numpy as np
import ev3_dc as ev3
from xarm.wrapper import XArmAPI

arm = XArmAPI('192.168.1.170')
# arm.set_mode(2)
# arm.set_state(0)
# time.sleep(1)

# set up ev6
motor = ev3.Motor(protocol=ev3.USB, port=ev3.PORT_A)
motor.move_for(0.5, speed=20, direction=-1).start()
time.sleep(0.5)
closed = motor.position
open = motor.position + 30

H8 = np.array([146, 137, 385, -125.614064, 6.815906, -124.336712])
A8 = np.array([146, -161, 385, -125.614064, 6.815906, -124.336712])
A1 = np.array([434.6, -161, 385, -125.614064, 6.815906, -124.336712])
H1 = np.array([434.6, 137, 385, -125.614064, 6.815906, -124.336712])
CENTER = np.array([288, 0, 385, -125.614064, 6.815906, -124.336712])
DOWN = np.array([0, 0, -100, 0, 0, 0])
MVACC = 180
MOVE_SPEED = 100
DOWN_SPEED = 50

# for pos in [A1, H1, H8, A8]:
#   arm.set_position_aa(CENTER.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
#   arm.set_position_aa(pos.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
#   arm.set_position_aa((pos + DOWN).tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
#   time.sleep(2)
#   arm.set_position_aa(pos.tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)

positions = np.zeros((8, 8, 6))
for i in range(8):
  for j in range(8):
    positions[i, j, 0] = A1[0] + ((A8[0] - A1[0]) * j / 7)
    positions[i, j, 1] = A1[1] + ((H1[1] - A1[1]) * i / 7)
    positions[i, j, 2:] = A1[2:]

for i, idx in enumerate([(4, 1), (4, 3)]):
  pos = positions[idx]
  arm.set_position_aa(CENTER.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa(pos.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa((pos + DOWN).tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
  if i == 0:
    motor.move_for(duration=0.5, speed=20, direction=-1, brake=True).start()
  else:
    motor.move_to(position=open, speed=20, brake=True).start()

  time.sleep(2)
  arm.set_position_aa(pos.tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
