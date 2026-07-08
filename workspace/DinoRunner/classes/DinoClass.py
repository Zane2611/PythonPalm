import os
import random

import pygame

from classes.runtime_paths import resource_path

DINO_WIDTH = 40
DINO_HEIGHT = 44

IDLE_FRAME = (0, 0, 80, 88)
IDLE_EASTER_EGG_FRAME = (88, 0, 80, 88)
RUN_FRAMES = [
    (176, 0, 80, 88),
    (264, 0, 80, 88),
]
DEAD_FRAMES = [
    (352, 0, 80, 88),
    (440, 0, 80, 88),
]


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
        self.dead = False
        self.is_dead = False
        self.run_frame_index = 0
        self.dead_frame_index = 0
        self.run_last_frame_time = pygame.time.get_ticks()
        self.dead_last_frame_time = pygame.time.get_ticks()
        self.idle_check_delay_ms = 450
        self.frame_delay_ms = 120
        self.idle_easter_egg_until = 0
        self.idle_last_check_time = pygame.time.get_ticks()
        self.sprite_sheet = pygame.image.load(str(resource_path("assets", "dinoSprite.png"))).convert_alpha()
        self.idle_frame = self.load_frame(IDLE_FRAME)
        self.idle_easter_egg_frame = self.load_frame(IDLE_EASTER_EGG_FRAME)
        self.run_frames = [self.load_frame(frame) for frame in RUN_FRAMES]
        self.dead_frames = [self.load_frame(frame) for frame in DEAD_FRAMES]
        self.image = self.run_frames[0]

    def load_frame(self, frame_rect):
        x, y, width, height = frame_rect
        frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, width, height))
        return pygame.transform.scale(frame, (self.width, self.height))

    def set_dead(self):
        self.dead = True
        self.is_dead = True
        self.dead_frame_index = 0
        self.dead_last_frame_time = pygame.time.get_ticks()
        self.image = self.dead_frames[0]

    def reset_state(self):
        self.dead = False
        self.is_dead = False
        self.run_frame_index = 0
        self.dead_frame_index = 0
        self.run_last_frame_time = pygame.time.get_ticks()
        self.dead_last_frame_time = pygame.time.get_ticks()
        self.idle_last_check_time = pygame.time.get_ticks()
        self.idle_easter_egg_until = 0
        self.image = self.run_frames[0]
        
    def jump(self):
        if not self.is_jumping and not self.dead:
            self.is_jumping = True
            self.velocity_y = self.jump_strength
    
    def update(self, ground_level):
        self.animate()
        if self.is_jumping and not self.dead:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            
            if self.y >= ground_level:
                self.y = ground_level
                self.is_jumping = False
                self.velocity_y = 0
    
    def animate(self):
        now = pygame.time.get_ticks()

        if not self.dead:
            if now - self.run_last_frame_time >= self.frame_delay_ms:
                self.run_frame_index = (self.run_frame_index + 1) % len(self.run_frames)
                self.run_last_frame_time = now

        if self.dead:
            now = pygame.time.get_ticks()
            if now - self.dead_last_frame_time >= self.frame_delay_ms:
                self.dead_frame_index = (self.dead_frame_index + 1) % len(self.dead_frames)
                self.dead_last_frame_time = now
            self.image = self.dead_frames[self.dead_frame_index]
            return

        if self.is_jumping:
            if self.idle_easter_egg_until > now:
                self.image = self.idle_easter_egg_frame
                return

            if now - self.idle_last_check_time >= self.idle_check_delay_ms:
                self.idle_last_check_time = now
                if random.randint(1, 200) == 1:
                    self.idle_easter_egg_until = now + 650
                    self.image = self.idle_easter_egg_frame
                    return

            self.image = self.idle_frame
            return

        self.image = self.run_frames[self.run_frame_index]
    
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