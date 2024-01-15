#!/usr/bin/env python3
import io
import time
import chess
import chess.pgn
import chess.svg
import chess.engine
import tkinter as tk
import pygame
import pygame.camera
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

WEBCAM_NAME = 'Logitech Webcam C930e'
PHOTO_ANGLES = [
  [64, 31, 117, 90, -70, -116],
  [-67, 20, 112, 90, 66, -66],
]

def read_pgns(pgn_fn):
  game = []

  with open(pgn_fn) as f:
    for line in f:
      game.append(line)
      if line.startswith('1.'):
        yield chess.pgn.read_game(io.StringIO(''.join(game)))
        game = []


class ChessGui(tk.Frame):
  def __init__(self, parent, pgns, arm, cam, data_dir, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.pgns = pgns
    self.arm = arm
    self.cam = cam
    self.data_dir = data_dir

    self.grid()
    self.game, self.move = 0, 0
    self.chessboard = next(pgns)
    self.canvas = tk.Canvas(self, width=510, height=510, bg="grey")
    self.canvas.grid(row=0, column=0)
    self.canvas.bind("<Button-1>", self.click)
    self.selected_position = None
    self.draw_board()

  def draw_board(self):
    board_svg = chess.svg.board(board=self.chessboard.board(), fill={self.selected_position: '#cc0000cc'}, size=510)
    drawing = svg2rlg(io.StringIO(board_svg))
    imgdata = io.BytesIO()
    renderPM.drawToFile(drawing, imgdata, fmt='png')
    imgdata.seek(0)
    self.board_photo = tk.PhotoImage(data=imgdata.read())
    self.canvas.create_image(0, 0, anchor='nw', image=self.board_photo)

  def click(self, event):
    self.chessboard = self.chessboard.next()
    self.move += 1
    if self.chessboard is None:
      self.chessboard = next(pgns)
      self.game += 1
      self.move = 0

    self.draw_board()
    self.parent.after(100, self.take_snapshot)

  def take_snapshot(self):
    for i, angles in enumerate(PHOTO_ANGLES):
      self.arm.set_servo_angle(servo_id=None, angle=angles, speed=50, mvacc=90, is_radian=False, wait=True)
      time.sleep(0.2)
      image = cam.get_image()
      pygame.image.save(image, data_dir / f'positions/{self.game:03d}-{self.move:03d}-{i}.jpg')


if __name__ == "__main__":
  from xarm.wrapper import XArmAPI

  arm = XArmAPI('192.168.1.170')
  arm.set_mode(0)
  arm.set_state(0)
  time.sleep(0.1)

  pygame.camera.init()
  camlist = pygame.camera.list_cameras()
  if WEBCAM_NAME not in camlist:
    raise RuntimeError("No camera on current device")
  cam = pygame.camera.Camera(WEBCAM_NAME, (640, 480))
  cam.start()

  data_dir = Path(__file__).parent / 'data'
  (data_dir / 'positions').mkdir(exist_ok=True)

  pgns = read_pgns(data_dir / '2022.pgn')
  root = tk.Tk()
  ChessGui(root, pgns, arm, cam, data_dir)
  root.mainloop()
