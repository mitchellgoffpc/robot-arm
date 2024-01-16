import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

INPUT_SIZE = (240, 256, 3)

class PositionModel(nn.Module):
  def __init__(self, output_size):
    super().__init__()
    resnet = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.DEFAULT)
    self.backbone = torch.nn.Sequential(*list(resnet.children())[1:-2])
    self.conv1 = nn.Conv2d(6, 64, kernel_size=7, stride=2, padding=3, bias=False)
    self.conv2 = nn.Conv2d(512, 16, kernel_size=1, bias=False)
    self.fc1 = nn.Linear(16*8*8, 128)
    self.fc2 = nn.Linear(128, output_size)

  def forward(self, img1, img2):
    b,h,w,c = img1.shape
    device = self.fc1.weight.device
    img1 = torch.as_tensor(img1).permute(0,3,1,2).contiguous().float().to(device)
    img2 = torch.as_tensor(img2).permute(0,3,1,2).contiguous().float().to(device)
    x = torch.cat([img1, img2], dim=1) / 255
    x = self.conv1(x)
    x = self.backbone(x)
    x = self.conv2(x)
    x = x.flatten(start_dim=1)  # No relu for now
    x = F.relu(self.fc1(x))
    x = self.fc2(x)
    return x.view(-1, 13, 8*8)
