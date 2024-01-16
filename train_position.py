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
  def __init__(self, transform):
    self.transform = transform
    self.data_dir = Path(__file__).parent / 'data/positions'
    self.image_names = sorted(set(x.name.rsplit('-', 1)[0] for x in self.data_dir.iterdir() if x.name.endswith('.jpg')))

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

  dataset = PositionDataset(transform)
  dataloader = DataLoader(dataset, batch_size=32)

  # import matplotlib.pyplot as plt
  # for i, (image1, image2, label) in enumerate(dataset):
  #   if i >= 3: break
  #   _, ax = plt.subplots(1, 2, figsize=(12, 6))
  #   ax[0].imshow(image1)
  #   ax[1].imshow(image2)
  #   plt.show()
  # exit()

  device = torch.device('cpu')
  model = PositionModel(output_size=64 * 13)
  optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)

  for epoch in range(10):
    for image1, image2, labels in tqdm(dataloader):
      preds = model(image1, image2)
      loss = F.cross_entropy(preds, labels)
      loss.backward()
      optimizer.step()
      optimizer.zero_grad()


if __name__ == '__main__':
  train()
