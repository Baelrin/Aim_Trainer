import math
import random
import time
import pygame
import json

pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (0, 25, 40)
TOP_BAR_HEIGHT = 50
LIVES = 10
TARGET_INCREMENT = 400
TARGET_PADDING = 30

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)

# Fonts
LABEL_FONT = pygame.font.SysFont("comicsans", 24)
MENU_FONT = pygame.font.SysFont("comicsans", 40)

# Pygame setup
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

# Custom events
TARGET_EVENT = pygame.USEREVENT


class Target(pygame.sprite.Sprite):
    """Represents a target in the game."""

    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = RED
    SECOND_COLOR = WHITE

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.rect = pygame.Rect(
            x - self.size, y - self.size, self.size * 2, self.size * 2
        )

    def update(self, *args, **kwargs):
        """Update the target's size and position."""
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

        self.rect = pygame.Rect(
            self.x - self.size, self.y - self.size, self.size * 2, self.size * 2
        )

    def draw(self, win):
        """Draw the target on the given surface."""
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        """Check if the given point collides with the target."""
        return self.rect.collidepoint(x, y)


class Game:
    """Manages the game state and logic."""

    def __init__(self, difficulty="normal"):
        self.targets = pygame.sprite.Group()
        self.targets_pressed = 0
        self.clicks = 0
        self.misses = 0
        self.start_time = time.time()
        self.set_difficulty(difficulty)
        self.paused = False
        self.load_high_score()

    def set_difficulty(self, difficulty):
        """Set the game difficulty."""
        if difficulty == "easy":
            self.target_increment = 600
            Target.GROWTH_RATE = 0.15
        elif difficulty == "hard":
            self.target_increment = 300
            Target.GROWTH_RATE = 0.25
        else:  # normal
            self.target_increment = 400
            Target.GROWTH_RATE = 0.2

    def add_target(self):
        """Add a new target to the game."""
        x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
        y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
        self.targets.add(Target(x, y))

    def update(self, mouse_pos, click):
        """Update the game state."""
        if self.paused:
            return time.time() - self.start_time

        elapsed_time = time.time() - self.start_time

        for target in self.targets.sprites():
            target.update()

            if target.size <= 0:
                self.targets.remove(target)
                self.misses += 1

            elif click and target.collide(*mouse_pos):
                self.targets.remove(target)
                self.targets_pressed += 1

        if click:
            self.clicks += 1

        return elapsed_time

    def draw(self, win):
        """Draw the game state on the given surface."""
        win.fill(BG_COLOR)
        for target in self.targets:
            target.draw(win)

    def draw_top_bar(self, win, elapsed_time):
        """Draw the top information bar."""
        pygame.draw.rect(win, GREY, (0, 0, WIDTH, TOP_BAR_HEIGHT))

        time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, BLACK)
        speed = round(self.targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
        speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, BLACK)
        hits_label = LABEL_FONT.render(f"Hits: {self.targets_pressed}", 1, BLACK)
        lives_label = LABEL_FONT.render(f"Lives: {LIVES - self.misses}", 1, BLACK)

        win.blit(time_label, (5, 5))
        win.blit(speed_label, (200, 5))
        win.blit(hits_label, (450, 5))
        win.blit(lives_label, (650, 5))

    def toggle_pause(self):
        """Toggle the game's pause state."""
        self.paused = not self.paused

    def load_high_score(self):
        """Load the high score from a file."""
        try:
            with open("high_score.json", "r") as f:
                self.high_score = json.load(f)
        except FileNotFoundError:
            self.high_score = {"speed": 0, "hits": 0}

    def save_high_score(self):
        """Save the current high score to a file."""
        with open("high_score.json", "w") as f:
            json.dump(self.high_score, f)

    def update_high_score(self, elapsed_time):
        """Update the high score if necessary."""
        speed = round(self.targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
        if speed > self.high_score["speed"]:
            self.high_score["speed"] = speed
        if self.targets_pressed > self.high_score["hits"]:
            self.high_score["hits"] = self.targets_pressed
        self.save_high_score()


def format_time(secs):
    """Format the given time in seconds to a string."""
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"


def draw_menu(win):
    """Draw the main menu."""
    win.fill(BG_COLOR)
    title = MENU_FONT.render("Aim Trainer", 1, WHITE)
    start = MENU_FONT.render("Press SPACE to Start", 1, WHITE)
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
    win.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.update()


def end_screen(win, elapsed_time, targets_pressed, clicks, high_score):
    """Display the end screen with game results."""
    win.fill(BG_COLOR)
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, WHITE)
    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, WHITE)
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, WHITE)
    accuracy = round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, WHITE)
    high_score_label = LABEL_FONT.render(
        f"High Score: {high_score['speed']} t/s, {high_score['hits']} hits", 1, WHITE
    )

    win.blit(time_label, (WIDTH // 2 - time_label.get_width() // 2, 100))
    win.blit(speed_label, (WIDTH // 2 - speed_label.get_width() // 2, 200))
    win.blit(hits_label, (WIDTH // 2 - hits_label.get_width() // 2, 300))
    win.blit(accuracy_label, (WIDTH // 2 - accuracy_label.get_width() // 2, 400))
    win.blit(high_score_label, (WIDTH // 2 - high_score_label.get_width() // 2, 500))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                waiting = False


# ... (предыдущий код остается без изменений до функции main())


def handle_events(game):
    """Handle pygame events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == TARGET_EVENT and not game.paused:
            game.add_target()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.toggle_pause()
    return False


def update_game_state(game, mouse_pos, click):
    """Update the game state and check for game over condition."""
    elapsed_time = game.update(mouse_pos, click)

    if game.misses >= LIVES:
        game.update_high_score(elapsed_time)
        end_screen(
            WIN, elapsed_time, game.targets_pressed, game.clicks, game.high_score
        )
        return False

    return True


def draw_game(game, elapsed_time):
    """Draw the game state on the screen."""
    game.draw(WIN)
    game.draw_top_bar(WIN, elapsed_time)

    if game.paused:
        pause_label = MENU_FONT.render("PAUSED", 1, WHITE)
        WIN.blit(pause_label, (WIDTH // 2 - pause_label.get_width() // 2, HEIGHT // 2))

    pygame.display.update()


def run_game_loop():
    """Run the main game loop."""
    game = Game()
    pygame.time.set_timer(TARGET_EVENT, game.target_increment)

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        click = handle_events(game)
        mouse_pos = pygame.mouse.get_pos()

        if not update_game_state(game, mouse_pos, click):
            running = False

        draw_game(game, time.time() - game.start_time)


def main():
    """Main game function."""
    while show_menu():
        run_game_loop()

    pygame.quit()


def show_menu():
    """Show the main menu and wait for user input."""
    draw_menu(WIN)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
    return False


if __name__ == "__main__":
    main()
