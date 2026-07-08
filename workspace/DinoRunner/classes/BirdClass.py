import pygame

from classes.runtime_paths import resource_path


BIRD_WIDTH = 45
BIRD_HEIGHT = 16
BIRD_Y_OFFSET = -55


class BirdClass:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.base_image = pygame.image.load(str(resource_path("assets", "bird.png"))).convert_alpha()
        self.image = pygame.transform.smoothscale(self.base_image, (BIRD_WIDTH, BIRD_HEIGHT))
        self.parts = [
            {"offset_x": 0, "offset_y": BIRD_Y_OFFSET, "width": BIRD_WIDTH, "height": BIRD_HEIGHT},
        ]

    def update(self):
        self.x -= self.speed

    def is_off_screen(self):
        return self.x + self.get_width() < 0

    def get_width(self):
        return max(part["offset_x"] + part["width"] for part in self.parts)

    def draw(self, screen, color=(0, 0, 0)):
        for part in self.parts:
            screen.blit(self.image, (self.x + part["offset_x"], self.y + part["offset_y"]))

    def get_rects(self):
        return [
            pygame.Rect(
                self.x + part["offset_x"],
                self.y + part["offset_y"],
                part["width"],
                part["height"],
            )
            for part in self.parts
        ]