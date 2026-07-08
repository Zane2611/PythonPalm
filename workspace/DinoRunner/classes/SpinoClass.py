import pygame

from classes.runtime_paths import resource_path


SPINO_WIDTH = 216
SPINO_HEIGHT = 216
SPINO_Y_OFFSET = -150


class SpinoClass:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.frame_index = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_delay_ms = 110
        self.frames = [
            self.load_image("Spino9.png"),
            self.load_image("Spino10.png"),
            self.load_image("Spino11.png"),
            self.load_image("Spino12.png"),
        ]
        self.image = self.frames[0]
        self.parts = [
            {"offset_x": 0, "offset_y": SPINO_Y_OFFSET, "width": SPINO_WIDTH, "height": SPINO_HEIGHT},
        ]

    def load_image(self, file_name):
        image = pygame.image.load(str(resource_path("assets", "walk", file_name))).convert_alpha()
        return pygame.transform.smoothscale(image, (SPINO_WIDTH, SPINO_HEIGHT))

    def update(self):
        self.x -= self.speed
        now = pygame.time.get_ticks()
        if now - self.last_frame_time >= self.frame_delay_ms:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_frame_time = now
        self.image = self.frames[self.frame_index]

    def is_off_screen(self):
        return self.x + self.get_width() < 0

    def get_width(self):
        return max(part["offset_x"] + part["width"] for part in self.parts)

    def draw(self, screen, color=(0, 0, 0)):
        screen.blit(self.image, (self.x, self.y + SPINO_Y_OFFSET))

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