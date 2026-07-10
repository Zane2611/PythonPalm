import pygame
import random
import json
import os

from classes.runtime_paths import app_root

BASE_DIR = app_root()

from classes.DinoClass import DinoClass
from classes.BirdClass import BirdClass
from classes.BackgroundClass import BackgroundClass
from classes.CactusClass import CactusClass
from classes.SpinoClass import SpinoClass

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_Y = 300

DINO_X = 80
DINO_Y = 300
DINO_WIDTH = 40
DINO_HEIGHT = 40


OBSTACLE_X = 800
OBSTACLE_Y = 300
OBSTACLE_SPEED = 7
OBSTACLE_SPEED_INCREASE = 0.5
SPEED_INCREASE_INTERVAL_MS = 5000
OBSTACLE_SPAWN_OFFSET_MIN = 80
OBSTACLE_SPAWN_OFFSET_MAX = 260
OBSTACLE_VARIANTS = ["cactus", "bird"]
SPAWN_INTERVAL_MIN_MS = 700
SPAWN_INTERVAL_MAX_MS = 1600
EARLY_GAME_SPAWN_WINDOW_MS = 10000
EARLY_GAME_SPAWN_MULTIPLIER = 1.7
SPINO_TRIGGER_SCORE = 100
SPINO_SEQUENCE_COUNT = 3
SPINO_SEQUENCE_GAP_MS = 850
CODEWORD_TRIGGER_SCORE = 150





