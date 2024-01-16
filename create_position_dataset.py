#!/usr/bin/env python3
import io
import time
import chess
import chess.pgn
import chess.svg
import chess.engine
import tkinter as tk
import threading
import pygame
import pygame.camera
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

FILL_COLOR = '#cc0000cc'
WEBCAM_NAME = 'Logitech Webcam C930e'
PHOTO_ANGLES = [
  [43.30, 34.50, 121.60, 92.00, -43.20, 234.20],
  [-55.72, 41.4, 123.13, 275.02, -58.07, 105.51],
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
    self.game_id, self.move_id = 0, 0
    self.hand_photo_id = -1
    self.chessboard = next(self.pgns)

    existing_games = set(int(x.name.split('-')[0]) for x in (self.data_dir / 'positions').iterdir())
    while self.game_id in existing_games:
      self.next_move()

    self.grid()
    self.canvas = tk.Canvas(self, width=510, height=510, bg="grey")
    self.canvas.grid(row=0, column=0)
    self.canvas.bind("<Button-1>", self.click)
    self.selected_position = None
    self.draw_board()

    self.hand_snapshot_thread = threading.Thread(target=self.take_hand_snapshots, daemon=True)
    self.hand_snapshot_thread.start()

  def next_move(self):
    self.chessboard = self.chessboard.next()
    self.move_id += 1
    if self.chessboard is None:
      self.chessboard = next(self.pgns)
      self.game_id += 1
      self.move_id = 0

  def draw_board(self):
    move = self.chessboard.move
    fill = {move.from_square: FILL_COLOR, move.to_square: FILL_COLOR} if move else {}
    board_svg = chess.svg.board(board=self.chessboard.board(), fill=fill, size=510)
    drawing = svg2rlg(io.StringIO(board_svg))
    imgdata = io.BytesIO()
    renderPM.drawToFile(drawing, imgdata, fmt='png')
    imgdata.seek(0)
    self.board_photo = tk.PhotoImage(data=imgdata.read())
    self.canvas.create_image(0, 0, anchor='nw', image=self.board_photo)

  def click(self, event):
    self.hand_photo_id = -1
    self.take_move_snapshots()
    self.hand_photo_id = 0

    self.next_move()
    self.draw_board()

  def take_move_snapshots(self):
    for i, angles in enumerate(PHOTO_ANGLES):
      self.arm.set_servo_angle(servo_id=None, angle=angles, speed=100, mvacc=180, is_radian=False, wait=True)
      time.sleep(0.2)
      image = cam.get_image()
      pygame.image.save(image, data_dir / f'positions/{self.game_id:03d}-{self.move_id:03d}-{i}.jpg')

  def take_hand_snapshots(self):
    while True:
      image = cam.get_image()
      if self.hand_photo_id != -1:
        pygame.image.save(image, data_dir / f'hands/{self.game_id:03d}-{self.move_id-1:03d}-{self.hand_photo_id}.jpg')
        self.hand_photo_id += 1
      time.sleep(0.5)


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
  (data_dir / 'hands').mkdir(exist_ok=True)

  pgns = read_pgns(data_dir / '2022.pgn')
  root = tk.Tk()
  ChessGui(root, pgns, arm, cam, data_dir)
  root.mainloop()
