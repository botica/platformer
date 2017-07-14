# inertia, scrolling offset effect

import os, sys
import pygame
from pygame.locals import *
import pyganim

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

WINDOWWIDTH = 750
WINDOWHEIGHT = 500

FPS = 60
MOVESPEED = 15
GRAVITY = .5
JUMPHEIGHT = -10 # lower is higher jump arc


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        running = load_image('11.png')
        standing = load_image('22.png')

        self.anim_obj = pyganim.PygAnimation([(standing, 1), (running, 1)])

        self.image = standing
        self.rect = self.image.get_rect()

        self.rect.x = WINDOWWIDTH/2 - self.image.get_width()/2
        self.rect.y = WINDOWHEIGHT - self.image.get_height() - 5

        self.direction = 0

        self.jumping = False
        self.grav = GRAVITY
        self.yvel = 0
        self.falling = False

    def move(self, dx, dy):
        if dx != 0:
            self.move_single_axis(dx, 0)
            if dx < 0:
                if self.direction != 1:
                    self.anim_obj.flip(1,0)
                    self.direction = 1
            else:
                if self.direction != 0:
                    self.anim_obj.flip(1,0)
                    self.direction = 0
        if dy != 0:
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect): # dont do x axis collision dectection for just platforms, not bounding walls
                if dx > 0: # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0: # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                if dy > 0: # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                if dy < 0: # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.rect.bottom

    def is_running(self):
        pressed = pygame.key.get_pressed()
        if (pressed[K_LEFT] or pressed[K_RIGHT]):
            return True
        else:
            return False

    def on_ground(self):
        for platform in platforms:
            if self.rect.bottom == platform.rect.y:
                if self.rect.x == platform.rect.x or self.rect.bottomright[0] == platform.rect.x:
                    return True
        return False

    def get_vel(self):
        return self.yvel

    def apply_vel(self):
        self.yvel += self.grav
        self.rect.y += self.yvel

    def is_jumping(self):
        return self.jumping

    def jump(self):
        if not self.is_jumping():
            self.jumping = True
            self.yvel = JUMPHEIGHT

    def jump_update(self):
        if self.is_jumping():
            self.apply_vel()
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    self.rect.top = wall.rect.bottom
                    self.yvel = 0
            if self.get_vel() >= 0:
                self.jumping = False
                self.falling = True

    def is_falling(self):
        return self.falling

    def fall(self):
        if not self.is_falling():
            self.falling = True
            self.yvel = 0

    def fall_update(self):
        if self.is_falling():
            self.apply_vel()
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.rect.bottom <= platform.rect.bottom:
                        self.rect.bottom = platform.rect.top
                        self.falling = False

    def update_animation(self):
        if self.is_running():
            self.anim_obj.play()
        else:
            self.anim_obj.pause()
            if self.anim_obj.getCurrentFrame() != self.anim_obj.getFrame(0):
                self.anim_obj.prevFrame()

    def update(self):
        self.jump_update()
        self.fall_update()
        self.update_animation()


class Wall(object):
    
    def __init__(self, pos):
        self.rect = pygame.Rect(pos[0], pos[1], 15, 15) #width/height


#Initialize Everything
pygame.init()
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('get it')

#Create The Backgound
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250)) # white

clock = pygame.time.Clock()
walls = []
platforms = []

# create the walls

for i in range(0, WINDOWHEIGHT):
    a = Wall((0, i))
    walls.append(a)
    b = Wall(((WINDOWWIDTH - 5), i))
    walls.append(b)
for i in range(0, WINDOWWIDTH):
    c = Wall((i, 0))
    walls.append(c)
    d = Wall((i, (WINDOWHEIGHT - 5)))
    #walls.append(d)
    platforms.append(d) # floor

for i in range(0, WINDOWWIDTH/4):
    p = Wall((i, 400))
    platforms.append(p) # platform on left 400 px down

for i in range(WINDOWWIDTH/2, WINDOWWIDTH):
    p = Wall((i, 300))
    platforms.append(p) # platform on right 300 px down

for i in range(0, WINDOWWIDTH/4):
    p = Wall((i, 200))
    platforms.append(p) # platform on left 200 px down

#create sprite
player = Player()

#game loop
while 1:
    clock.tick(FPS)

    # loop through input events
    for event in pygame.event.get():
        if event.type == QUIT:
            raise SystemExit # quit

    pressed = pygame.key.get_pressed()

    if pressed[K_LEFT]:
        player.move(-MOVESPEED, 0)
    if pressed[K_RIGHT]:
        player.move(MOVESPEED, 0)

    if pressed[K_UP]:
        if player.on_ground():
            player.jump()

    if (not player.on_ground()) and (not player.is_jumping()):
        player.fall()

    # update the state of the sprite
    player.update()

    # draw it all
    screen.blit(background, (0, 0))

    for platform in platforms:
        pygame.draw.rect(screen, (0, 255, 0), platform.rect)

    for wall in walls:
        pygame.draw.rect(screen, (0, 0, 255), wall.rect)

    player.anim_obj.blit(screen, player.rect)

    pygame.display.update()
