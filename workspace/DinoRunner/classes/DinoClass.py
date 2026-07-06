import pygame
import pygame

class DinoClass:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity_y = 0
        self.is_jumping = False
        self.gravity = 0.6
        self.jump_strength = -11
        # Load and scale the dino sprite
        self.image = pygame.image.load("assets/dino.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_strength
    
    def update(self, ground_level):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            
            if self.y >= ground_level:
                self.y = ground_level
                self.is_jumping = False
                self.velocity_y = 0
    
    def draw(self, screen, color=(0, 0, 0)):
        screen.blit(self.image, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)