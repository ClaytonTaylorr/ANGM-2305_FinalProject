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

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    # This is the location on the sprite sheet for each block, 0 is top left 96 pixels over the 2nd block starts, if need lower position modify "y" position
    rect = pygame.Rect(272, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    # using this line we can replace each directory with the location of the sprite sheet files
    #SPRITES = load_sprite_sheets(dir1, dir2, width, height)
    SPRITES = load_sprite_sheets("MainCharacter", "BlueAlien", 32, 32, True)
    # animation delay so the sprites arent cycled through so fast, lower = faster
    ANIMATION_DELAY = 3

    def __init__(self,x , y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x,y, width, height)
        # how fast player goes in said direction
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    # subtracting by the gravity moves up since gravity is tied to a negative y velocity and the value 8 is how high I want. 
    # Gravity is always active so after the intiial jump, the player should go down immediately
    def jump(self):
        self.y_vel = -self.GRAVITY * 5
        self.animation_count = 0
        self.jump_count += 1
     # a 2nd jump clears the accumulated gravity so that you can make perform a double-jump.
        if self.jump_count == 1:
            self.fall_count = 0

    
    def move (self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

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

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    # need to stop gravity once collision is made/player lands so the gravity value doesnt keep adding up. Also reset velocity to zero
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    # switch velocity once collision with the "bottom" of a piece of geometry is hit so gravity starts
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        # default sprite if no velocity is idle
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        # sprite delayed conected to the length of the sprite sheets themselves, to show each sprite in a timely manner
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

        # reset player position after falling
    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.jump_count = 0
        self.fall_count = 0

    def update(self):
        # creating the collision box, constantly being updated by the size of the sprite its self
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # collision based off the pixels them selves on the spritesheet and not a full sized box
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

# Generic object class for every other sprite thats not the player, defining width and heigth and location, etc for other classes
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

# An object that is "fire" but can be used and iterated on to make other traps for the player
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name + "_right"]
        # sprite delayed conected to the length of the sprite sheets themselves, to show each sprite in a timely manner
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        # reset animation count instead of infinitely building up and up
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

# coin collectible class
class Collectible(Object):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height, name="coin")
        sprite = pygame.image.load(join("assets", "Items", image)).convert_alpha()
        sprite = pygame.transform.scale(sprite, (width, height))
        self.image.blit(sprite, (0, 0))
        # you can keep the mask around if you want—but it won't be used here
        self.mask = pygame.mask.from_surface(self.image)

    def collect(self, player):
        # simple rect-based overlap
        return self.rect.colliderect(player.rect)

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

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    # make sure to update the display so images dont stay rendered off screen, slowing the game down. Learned that in the matrix screensaver project
    pygame.display.update()

# Simple collision block calling on the object class again including player and "geometry" using the mask if 
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                # using ".top" as the collision to the geometry objects and " .bottom" for bottom of objects
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)  # Only move horizontally
    player.update()  # Update player position and mask
    collided_object = None

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)  # Move back to original position after checking collision

    return collided_object  # Return the collided object (if any)

def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    player.x_vel = 0

    # First, handle horizontal movement and check for horizontal collisions
    collide_left = collide(player, objects, -PLAYER_VEL)
    collide_right = collide(player, objects, PLAYER_VEL)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


    # Now handle vertical collisions after horizontal movement
    player.move(0, player.y_vel)
    handle_vertical_collision(player, objects, player.y_vel)
    player.update()

def reload_player_if_needed(player, floor_height):
    # Check if the player falls below the floor terrain
    if player.rect.bottom > HEIGHT:  # If player goes below the floor
        # Reset the player's position to a start
        player.rect.x = 10
        player.rect.y = 100
        player.y_vel = 0
        player.fall_count = 0
        player.jump_count = 0
        print("Player has fallen below the floor and has been reset.")

def main(window):
    clock = pygame.time.Clock()

    pygame.font.init()
    win_font = pygame.font.SysFont(None, 72)
    score = 0
    score_font = pygame.font.SysFont(None, 36)
    
    background, bg_image = get_background("Blue.png")

    block_size = 96
    floor_range_start = -10
    floor_range_end = 50

    # Player spawn position
    spawn_x, spawn_y = block_size + 10, 100
    win_font = pygame.font.SysFont(None, 72)
    player = Player(spawn_x, spawn_y, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    floor = []
    i = floor_range_start

    while i < floor_range_end:
        if random.random() < 0.15:
            hole_width = random.randint(1, 3)

            if hole_width == 3:
                # Add a "bridge" block in the middle of the 3 block wide hole
                bridge_x = (i + 1) * block_size
                bridge_y = HEIGHT - block_size - block_size
                floor.append(Block(bridge_x, bridge_y, block_size))

            i += hole_width
        else:
            x = i * block_size
            y = HEIGHT - block_size
            floor.append(Block(x, y, block_size))
            i += 1
    first_block = next(
        (b for b in floor 
         if b.rect.x == 0 and b.rect.y == HEIGHT - block_size), None)
    if first_block:
        # how tall the column should be
        stack_height = 8  
        for n in range(1, stack_height + 1):
            new_x = first_block.rect.x
            new_y = first_block.rect.y - n * block_size
            floor.append(Block(new_x, new_y, block_size))


    # Other level objects (for testing)
    objects = [*floor,
               Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               fire]
    
    # spawn coins
    coin_size = 32
    num_coins = 6
    collectibles = []

    for _ in range(num_coins):
        # keep picking x, y until it's free of any floor block
        while True:
            x = random.randint(0, floor_range_end * block_size)
            y = random.randint(HEIGHT // 2, HEIGHT - coin_size - 10)
            test_rect = pygame.Rect(x, y, coin_size, coin_size)

            # check against every floor block
            collision = False
            for block in floor:
                if test_rect.colliderect(block.rect):
                    collision = True
                    break

            if not collision:
                break

        coin = Collectible(x, y, coin_size, coin_size, "Coin.png")
        collectibles.append(coin)
        objects.append(coin)

    offset_x = 0  # Initial camera position
    scroll_area_width = 400

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                # Add this line to reset player and camera on 'R' key press
                if event.key == pygame.K_r:
                    # Reset the player to the spawn position
                    player.reset(spawn_x, spawn_y)  
                    # Reset the camera to its starting position
                    offset_x = 0  

        for coin in collectibles[:]:
            if coin.collect(player):
                collectibles.remove(coin)
                objects.remove(coin)
                #adds to the score
                score += 1


        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        # draw coin counter
        score_surf = score_font.render(f"Coins collected: {score}", True, (255,255,255))
        window.blit(score_surf, (10, 10))
        pygame.display.update()

        # show “You Win!” when all coins are collected
        if score == num_coins:
            text_surf = win_font.render("You Win!", True, (255,255,255))
            text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            window.blit(text_surf, text_rect)
            pygame.display.update()
            pygame.time.delay(3000)
            run = False

        # Screen scrolling
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        # Check if the player has fallen below the floor
        if player.rect.bottom > HEIGHT:
            player.reset(spawn_x, spawn_y)  # Reset the player to the spawn position
            offset_x = 0  # Reset the camera to the starting position

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)
