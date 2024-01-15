#!/usr/bin/env python3
import io
import chess
import chess.pgn
import chess.svg
import chess.engine
import tkinter as tk
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def read_pgns(pgn_fn):
  game = []

  with open(pgn_fn) as f:
    for line in f:
      game.append(line)
      if line.startswith('1.'):
        yield chess.pgn.read_game(io.StringIO(''.join(game)))
        game = []


class ChessGui(tk.Frame):
  def __init__(self, parent, pgns, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.pgns = pgns
    self.grid()
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
    if self.chessboard is None:
      self.chessboard = next(pgns)
    self.draw_board()


if __name__ == "__main__":
  pgns = read_pgns(Path(__file__).parent / 'data/2022.pgn')
  root = tk.Tk()
  ChessGui(root, pgns)
  root.mainloop()