class DinoRunnerClass:
    def __init__(self):
        pygame.init()

        self.fade_alpha = 255
        self.fade_start_time = None
        self.fade_duration = 2000  # fade out over 2 seconds
        self.display_duration = 1000  # show text for 1 second before fading

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.WHITE = (235, 235, 235)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Dino Runner in Python")

        self.clock = pygame.time.Clock()
        self.game_speed = 100
        self.last_speed_increase_time = pygame.time.get_ticks()

        self.dino = DinoClass(DINO_X, DINO_Y, DINO_WIDTH, DINO_HEIGHT)
        self.background = BackgroundClass(self.SCREEN_WIDTH)
        # obstacle management: allow multiple active obstacles and timed spawns
        self.obstacles = []
        self.obstacle_speed = OBSTACLE_SPEED
        self.game_start_time = pygame.time.get_ticks()
        now = self.game_start_time
        self.next_spawn_time = now + self.get_spawn_interval(now)
        self.spino_triggered = False
        self.spino_sequence_active = False
        self.spino_sequence_remaining = 0
        self.spino_next_spawn_time = 0

        self.running = True
        self.game_over = False
        self.current_score = 0
        self.highscore = self.load_highscore()
        self.font = pygame.font.Font(None, 36)

    def reset_game(self):
        self.dino = DinoClass(DINO_X, DINO_Y, DINO_WIDTH, DINO_HEIGHT)
        self.background.reset()
        self.obstacles = []
        self.obstacle_speed = OBSTACLE_SPEED
        self.game_start_time = pygame.time.get_ticks()
        now = self.game_start_time
        self.next_spawn_time = now + self.get_spawn_interval(now)
        self.spino_sequence_active = False
        self.spino_sequence_remaining = 0
        self.spino_next_spawn_time = 0
        # keep spino_triggered as a session flag so the boss event only happens once per app run
        self.game_over = False
        self.last_speed_increase_time = pygame.time.get_ticks()
        self.current_score = 0
        # inform dino of reset speed
        self.dino.scale_movement_for_speed(self.obstacle_speed)

    def load_highscore(self):
        score_file = BASE_DIR / "data" / "score.json"
        if os.path.exists(score_file):
            try:
                with open(score_file, "r") as f:
                    data = json.load(f)
                    return data.get("highscore", 0)
            except:
                return 0
        return 0

    def save_highscore(self, score):
        score_file = BASE_DIR / "data" / "score.json"
        score_file.parent.mkdir(parents=True, exist_ok=True)
        with open(score_file, "w") as f:
            json.dump({"highscore": score}, f)

    def get_spawn_interval(self, now):
        elapsed_ms = now - self.game_start_time
        if elapsed_ms < EARLY_GAME_SPAWN_WINDOW_MS:
            interval_min = int(SPAWN_INTERVAL_MIN_MS * EARLY_GAME_SPAWN_MULTIPLIER)
            interval_max = int(SPAWN_INTERVAL_MAX_MS * EARLY_GAME_SPAWN_MULTIPLIER)
        else:
            interval_min = SPAWN_INTERVAL_MIN_MS
            interval_max = SPAWN_INTERVAL_MAX_MS

        interval = random.randint(interval_min, interval_max)
        speed_factor = 1.0 / max(1.0, (1.0 + (self.obstacle_speed - OBSTACLE_SPEED) * 0.03))
        return int(interval * speed_factor)

    def create_obstacle(self, speed=OBSTACLE_SPEED):
        spawn_x = self.SCREEN_WIDTH + random.randint(OBSTACLE_SPAWN_OFFSET_MIN, OBSTACLE_SPAWN_OFFSET_MAX)
        # Types: 'single'=single cactus, 'double'=two cactuses, 'triple'=three-part cactus, 'bird'
        # Weights: single 30%, double 30%, triple 30%, bird 10%
        choice = random.choices(['single', 'double', 'triple', 'bird'], weights=[30, 30, 30, 10], k=1)[0]

        if choice == 'bird':
            return BirdClass(spawn_x, OBSTACLE_Y, speed)

        if choice == 'double':
            return CactusClass(spawn_x, OBSTACLE_Y, speed, variant=2)

        if choice == 'triple':
            return CactusClass(spawn_x, OBSTACLE_Y, speed, variant=3)

        # default: single
        return CactusClass(spawn_x, OBSTACLE_Y, speed, variant=1)

    def create_spino(self, speed):
        spawn_x = self.SCREEN_WIDTH + 20
        return SpinoClass(spawn_x, OBSTACLE_Y, speed)

    def has_active_spino(self):
        return any(isinstance(obs, SpinoClass) for obs in self.obstacles)

    def update_spino_event(self):
        if self.current_score >= SPINO_TRIGGER_SCORE and not self.spino_triggered:
            self.spino_triggered = True
            self.spino_sequence_active = True
            self.spino_sequence_remaining = SPINO_SEQUENCE_COUNT
            self.spino_next_spawn_time = pygame.time.get_ticks()
            self.obstacles = [obs for obs in self.obstacles if isinstance(obs, SpinoClass)]

        if not self.spino_sequence_active:
            return

        now = pygame.time.get_ticks()
        if self.has_active_spino():
            return

        if self.spino_sequence_remaining > 0 and now >= self.spino_next_spawn_time:
            self.obstacles.append(self.create_spino(self.obstacle_speed + 4))
            self.spino_sequence_remaining -= 1
            if self.spino_sequence_remaining > 0:
                self.spino_next_spawn_time = now + SPINO_SEQUENCE_GAP_MS
            else:
                self.spino_sequence_active = False

    def try_spawn(self):
        if self.spino_sequence_active or self.has_active_spino():
            return

        if not self.spino_triggered and self.current_score >= (SPINO_TRIGGER_SCORE - 20):
            return

        now = pygame.time.get_ticks()
        if now >= self.next_spawn_time:
            self.obstacles.append(self.create_obstacle(self.obstacle_speed))
            self.next_spawn_time = now + self.get_spawn_interval(now)

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
        self.update_spino_event()

    def update_obstacles(self):
        for obs in list(self.obstacles):
            obs.speed = self.obstacle_speed
            obs.update()
            if obs.is_off_screen():
                self.obstacles.remove(obs)


    def increase_obstacle_speed(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_speed_increase_time >= SPEED_INCREASE_INTERVAL_MS:
            self.obstacle_speed += OBSTACLE_SPEED_INCREASE
            # update dino movement to match faster obstacles
            self.dino.scale_movement_for_speed(self.obstacle_speed)
            self.last_speed_increase_time = current_time

    def check_collision(self):
        for obs in self.obstacles:
            for obstacle_rect in obs.get_rects():
                if self.dino.get_rect().colliderect(obstacle_rect):
                    self.dino.set_dead()
                    print(f"Game Over! Score: {self.current_score}")
                    if self.current_score > self.highscore:
                        self.highscore = self.current_score
                        self.save_highscore(self.highscore)
                        print(f"New Highscore: {self.highscore}")
                    self.game_over = True
                    return

    def draw_game_over(self):
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.WHITE)
        self.screen.blit(overlay, (0, 0))

        title_font = pygame.font.Font(None, 64)
        text_font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 28)

        if self.current_score >= CODEWORD_TRIGGER_SCORE:
            codeword = text_font.render("Das ist das Code Wort", True, self.GREEN)
            codeword_rect = codeword.get_rect(center=(self.SCREEN_WIDTH // 2, 220))
            self.screen.blit(codeword, codeword_rect)

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
        self.background.draw(self.screen)
        pygame.draw.line(self.screen, self.BLACK, (0, 340), (self.SCREEN_WIDTH, 340), 2)
        self.dino.draw(self.screen, self.BLACK)
        for obs in self.obstacles:
            obs.draw(self.screen, self.BLACK)

        small_font = pygame.font.Font(None, 24)

        if self.spino_sequence_remaining > 0:

            # Start timer once
            if self.fade_start_time is None:
                self.fade_start_time = pygame.time.get_ticks()

            elapsed = pygame.time.get_ticks() - self.fade_start_time

            # Create text surface
            codeword = small_font.render("Ihr könnt mich nie besiegen", True, self.BLACK)
            codeword = codeword.convert_alpha()  # important for transparency

            # After display_duration, start fading
            if elapsed > self.display_duration:
                fade_elapsed = elapsed - self.display_duration
                fade_progress = fade_elapsed / self.fade_duration
                self.fade_alpha = max(0, 255 - int(255 * fade_progress))

            # Apply alpha
            codeword.set_alpha(self.fade_alpha)

            # Draw
            codeword_rect = codeword.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
            self.screen.blit(codeword, codeword_rect)

            #reset 
            self.fade_start_time = None
            self.fade_alpha = 255
            

        if self.current_score > CODEWORD_TRIGGER_SCORE:

            # Start timer once
            if self.fade_start_time is None:
                self.fade_start_time = pygame.time.get_ticks()

            elapsed = pygame.time.get_ticks() - self.fade_start_time

            # Create text surface
            codeword = small_font.render("Oh nein wie habt ihr es soweit geschafft?", True, self.BLACK)
            codeword = codeword.convert_alpha()  

            # After display_duration, start fading
            if elapsed > self.display_duration:
                fade_elapsed = elapsed - self.display_duration
                fade_progress = fade_elapsed / self.fade_duration
                self.fade_alpha = max(0, 255 - int(255 * fade_progress))

            # Apply alpha
            codeword.set_alpha(self.fade_alpha)

            # Draw
            codeword_rect = codeword.get_rect(center=(self.SCREEN_WIDTH // 2, 180))
            self.screen.blit(codeword, codeword_rect)


        score_text = small_font.render(f"Score: {self.current_score}", True, self.BLACK)
        highscore_text = small_font.render(f"Highscore: {self.highscore}", True, self.BLACK)

        score_rect = score_text.get_rect(topright=(self.SCREEN_WIDTH - 10, 10))
        highscore_rect = highscore_text.get_rect(topright=(self.SCREEN_WIDTH - 10, 35))

        self.screen.blit(score_text, score_rect)
        self.screen.blit(highscore_text, highscore_rect)

        


    def run(self):
        while self.running:
            self.handle_events()
            self.background.update()

            if self.game_over:
                self.draw()
                self.draw_game_over()
            else:
                self.update_physics()
                if self.obstacle_speed < 26:
                    self.increase_obstacle_speed()
                # spawn new obstacles based on timer
                self.try_spawn()
                self.update_obstacles()
                self.check_collision()
                self.draw()

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    DinoRunnerClass().run()
