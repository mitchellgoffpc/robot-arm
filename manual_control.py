import hid
import time
import numpy as np
import ev3_dc as ev3

DEVICE_ID = (0x057e, 0x2009)

def get_stick_data(data, left):
  data = data[(6 if left else 9):]
  stick_horizontal = data[0] | ((data[1] & 0xF) << 8)
  stick_vertical = (data[1] >> 4) | (data[2] << 4)
  return np.array([stick_vertical, -stick_horizontal])


if __name__ == '__main__':
    # set up arm with cartesian velocity control mode
  from xarm.wrapper import XArmAPI
  arm = XArmAPI('192.168.1.170')
  arm.set_mode(5)
  arm.set_state(0)
  time.sleep(1)
  _, arm_position = arm.get_position()

  # set up ev6
  motor = ev3.Motor(protocol=ev3.USB, port=ev3.PORT_A)
  motor.move_for(0.5, speed=20, direction=-1).start()
  time.sleep(0.5)
  closed = motor.position
  open = motor.position + 30

  # set up gamepad
  try:
    gamepad = hid.device()
    gamepad.open(*DEVICE_ID)
    gamepad.set_nonblocking(True)
  except Exception:
    print(f"device id {DEVICE_ID} not found")
    print("connected devices:")
    for device in hid.enumerate():
      print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
    exit()

  print("calibrating...")
  left_positions, right_positions = [], []
  left_center, right_center = None, None
  stopped = True

  while True:
    report = gamepad.read(64)
    if not report:
      continue

    left_pos = get_stick_data(report, True)
    right_pos = get_stick_data(report, False)
    if len(left_positions) >= 100:
      left_center = np.mean(left_positions, axis=0)
      right_center = np.mean(right_positions, axis=0)
      left_positions, right_positions = [], []
      print("done calibrating")

    if left_center is None:  # calibrating
      left_positions.append(left_pos)
      right_positions.append(right_pos)
    else:
      left_pos_norm = left_pos - left_center
      right_pos_norm = right_pos - right_center

      speed = np.zeros(6)
      if np.any(np.abs(left_pos_norm) > 100):
        speed[:2] = left_pos_norm * .03
      if np.abs(right_pos_norm[0]) > 100:
        speed[2] = right_pos_norm[0] * .03

      if np.any(speed):
        stopped = False
        arm.vc_set_cartesian_velocity(speed.tolist())
        time.sleep(0.05)
      elif not stopped:
        stopped = True
        arm.set_state(4)
        time.sleep(0.1)
        arm.set_mode(5)
        arm.set_state(0)

      if report[5] >> 7 == 1:
        motor.move_for(duration=0.5, speed=20, direction=-1, brake=True).start()
        time.sleep(0.5)
      elif report[3] >> 7 == 1:
        motor.move_to(position=open, speed=20, brake=True).start()
        time.sleep(0.5)
