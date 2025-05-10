import os
import random
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()


pygame.display.set_caption("ANGM 2305 Final - Sidescrolling Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

# 
class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)

    def __init__(self,x , y, width, height):
        self.rect = pygame.Rect(x,y, width, height)
        # how fast player goes in said direction
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
    
    def move (self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    # negative to velocity since coordinated work from left to right
    def move_left(self, vel):
        self.x_vel = -vel

    def move_right(self, vel):
        self.x_vel = vel


# calls for the background, first letting pygame know im using the assets folde and the background folde inside
# using intigers to tile the images by multiplying its position, top left corner, to its height & width to move said tile
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))

    # scale inward for 16x16 pixel art, may rid of later
    scale_factor = 4
    image = pygame.transform.scale(image, (16 * scale_factor, 16 * scale_factor))

    _, _, width, height, = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)
# make sure to update the display so images dont stay rendered off screen, slowing the game down. Learned that in the matrix screensaver project
    pygame.display.update()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        draw(window, background, bg_image)
    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)