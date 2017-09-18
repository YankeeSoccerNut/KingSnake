# Start with a basic snake game....thanks Gareth Rees!
# In our version beer is equivalent to food
#
from collections import deque
import pygame
from pygame.sprite import Sprite
from random import randrange
import sys
from pygame.locals import *


class Vector(tuple):
    """A tuple that supports some vector operations.

    >>> v, w = Vector((1, 2)), Vector((3, 4))
    >>> v + w, w - v, v * 10, 100 * v, -v
    ((4, 6), (2, 2), (10, 20), (100, 200), (-1, -2))
    """

    def __add__(self, other): return Vector(v + w for v, w in zip(self, other))

    def __radd__(self, other): return Vector(
        w + v for v, w in zip(self, other))

    def __sub__(self, other): return Vector(v - w for v, w in zip(self, other))

    def __rsub__(self, other): return Vector(
        w - v for v, w in zip(self, other))

    def __mul__(self, s): return Vector(v * s for v in self)

    def __rmul__(self, s): return Vector(v * s for v in self)

    def __neg__(self): return -1 * self


FPS = 60                        # Game frames per second
SEGMENT_SCORE = 50              # Score per segment

SNAKE_SPEED_INITIAL = 4.0       # Initial snake speed (squares per second)
SNAKE_SPEED_INCREMENT = 0.25    # Snake speeds up this much each time it grows
SNAKE_START_LENGTH = 1          # Initial snake length in segments

WORLD_SIZE = Vector((20, 20))   # World size, in blocks
BLOCK_SIZE = 24                 # Block size, in pixels

BACKGROUND_COLOR = 45, 45, 45
SNAKE_COLOR = 0, 255, 0
FOOD_COLOR = 255, 0, 0
DEATH_COLOR = 255, 0, 0
TEXT_COLOR = 255, 255, 255

DIRECTION_UP = Vector((0, -1))
DIRECTION_DOWN = Vector((0,  1))
DIRECTION_LEFT = Vector((-1,  0))
DIRECTION_RIGHT = Vector((1,  0))
DIRECTION_DR = DIRECTION_DOWN + DIRECTION_RIGHT

# Map from PyGame key event to the corresponding direction.
KEY_DIRECTION = {
    K_w: DIRECTION_UP,    K_UP:    DIRECTION_UP,
    K_s: DIRECTION_DOWN,  K_DOWN:  DIRECTION_DOWN,
    K_a: DIRECTION_LEFT,  K_LEFT:  DIRECTION_LEFT,
    K_d: DIRECTION_RIGHT, K_RIGHT: DIRECTION_RIGHT,
}


class Snake(Sprite):
    # Snake implemented using "Double Ended Queue - deque"
    def __init__(self, start, start_length):
        self.speed = SNAKE_SPEED_INITIAL  # Speed in squares per second.
        self.timer = 1.0 / self.speed    # Time remaining to next movement.
        self.growth_pending = 0          # Number of segments still to grow.
        self.direction = DIRECTION_UP    # Current movement direction.
        self.segments = deque([start - self.direction * i
                               for i in xrange(start_length)])

    def __iter__(self):
        return iter(self.segments)

    def __len__(self):
        return len(self.segments)

    def change_direction(self, direction):
        """Update the direction of the snake."""
        # Moving in the opposite direction of current movement is not allowed.
        if self.direction != -direction:
            self.direction = direction

    def head(self):
        """Return the position of the snake's head."""
        return self.segments[0]

    def update(self, dt, direction):
        """Update the snake by dt seconds and possibly set direction."""
        self.timer -= dt
        if self.timer > 0:
            # Nothing to do yet.
            return
        # Moving in the opposite direction of current movement is not allowed.
        if self.direction != -direction:
            self.direction = direction
        self.timer += 1 / self.speed
        # Add a new head.
        self.segments.appendleft(self.head() + self.direction)
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            # Remove tail.
            self.segments.pop()

    def grow(self):
        """Grow snake by one segment and speed up."""
        self.growth_pending += 1
        self.speed += SNAKE_SPEED_INCREMENT

    def self_intersecting(self):
        """Is the snake currently self-intersecting?"""
        it = iter(self)
        head = next(it)
        return head in it


