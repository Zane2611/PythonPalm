import random

import pygame


CACTUS_WIDTH = 20
CACTUS_HEIGHT = 40
TRIPLE_MIDDLE_WIDTH = 24
TRIPLE_MIDDLE_HEIGHT = 52
TRIPLE_MIDDLE_Y_OFFSET = 12
TRIPLE_SIDE_OFFSET = 24


class CactusClass:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.variant = random.choice([1, 1, 1, 3, 3])
        self.parts = self.build_parts()

    def build_parts(self):
        if self.variant == 3:
            return [
                {"offset_x": 0, "offset_y": 0, "width": CACTUS_WIDTH, "height": CACTUS_HEIGHT},
                {"offset_x": TRIPLE_SIDE_OFFSET, "offset_y": -TRIPLE_MIDDLE_Y_OFFSET, "width": TRIPLE_MIDDLE_WIDTH, "height": TRIPLE_MIDDLE_HEIGHT},
                {"offset_x": TRIPLE_SIDE_OFFSET + TRIPLE_MIDDLE_WIDTH + 6, "offset_y": 0, "width": CACTUS_WIDTH, "height": CACTUS_HEIGHT},
            ]

        return [{"offset_x": 0, "offset_y": 0, "width": CACTUS_WIDTH, "height": CACTUS_HEIGHT}]

    def update(self):
        self.x -= self.speed

    def is_off_screen(self):
        return self.x + self.get_width() < 0

    def get_width(self):
        return max(part["offset_x"] + part["width"] for part in self.parts)

    def draw(self, screen, color=(0, 0, 0)):
        for part in self.parts:
            pygame.draw.rect(
                screen,
                color,
                (
                    self.x + part["offset_x"],
                    self.y + part["offset_y"],
                    part["width"],
                    part["height"],
                ),
            )

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