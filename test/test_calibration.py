import time
import numpy as np
from xarm.wrapper import XArmAPI

arm = XArmAPI('192.168.1.170')
# print(arm.get_position_aa())
# exit()

A1 = np.array([444, -164, 385, -125.614064, 6.815906, -122])
H1 = np.array([444, 137, 385, -125.614064, 6.815906, -122])
H8 = np.array([146, 137, 385, -125.614064, 6.815906, -122])
A8 = np.array([146, -164, 385, -125.614064, 6.815906, -122])
CENTER = np.array([288, 0, 385, -125.614064, 6.815906, -122])
DOWN = np.array([0, 0, -100, 0, 0, 0])
MVACC = 180
MOVE_SPEED = 100
DOWN_SPEED = 50

for pos in [H8, A1, H1, H8, A8]:
  arm.set_position_aa(CENTER.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa(pos.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa((pos + DOWN).tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
  time.sleep(2)
  arm.set_position_aa(pos.tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
