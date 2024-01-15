import hid

for device in hid.enumerate():
  print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
exit()

gamepad = hid.device()
gamepad.open(0x057e, 0x2009)
gamepad.set_nonblocking(True)

def get_stick_data(data, left):
  data = data[(6 if left else 9):]
  stick_horizontal = data[0] | ((data[1] & 0xF) << 8)
  stick_vertical = (data[1] >> 4) | (data[2] << 4)
  return stick_horizontal, stick_vertical

while True:
    report = gamepad.read(64)
    if report:
        # print(' '.join(f'{x:03d}' for x in report))
        # print(get_stick_data(report, True), get_stick_data(report, False))
        print(report[5] >> 7 == 1, report[3] >> 7 == 1)
