import pygame
import random
import json
import os

from classes.DinoClass import DinoClass
from classes.BirdClass import BirdClass
from classes.CactusClass import CactusClass

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_Y = 300

DINO_X = 80
DINO_Y = 300
DINO_WIDTH = 40
DINO_HEIGHT = 40

OBSTACLE_X = 800
OBSTACLE_Y = 300
OBSTACLE_SPEED = 10
OBSTACLE_SPEED_INCREASE = 1
SPEED_INCREASE_INTERVAL_MS = 5000
OBSTACLE_SPAWN_OFFSET_MIN = 80
OBSTACLE_SPAWN_OFFSET_MAX = 260
OBSTACLE_VARIANTS = ["cactus", "bird"]

class DinoRunnerClass:
    def __init__(self):
        pygame.init()

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Runner in Python")

        self.clock = pygame.time.Clock()
        self.game_speed = 100
        self.last_speed_increase_time = pygame.time.get_ticks()

        self.dino = DinoClass(DINO_X, DINO_Y, DINO_WIDTH, DINO_HEIGHT)
        self.obstacle = self.create_obstacle()

        self.running = True
        self.game_over = False
        self.game_start_time = pygame.time.get_ticks()
        self.current_score = 0
        self.highscore = self.load_highscore()
        self.font = pygame.font.Font(None, 36)

    def reset_game(self):
        self.dino = DinoClass(DINO_X, DINO_Y, DINO_WIDTH, DINO_HEIGHT)
        self.obstacle = self.create_obstacle()
        self.game_over = False
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.game_start_time = pygame.time.get_ticks()
        self.current_score = 0
        self.obstacle.speed = OBSTACLE_SPEED

    def load_highscore(self):
        score_file = "data/score.json"
        if os.path.exists(score_file):
            try:
                with open(score_file, "r") as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except:
                return 0
        return 0

    def save_highscore(self, score):
        score_file = "data/score.json"
        with open(score_file, "w") as f:
            json.dump({"highscore": score}, f)

    def create_obstacle(self, speed=OBSTACLE_SPEED):
        spawn_x = self.SCREEN_WIDTH + random.randint(OBSTACLE_SPAWN_OFFSET_MIN, OBSTACLE_SPAWN_OFFSET_MAX)
        obstacle_type = random.choice(OBSTACLE_VARIANTS)

        if obstacle_type == "bird":
            return BirdClass(spawn_x, OBSTACLE_Y, speed)

        return CactusClass(spawn_x, OBSTACLE_Y, speed)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                else:
                    if event.key == pygame.K_SPACE:
                        self.dino.jump()

    def update_physics(self):
        self.dino.update(GROUND_Y)
        self.current_score = (pygame.time.get_ticks() - self.game_start_time) // 100

    def update_obstacles(self):
        self.obstacle.update()
        if self.obstacle.is_off_screen():
            self.obstacle = self.create_obstacle(self.obstacle.speed)


    def increase_obstacle_speed(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_speed_increase_time >= SPEED_INCREASE_INTERVAL_MS:
            self.obstacle.speed += OBSTACLE_SPEED_INCREASE
            self.last_speed_increase_time = current_time

    def check_collision(self):
        for obstacle_rect in self.obstacle.get_rects():
            if self.dino.get_rect().colliderect(obstacle_rect):
                print(f"Game Over! Score: {self.current_score}")
                if self.current_score > self.highscore:
                    self.highscore = self.current_score
                    self.save_highscore(self.highscore)
                    print(f"New Highscore: {self.highscore}")
                self.game_over = True
                break

    def draw_game_over(self):
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.WHITE)
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 64)
        text_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)

        game_over_text = title_font.render("GAME OVER", True, self.BLACK)
        final_score_text = text_font.render(f"Score: {self.current_score}", True, self.BLACK)
        highscore_text = text_font.render(f"Highscore: {self.highscore}", True, self.BLACK)
        play_again_text = small_font.render("Press SPACE to Play Again", True, self.BLACK)
        quit_text = small_font.render("Press Q to Quit", True, self.BLACK)

        game_over_rect = game_over_text.get_rect(center=(self.SCREEN_WIDTH // 2, 50))
        final_score_rect = final_score_text.get_rect(center=(self.SCREEN_WIDTH // 2, 130))
        highscore_rect = highscore_text.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
        play_again_rect = play_again_text.get_rect(center=(self.SCREEN_WIDTH // 2, 260))
        quit_rect = quit_text.get_rect(center=(self.SCREEN_WIDTH // 2, 310))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(final_score_text, final_score_rect)
        self.screen.blit(highscore_text, highscore_rect)
        self.screen.blit(play_again_text, play_again_rect)
        self.screen.blit(quit_text, quit_rect)

        

    def draw(self):
        self.screen.fill(self.WHITE)
        pygame.draw.line(self.screen, self.BLACK, (0, 340), (self.SCREEN_WIDTH, 340), 2)
        self.dino.draw(self.screen, self.BLACK)
        self.obstacle.draw(self.screen, self.BLACK)

        small_font = pygame.font.Font(None, 24)

        score_text = small_font.render(f"Score: {self.current_score}", True, self.BLACK)
        highscore_text = small_font.render(f"Highscore: {self.highscore}", True, self.BLACK)

        score_rect = score_text.get_rect(topright=(self.SCREEN_WIDTH - 10, 10))
        highscore_rect = highscore_text.get_rect(topright=(self.SCREEN_WIDTH - 10, 35))

        self.screen.blit(score_text, score_rect)
        self.screen.blit(highscore_text, highscore_rect)

        


    def run(self):
        while self.running:
            self.handle_events()

            if self.game_over:
                self.draw()
                self.draw_game_over()
            else:
                self.update_physics()
                if self.obstacle.speed < 30:
                    self.increase_obstacle_speed()
                self.update_obstacles()
                self.check_collision()
                self.draw()

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    DinoRunnerClass().run()
