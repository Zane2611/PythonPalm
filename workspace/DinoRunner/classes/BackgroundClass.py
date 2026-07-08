import random

import pygame

from classes.runtime_paths import resource_path


class BackgroundClass:
    def __init__(self, screen_width, cloud_count=5, cloud_y_min=20, cloud_y_max=160):
        self.screen_width = screen_width
        self.cloud_y_min = cloud_y_min
        self.cloud_y_max = cloud_y_max
        self.base_image = pygame.image.load(str(resource_path("assets", "Cloud2.png"))).convert_alpha()
        self.clouds = [self.create_cloud(start_x=random.randint(0, self.screen_width)) for _ in range(cloud_count)]

    def create_cloud(self, start_x=None):
        scale = random.uniform(0.08, 0.17)
        width = max(1, int(self.base_image.get_width() * scale))
        height = max(1, int(self.base_image.get_height() * scale))
        image = pygame.transform.smoothscale(self.base_image, (width, height))

        return {
            "x": self.screen_width + random.randint(20, 260) if start_x is None else start_x,
            "y": random.randint(self.cloud_y_min, self.cloud_y_max),
            "speed": random.uniform(0.4, 1.9),
            "image": image,
            "width": width,
        }

    def reset(self):
        self.clouds = [self.create_cloud(start_x=random.randint(0, self.screen_width)) for _ in self.clouds]

    def update(self):
        for index, cloud in enumerate(self.clouds):
            cloud["x"] -= cloud["speed"]
            if cloud["x"] + cloud["width"] < 0:
                self.clouds[index] = self.create_cloud()

    def draw(self, screen):
        for cloud in self.clouds:
            screen.blit(cloud["image"], (cloud["x"], cloud["y"]))