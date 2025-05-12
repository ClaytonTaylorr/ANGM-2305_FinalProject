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

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False)for sprite in sprites]

# load all files(sprite sheets) in the directory for the block to use to display
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        # Selecting only the individual frames out of the sprite sheets by multiplying by its width
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            # Need to rid of the scale from earlier since scaling will be done here now
            sprites.append(pygame.transform.scale2x(surface))
        # Flips the sprite sheet for when changing character direction
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "") + "_right"] = sprites

    return all_sprites

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    # using this line we can replace each directory with the location of the sprite sheet files
    #SPRITES = load_sprite_sheets(dir1, dir2, width, height)
    SPRITES = load_sprite_sheets("MainCharacter", "BlueAlien", 32, 32, True)
    # animation delay so the sprites arent cycled through so fast, lower = faster
    ANIMATION_DELAY = 3

    def __init__(self,x , y, width, height):
        self.rect = pygame.Rect(x,y, width, height)
        # how fast player goes in said direction
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
    
    def move (self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    # negative to velocity since coordinated work from left to right
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # define loop to update the movement per iteration of the loop/per frame
    # adding gravity and velocity/acceleration to the gravity
    def loop(self, fps):
        # fall a minimum of 1 pixel a second at base
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        # default sprite if no velocity is idle
        sprite_sheet = "idle"
        if self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        # sprite delayed conected to the length of the sprite sheets themselves, to show each sprite in a timely manner
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def update():
        # creating the collision box, constantly being updated by the size of the sprite its self
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # collision based off the pixels them selves on the spritesheet and not a full sized box
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))


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

def draw(window, background, bg_image, player):
    for tile in background:
        window.blit(bg_image, tile)

    player.draw(window)

    # make sure to update the display so images dont stay rendered off screen, slowing the game down. Learned that in the matrix screensaver project
    pygame.display.update()

def handle_move(player):
    keys = pygame.key.get_pressed()
    # set player movement to zero so that they only move when key is pressed
    player.x_vel = 0
    if keys [pygame.K_LEFT]:
        player.move_left(PLAYER_VEL)
    if keys [pygame.K_RIGHT]:
        player.move_right(PLAYER_VEL)

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    player = Player(100,100,50,50)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # call loop def from above to allow player to move
        player.loop(FPS)
        # call the keybinds def to actually move said character
        handle_move(player)
        draw(window, background, bg_image, player)
    
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)