class SnakeGame(object):
    def __init__(self):
        pygame.display.set_caption('PyGame Snake')
        self.block_size = BLOCK_SIZE
        self.window = pygame.display.set_mode(WORLD_SIZE * self.block_size)
        self.screen = pygame.display.get_surface()

        self.head_image = pygame.image.load("./images/Bobble_Dale.png")
        self.segment_image = pygame.image.load("./images/crushed_can2.png")
        self.food_image = pygame.image.load("./images/Alamo_can.png")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.world = Rect((0, 0), WORLD_SIZE)
        self.reset()

    def reset(self):
        """Start a new game."""
        self.playing = True
        self.next_direction = DIRECTION_UP
        self.score = 0
        self.snake = Snake(self.world.center, SNAKE_START_LENGTH)
        self.food = set()
        self.spread_food(1)
        #self.add_food()

    def add_food(self):
        """Ensure that there is at least one piece of food.
        (And, with small probability, more than one.)
        """
        while not (self.food and randrange(4)):
            food = Vector(map(randrange, self.world.bottomright))
            if food not in self.food and food not in self.snake:
                self.food.add(food)

    def spread_food(self, numfood):
        # Our version of the game distributes a set number of food items for our characters to clear before they can level up

        for i in range (0, numfood):
            food = Vector(map(randrange, self.world.bottomright))
            if food not in self.food and food not in self.snake:
                self.food.add(food)

    def input(self, e):
        """Process keyboard event e."""
        if e.key in KEY_DIRECTION:
            self.next_direction = KEY_DIRECTION[e.key]
        elif e.key == K_SPACE and not self.playing:
            self.reset()

    def update(self, dt):
        """Update the game by dt seconds."""
        self.snake.update(dt, self.next_direction)

        # # If snake hits a food block, then consume the food, add new
        # # food and grow the snake.
        # head = self.snake.head()
        # if head in self.food:
        #     self.food.remove(head)
        #     self.add_food()
        #     self.snake.grow()
        #     self.score += len(self.snake) * SEGMENT_SCORE

        # If our snake hits a food block, just consume it and grow...could be a good place to introduce random "bonus" object

        head = self.snake.head()
        if head in self.food:
            self.food.remove(head)
            self.snake.grow()
            self.score += len(self.snake) * SEGMENT_SCORE

        #if no more food then we cleared the screen!
        if (bool(self.food) == False):  #  No more food!
            print "You cleared the screen"
            pygame.quit()


        # If snake collides with self or the screen boundaries, then
        # it's game over.
        if self.snake.self_intersecting() or not self.world.collidepoint(self.snake.head()):
            self.playing = False

    def block(self, p):
        """Return the screen rectangle corresponding to the position p."""
        return Rect(p * self.block_size, DIRECTION_DR * self.block_size)

    def draw_text(self, text, p):
        """Draw text at position p."""
        self.screen.blit(self.font.render(text, 1, TEXT_COLOR), p)

    def draw(self):
        # SLA - modified to use loaded images instead of simple blocks
        """Draw game (while playing)."""
        self.screen.fill(BACKGROUND_COLOR)
        # always draw the head then "fill the other segments"
        # self.screen.blit(self.snake.head_image, self.block(0))

        for i, p in enumerate(self.snake):
            if i == 0:  # it's the head, use our image
                self.screen.blit(self.head_image, self.block(p))
            else:  # it's a segment, use our image
                self.screen.blit(self.segment_image, self.block(p))
                #pygame.draw.rect(self.screen, SNAKE_COLOR, self.block(p))

        # Note:  at this point i and p are at the tail...

        for f in self.food:
        #    pygame.draw.rect(self.screen, FOOD_COLOR, self.block(f))
            self.screen.blit(self.food_image, self.block(f))

        self.draw_text("Score: {}".format(self.score), (20, 20))

    def draw_death(self):
        """Draw game (after game over)."""
        self.screen.fill(DEATH_COLOR)
        self.draw_text("Game over! Press Space to start a new game", (20, 150))
        self.draw_text("Your score is: {}".format(self.score), (140, 180))

    def play(self):
        """Play game until the QUIT event is received."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0  # convert to seconds
            for e in pygame.event.get():
                if e.type == QUIT:
                    return
                elif e.type == KEYUP:
                    self.input(e)
            if self.playing:
                self.update(dt)
                self.draw()
            else:
                self.draw_death()
            pygame.display.flip()


pygame.init()
SnakeGame().play()
pygame.quit()
