import pygame
import pygame.camera

WEBCAM_NAME = 'Logitech Webcam C930e'

pygame.camera.init()
camlist = pygame.camera.list_cameras()
if WEBCAM_NAME not in camlist:
  raise RuntimeError("No camera on current device")
print(camlist)

cam = pygame.camera.Camera(WEBCAM_NAME, (640, 480))
cam.start()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Webcam')
pygame.display.flip()

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  image = cam.get_image()
  screen.blit(image, (0, 0))
  pygame.display.flip()
