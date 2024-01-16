import io
import chess
import chess.pgn

def read_pgns(pgn_fn):
  game = []

  with open(pgn_fn) as f:
    for line in f:
      game.append(line)
      if line.startswith('1.'):
        yield chess.pgn.read_game(io.StringIO(''.join(game)))
        game = []
