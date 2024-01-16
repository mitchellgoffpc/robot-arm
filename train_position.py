import cv2
import chess
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from PIL import Image
from pathlib import Path

from models import PositionModel
from helpers import read_pgns

COLORS = [chess.WHITE, chess.BLACK]
PIECES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]

PIECE_NUMBERS = {
  (color, piece): i*6+j+1
  for i, color in enumerate(COLORS)
  for j, piece in enumerate(PIECES)}

def get_board_state(board):
  board_state = np.zeros((8, 8), dtype=int)
  for square, piece in board.piece_map().items():
    board_state[square // 8, square % 8] = PIECE_NUMBERS[piece.color, piece.piece_type]
  return board_state


class PositionDataset(Dataset):
  def __init__(self, train=True, transform=None):
    games_to_pick = [1, 2] if train else [0]
    self.transform = transform or lambda x: x
    self.data_dir = Path(__file__).parent / 'data/positions'
    self.image_names = sorted(set(x.name.rsplit('-', 1)[0] for x in self.data_dir.iterdir() if x.name.endswith('.jpg')))
    self.image_names = [x for x in self.image_names if any(x.startswith(f'{game:03d}-') for game in games_to_pick)]

    self.games = {i: [] for i in range(10)}
    for i, game in enumerate(read_pgns(self.data_dir.parent / '2022.pgn')):
      if i >= len(self.games): break
      while game is not None:
        self.games[i].append(game.board())
        game = game.next()

  def __len__(self):
    return len(self.image_names)

  def __getitem__(self, idx):
    image1 = Image.open(self.data_dir / f'{self.image_names[idx]}-0.jpg')
    image2 = Image.open(self.data_dir / f'{self.image_names[idx]}-1.jpg')
    image1 = np.array(self.transform(image1))
    image2 = np.array(self.transform(image2))
    image1 = cv2.resize(image1[:400, 50:-50], (256, 256))
    image2 = cv2.resize(image2[10:-50, 100:-40], (256, 256))

    game_idx, move_idx = self.image_names[idx].split('-')
    board = self.games[int(game_idx)][int(move_idx)]
    return image1, image2, get_board_state(board).flatten()


def train():
  transform = T.Compose([
    T.ColorJitter(1, 1),
    T.GaussianBlur(11),
  ])

  train_dataset = PositionDataset(train=True, transform=transform)
  test_dataset = PositionDataset(train=False, transform=None)
  train_dataloader = DataLoader(train_dataset, batch_size=16, num_workers=0, shuffle=True)
  test_dataloader = DataLoader(test_dataset, batch_size=16, num_workers=0)

  device = (
    torch.device('cuda') if torch.cuda.is_available() else
    torch.device('mps') if torch.backends.mps.is_available() else
    torch.device('cpu'))

  model = PositionModel(output_size=64 * 13).to(device)
  optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)

  for epoch in range(10):
    train_loss, total = 0, 0
    for image1, image2, labels in (pbar := tqdm(train_dataloader)):
      preds = model(image1, image2)
      loss = F.cross_entropy(preds, labels.to(device))
      loss.backward()
      optimizer.step()
      optimizer.zero_grad()
      train_loss += loss.item()
      total += 1
      pbar.set_description(f"Train loss: {train_loss / total:.3f}")

    test_loss, total = 0, 0
    for image1, image2, labels in (pbar := tqdm(test_dataloader)):
      with torch.no_grad():
        preds = model(image1, image2)
      test_loss += F.cross_entropy(preds, labels.to(device)).item()
      total += 1
      pbar.set_description(f"Test loss: {test_loss / total:.3f}")


if __name__ == '__main__':
  train()
