import random

import pygame

from classes.runtime_paths import resource_path


CACTUS_WIDTH = 24
CACTUS_HEIGHT = 36
TRIPLE_MIDDLE_WIDTH = 28
TRIPLE_MIDDLE_HEIGHT = 46
TRIPLE_MIDDLE_Y_OFFSET = 12
TRIPLE_SIDE_OFFSET = 28


class CactusClass:
    def __init__(self, x, y, speed, variant=None):
        self.x = x
        self.y = y
        self.speed = speed
        # variant: 1=single, 2=double, 3=triple
        if variant is None:
            self.variant = random.choice([1, 1, 1, 3, 3])
        else:
            self.variant = variant
        self.base_image = pygame.image.load(str(resource_path("assets", "bones.png"))).convert_alpha()
        self.parts = self.build_parts()

    def create_part(self, offset_x, offset_y, width, height):
        image_width = int(width * 1.1)
        image_offset_x = offset_x - ((image_width - width) // 2)
        return {
            "offset_x": offset_x,
            "offset_y": offset_y,
            "width": width,
            "height": height,
            "image_offset_x": image_offset_x,
            "image": pygame.transform.smoothscale(self.base_image, (image_width, height)),
        }

    def build_parts(self):
        if self.variant == 3:
            return [
                self.create_part(0, 0, CACTUS_WIDTH, CACTUS_HEIGHT),
                self.create_part(TRIPLE_SIDE_OFFSET, -TRIPLE_MIDDLE_Y_OFFSET, TRIPLE_MIDDLE_WIDTH, TRIPLE_MIDDLE_HEIGHT),
                self.create_part(TRIPLE_SIDE_OFFSET + TRIPLE_MIDDLE_WIDTH + 6, 0, CACTUS_WIDTH, CACTUS_HEIGHT),
            ]
        if self.variant == 2:
            # double cactus: two single-width cactuses with a small gap
            double_gap = 8
            return [
                self.create_part(0, 0, CACTUS_WIDTH, CACTUS_HEIGHT),
                self.create_part(CACTUS_WIDTH + double_gap, 0, CACTUS_WIDTH, CACTUS_HEIGHT),
            ]

        return [self.create_part(0, 0, CACTUS_WIDTH, CACTUS_HEIGHT)]

    def update(self):
        self.x -= self.speed

    def is_off_screen(self):
        return self.x + self.get_width() < 0

    def get_width(self):
        return max(part["offset_x"] + part["width"] for part in self.parts)

    def draw(self, screen, color=(0, 0, 0)):
        for part in self.parts:
            screen.blit(part["image"], (self.x + part["image_offset_x"], self.y + part["offset_y"] + 5))

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