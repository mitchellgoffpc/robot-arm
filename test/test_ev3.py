import time
import ev3_dc as ev3

motor = ev3.Motor(protocol=ev3.USB, port=ev3.PORT_A)
motor.move_for(0.5, speed=20, direction=-1).start()
time.sleep(0.5)
closed = motor.position
open = motor.position + 30

task = motor.move_to(position=open, speed=20, brake=True).start()
time.sleep(0.5)
print(motor.position)

for _ in range(5):
  task = motor.move_for(duration=0.5, speed=20, direction=-1, brake=True).start()
  time.sleep(3)
  print(motor.position)
  task = motor.move_to(position=open, speed=20, brake=True).start()
  # task = motor.move_for(0.5, speed=20, direction=1, brake=True).start()
  time.sleep(3)
  print(motor.position)
