import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = -8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
SILVER = (192, 192, 192)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Bonus:
    def __init__(self, x, y):
        self.width = 20
        self.height = 20
        self.x = x
        self.y = y
        self.collected = False
        self.points = 50
        
    def draw(self, screen):
        if not self.collected:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
            # Add sparkle effect
            time = pygame.time.get_ticks() / 200
            for i in range(4):
                angle = time + i * math.pi / 2
                x = self.x + self.width/2 + math.cos(angle) * 15
                y = self.y + self.height/2 + math.sin(angle) * 15
                pygame.draw.circle(screen, WHITE, (int(x), int(y)), 2)

class Aviator:
    def __init__(self):
        self.width = 60
        self.height = 30
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.angle = 0
        
    def jump(self):
        self.velocity = JUMP_FORCE
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Tilt the airplane based on velocity
        self.angle = max(min(self.velocity * 3, 45), -45)
        
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity = 0
            
    def draw(self, screen):
        # Create a surface for the airplane
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw airplane body
        pygame.draw.ellipse(surface, SILVER, (10, 5, 40, 20))
        
        # Draw wings
        pygame.draw.polygon(surface, BLUE, [(25, 0), (35, 0), (30, 15)])
        pygame.draw.polygon(surface, BLUE, [(25, 30), (35, 30), (30, 15)])
        
        # Draw tail
        pygame.draw.polygon(surface, RED, [(45, 10), (55, 5), (55, 25), (45, 20)])
        
        # Draw cockpit
        pygame.draw.ellipse(surface, BLACK, (15, 10, 10, 10))
        
        # Rotate the surface
        rotated = pygame.transform.rotate(surface, self.angle)
        new_rect = rotated.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
        screen.blit(rotated, new_rect.topleft)

class Obstacle:
    def __init__(self, speed):
        self.width = 50
        self.gap = 200
        self.x = SCREEN_WIDTH
        self.top_height = random.randint(100, SCREEN_HEIGHT - self.gap - 100)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - self.gap
        self.speed = speed
        self.passed = False
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, SCREEN_HEIGHT - self.bottom_height, 
                                       self.width, self.bottom_height))
    
    def collides_with(self, aviator):
        aviator_rect = pygame.Rect(aviator.x, aviator.y, aviator.width, aviator.height)
        top_obstacle = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_obstacle = pygame.Rect(self.x, SCREEN_HEIGHT - self.bottom_height, 
                                    self.width, self.bottom_height)
        return aviator_rect.colliderect(top_obstacle) or aviator_rect.colliderect(bottom_obstacle)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Aviator Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.game_state = "menu"  # Changed from self.state to self.game_state
        
        # Create menu buttons
        button_width = 200
        button_height = 50
        start_x = SCREEN_WIDTH // 2 - button_width // 2
        self.start_button = Button(start_x, 250, button_width, button_height, "Start Game", GREEN)
        self.exit_button = Button(start_x, 350, button_width, button_height, "Exit", RED)
        
        self.reset_game()
        
    def reset_game(self):
        self.aviator = Aviator()
        self.level = 1
        self.obstacle_speed = 5
        self.obstacles = [Obstacle(self.obstacle_speed)]
        self.score = 0
        self.bonuses = []
        self.bonus_timer = 0
        
    def spawn_bonus(self):
        x = SCREEN_WIDTH
        y = random.randint(100, SCREEN_HEIGHT - 100)
        self.bonuses.append(Bonus(x, y))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.game_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button.is_clicked(mouse_pos):
                        print("Starting game...")  # Debug print
                        self.game_state = "playing"
                        self.reset_game()
                        return True
                    elif self.exit_button.is_clicked(mouse_pos):
                        return False
                        
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.aviator.jump()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = "menu"
                        
        return True
    
    def update(self):
        if self.game_state != "playing":
            return
            
        self.aviator.update()
        
        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update()
            
            if obstacle.collides_with(self.aviator):
                print("Collision detected!")  # Debug print
                self.game_state = "menu"
                return
            
            if not obstacle.passed and obstacle.x + obstacle.width < self.aviator.x:
                self.score += 10
                obstacle.passed = True
                if self.score % 50 == 0:
                    self.level += 1
                    self.obstacle_speed += 1
        
        # Update bonuses
        self.bonus_timer += 1
        if self.bonus_timer > 180:
            self.spawn_bonus()
            self.bonus_timer = 0
            
        for bonus in self.bonuses:
            if not bonus.collected:
                bonus.x -= self.obstacle_speed
                if (abs(bonus.x - self.aviator.x) < self.aviator.width and 
                    abs(bonus.y - self.aviator.y) < self.aviator.height):
                    bonus.collected = True
                    self.score += bonus.points
        
        # Clean up obstacles and bonuses
        self.obstacles = [obs for obs in self.obstacles if obs.x + obs.width > 0]
        self.bonuses = [bonus for bonus in self.bonuses if bonus.x > -bonus.width]
        
        # Add new obstacles
        if len(self.obstacles) == 0 or self.obstacles[-1].x < SCREEN_WIDTH - 300:
            self.obstacles.append(Obstacle(self.obstacle_speed))
            
    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        if self.game_state == "menu":
            # Draw menu
            title_text = self.font.render("Aviator Game", True, BLACK)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(title_text, title_rect)
            
            self.start_button.draw(self.screen)
            self.exit_button.draw(self.screen)
            
            # Draw instructions
            instruction_font = pygame.font.Font(None, 32)
            instruction_text = instruction_font.render("Press SPACE to fly, ESC to return to menu", True, BLACK)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 450))
            self.screen.blit(instruction_text, instruction_rect)
            
        elif self.game_state == "playing":
            # Draw game elements
            # Draw clouds
            for i in range(3):
                cloud_x = (pygame.time.get_ticks() // 20 + i * 300) % SCREEN_WIDTH
                pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 100, 100, 40))
            
            # Draw obstacles and bonuses
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            for bonus in self.bonuses:
                bonus.draw(self.screen)
            
            # Draw aviator
            self.aviator.draw(self.screen)
            
            # Draw score and level
            score_text = self.font.render(f'Score: {self.score}', True, BLACK)
            level_text = self.font.render(f'Level: {self.level}', True, BLACK)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 60))
        
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()