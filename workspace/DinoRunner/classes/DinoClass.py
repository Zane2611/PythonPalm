import os

import pygame

from classes.runtime_paths import resource_path

DINO_WIDTH = 40
DINO_HEIGHT = 40


class DinoClass:
    def __init__(self, x, y, width=DINO_WIDTH, height=DINO_HEIGHT):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_y = 0
        self.is_jumping = False
        # Movement tuning (base values kept for scaling)
        self.base_gravity = 0.6
        self.base_jump_strength = -11
        self.gravity = self.base_gravity
        self.jump_strength = self.base_jump_strength
        image_path = resource_path("assets", "dino.png")
        self.image = pygame.image.load(str(image_path))
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_strength
    
    def update(self, ground_level):
        self.animate()
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            
            if self.y >= ground_level:
                self.y = ground_level
                self.is_jumping = False
                self.velocity_y = 0
    
    def animate(self):
        # später implementieren
        pass
    
    def draw(self, screen, color=(0, 0, 0)):
        screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def scale_movement_for_speed(self, obstacle_speed, base_obstacle_speed=10):
        """Scale jump strength and gravity based on obstacle speed.

        The scaling increases movement proportionally so the dino can reach higher/further
        jumps when obstacles get faster. We want the jump HEIGHT to remain
        approximately constant (so the dino can't clear birds), but make the
        jump occur faster: a larger initial upward velocity and a stronger
        gravity so time-to-peak decreases while peak height stays the same.

        Implementation: scale initial velocity by `beta` and gravity by
        `beta**2` so that h = v^2/(2g) remains constant. `beta` increases
        modestly with obstacle speed.
        """
        delta = max(0.0, obstacle_speed - base_obstacle_speed)
        # beta: how much faster the upward velocity should be (modest rate)
        beta = 1.0 + (delta * 0.03)
        self.jump_strength = self.base_jump_strength * beta
        self.gravity = self.base_gravity * (beta * beta)