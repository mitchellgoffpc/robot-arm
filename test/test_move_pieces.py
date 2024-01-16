import io
import time
import chess
import chess.pgn
import numpy as np
import ev3_dc as ev3
from xarm.wrapper import XArmAPI

A1 = np.array([444, -164, 385, -125.614064, 6.815906, -122])
H1 = np.array([444, 137, 385, -125.614064, 6.815906, -122])
H8 = np.array([146, 137, 385, -125.614064, 6.815906, -122])
A8 = np.array([146, -164, 385, -125.614064, 6.815906, -122])
CENTER = np.array([288, 0, 385, -125.614064, 6.815906, -122])
SIDE = np.array([378, -246, 363, -125.614064, 6.815906, -122])
DOWN = np.array([0, 0, -100, 0, 0, 0])
MVACC = 180
MOVE_SPEED = 100
DOWN_SPEED = 50
PIECE_HEIGHTS = {
  chess.KING: np.array([0, 0, 20, 0, 0, 0]),
  chess.QUEEN: np.array([0, 0, 20, 0, 0, 0])}

POSITIONS = np.zeros((8, 8, 6))
for i in range(8):
  for j in range(8):
    POSITIONS[i, j, 0] = A1[0] + ((A8[0] - A1[0]) * j / 7)
    POSITIONS[i, j, 1] = A1[1] + ((H1[1] - A1[1]) * i / 7)
    POSITIONS[i, j, 2:] = A1[2:]

# set up arm
arm = XArmAPI('192.168.1.170')

# set up ev6
motor = ev3.Motor(protocol=ev3.USB, port=ev3.PORT_A)
motor.move_for(0.5, speed=20, direction=-1).start()
time.sleep(0.5)
closed = motor.position
open = motor.position + 35

current_pos = CENTER
threshold = A8[0] + (A1[0] - A8[0]) / 4

def perform_move(from_square, to_square, piece_type):
  global current_pos
  pos = from_square
  if current_pos[0] < threshold and pos[0] < threshold and np.sign(current_pos[1]) != np.sign(pos[1]):
    arm.set_position_aa(CENTER.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa(pos.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa((pos + DOWN + PIECE_HEIGHTS.get(piece_type, 0)).tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
  motor.move_for(duration=0.5, speed=20, direction=-1, brake=True).start()
  time.sleep(0.5)
  arm.set_position_aa(pos.tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
  current_pos = pos

  pos = to_square
  if current_pos[0] < threshold and pos[0] < threshold and np.sign(current_pos[1]) != np.sign(pos[1]):
    arm.set_position_aa(CENTER.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa(pos.tolist(), speed=MOVE_SPEED, mvacc=MVACC, wait=True)
  arm.set_position_aa((pos + DOWN + PIECE_HEIGHTS.get(piece_type, 0)).tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
  motor.move_to(position=open, speed=20, brake=True).start()
  time.sleep(0.5)
  arm.set_position_aa(pos.tolist(), speed=DOWN_SPEED, mvacc=MVACC, wait=True)
  current_pos = pos


game1 = """
[Event "FICS rated standard game"]
[Site "FICS freechess.org"]
[FICSGamesDBGameNo "530000657"]
[White "IFDStock"]
[Black "Aromas"]
[WhiteElo "2526"]
[BlackElo "1979"]
[WhiteRD "51.5"]
[BlackRD "25.0"]
[WhiteIsComp "Yes"]
[TimeControl "900+0"]
[Date "2022.12.31"]
[Time "22:03:00"]
[WhiteClock "0:15:00.000"]
[BlackClock "0:15:00.000"]
[ECO "A00"]
[PlyCount "41"]
[Result "1-0"]

1. d3 d5 2. Bd2 e5 3. g3 Nc6 4. Bg2 Nf6 5. Nc3 Be7 6. e4 d4 7. Nd5 Be6 8. Nxe7 Qxe7 9. Nf3 O-O 10. O-O h6 11. Ne1 Ng4 12. h3 Nf6 13. f4 exf4 14. gxf4 Ne8 15. f5 Bd7 16. Qg4 Ne5 17. Qg3 Kh8 18. Bf4 Nc6 19. Nf3 Nf6 20. Bxc7 Rac8 21. Bd6 {Black resigns} 1-0
"""

game2 = """
[Event "FICS rated blitz game"]
[Site "FICS freechess.org"]
[FICSGamesDBGameNo "530000656"]
[White "exeComp"]
[Black "slaran"]
[WhiteElo "2509"]
[BlackElo "1593"]
[WhiteRD "93.8"]
[BlackRD "47.6"]
[WhiteIsComp "Yes"]
[TimeControl "120+12"]
[Date "2022.12.31"]
[Time "21:56:00"]
[WhiteClock "0:02:00.000"]
[BlackClock "0:02:00.000"]
[ECO "A56"]
[PlyCount "29"]
[Result "1-0"]

1. d4 c5 2. d5 d6 3. e4 g6 4. c4 Bg7 5. Bd3 Nf6 6. Nc3 O-O 7. Bg5 Bg4 8. Qd2 Bc8 9. f4 Nbd7 10. Nf3 a6 11. a4 Qe8 12. O-O h5 13. Rae1 Nh7 14. Bh4 Ndf6 15. e5 {Black forfeits on time} 1-0
"""

game3 = """
[Event "FICS rated standard game"]
[Site "FICS freechess.org"]
[FICSGamesDBGameNo "530000072"]
[White "damouno"]
[Black "Aromas"]
[WhiteElo "2212"]
[BlackElo "1995"]
[WhiteRD "42.2"]
[BlackRD "25.1"]
[TimeControl "900+0"]
[Date "2022.12.31"]
[Time "19:19:00"]
[WhiteClock "0:15:00.000"]
[BlackClock "0:15:00.000"]
[ECO "A03"]
[PlyCount "29"]
[Result "1-0"]

1. f4 d5 2. Nf3 c5 3. e3 Nc6 4. Bb5 Bd7 5. b3 a6 6. Bxc6 Bxc6 7. Bb2 Nf6 8. O-O e6 9. Ne5 Qc7 10. d3 Bd6 11. Nd2 Nd7 12. Qh5 g6 13. Qf3 O-O 14. Ng4 f5 15. Nh6# {Black checkmated} 1-0
"""

def get_rank_file(square):
  return chess.square_file(square), chess.square_rank(square)
def get_position(square):
  return POSITIONS[get_rank_file(square)]

game = chess.pgn.read_game(io.StringIO(game3.strip()))
board = game.board()

while game:
  if (move := game.move):
    # handle captures
    if move.to_square in board.piece_map():
      perform_move(get_position(move.to_square), SIDE, board.piece_map()[move.to_square].piece_type)
      SIDE[0] -= 50

    # handle move
    perform_move(get_position(move.from_square), get_position(move.to_square), board.piece_map()[move.from_square].piece_type)

    # handle castling
    if board.piece_map()[move.from_square].piece_type is chess.KING:
      if (move.from_square, move.to_square) == (chess.E1, chess.G1):
        perform_move(get_position(chess.H1), get_position(chess.F1), chess.ROOK)
      elif (move.from_square, move.to_square) == (chess.E1, chess.C1):
        perform_move(get_position(chess.A1), get_position(chess.D1), chess.ROOK)
      elif (move.from_square, move.to_square) == (chess.E8, chess.G8):
        perform_move(get_position(chess.H8), get_position(chess.F8), chess.ROOK)
      elif (move.from_square, move.to_square) == (chess.E8, chess.C8):
        perform_move(get_position(chess.A8), get_position(chess.D8), chess.ROOK)

  board = game.board()
  game = game.next()
