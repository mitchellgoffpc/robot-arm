import time
import numpy as np
from xarm.wrapper import XArmAPI

arm = XArmAPI('192.168.1.170')
# arm.set_mode(2)
# arm.set_state(0)
# time.sleep(1)

_, pos = arm.get_position_aa()
print(pos)

# while True:
#   print(arm.get_servo_angle(servo_id=None))
#   time.sleep(1)

# arm.set_servo_angle(servo_id=None, angle=[43.30, 34.50, 121.60, 92.00, -43.20, 234.20], speed=100, mvacc=180, is_radian=False, wait=True)
# time.sleep(3)
# arm.set_servo_angle(servo_id=None, angle=[-55.72, 41.4, 123.13, 275.02, -58.07, 105.51], speed=100, mvacc=180, is_radian=False, wait=True)
#
# _, pos = arm.get_servo_angle(servo_id=None)
# print(pos)

# arm.set_mode(0)
# arm.set_state(0)
# time.sleep(1)

# arm.set_servo_angle(servo_id=None, angle=[64, 31, 117, 90, -70, -116], speed=40, is_radian=False, wait=True)
# time.sleep(3)
#
# arm.set_servo_angle(servo_id=None, angle=[-67, 20, 112, 90, 66, -66], speed=40, is_radian=False, wait=True)
# time.sleep(3)

# while True:
#   _, pos = arm.get_position()
#   print(pos)
#   time.sleep(0.2)
