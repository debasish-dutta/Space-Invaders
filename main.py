import random
import pygame
from sys import exit

WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders')

#fonts
pygame.font.init()

# Enemy ships
RED_SPACE_SHIP = pygame.image.load("Space Invaders\Graphics\ships\ship_red.png").convert_alpha()
RED_SPACE_SHIP = pygame.transform.scale(RED_SPACE_SHIP, (50,50))
GREEN_SPACE_SHIP = pygame.image.load("Space Invaders\Graphics\ships\ship_green.png").convert_alpha()
GREEN_SPACE_SHIP = pygame.transform.scale(GREEN_SPACE_SHIP, (50,50))
BLUE_SPACE_SHIP = pygame.image.load("Space Invaders\Graphics\ships\ship_blue.png").convert_alpha()
BLUE_SPACE_SHIP = pygame.transform.scale(BLUE_SPACE_SHIP, (50,50))

# Player ship
SHOOTER_SPACE_SHIP = pygame.image.load("Space Invaders\Graphics\shooter\shooter_ship.png").convert_alpha()
SHOOTER_SPACE_SHIP = pygame.transform.scale(SHOOTER_SPACE_SHIP, (75,75))

# Missiles
RED_LASER = pygame.image.load("Space Invaders\Graphics\missiles\mr.png").convert_alpha()
RED_LASER = pygame.transform.rotozoom(RED_LASER, 180, 0.5)
GREEN_LASER = pygame.image.load("Space Invaders\Graphics\missiles\mg.png").convert_alpha()
GREEN_LASER = pygame.transform.rotozoom(GREEN_LASER, 180, 0.5)
BLUE_LASER = pygame.image.load("Space Invaders\Graphics\missiles\mb.png").convert_alpha()
BLUE_LASER = pygame.transform.rotozoom(BLUE_LASER, 180, 0.5)
MAIN_LASER = pygame.image.load("Space Invaders\Graphics\missiles\sm.png").convert_alpha()
MAIN_LASER = pygame.transform.rotozoom(MAIN_LASER, 0, 0.5)


#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter +=1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+23, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Shooter(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health=health)
        self.ship_img = SHOOTER_SPACE_SHIP
        self.laser_img = MAIN_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health=health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5

    lost = False
    lost_count = 0

    player_vel = 5
    laser_vel = 4

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player = Shooter(300, 400)

    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 30)
    lost_font = pygame.font.SysFont("comicsans",40)


    def redraw_window():
        WIN.fill(BLACK)

        lives_label = main_font.render(f"Lives: {lives}", 1, WHITE)
        level_label = main_font.render(f"Level: {level}", 1, WHITE)
        
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width()- 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!!", 1, RED)
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1100, -100), random.choice(['red', 'green', 'blue']))
                enemies.append(enemy)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]and player.x + player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_d]and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w]and player.y + player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

            
            
        player.move_lasers(-laser_vel, enemies)
        
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.fill(BLACK)
        title_label = title_font.render("SPACE INVADERS", 1, RED)
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 75))
        title_label = title_font.render("Press the mouse to begin...", 1, WHITE)
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 500))
        SHOOTER_SPACE_SHIP = pygame.image.load("Space Invaders\Graphics\shooter\shooter_ship.png").convert_alpha()
        SHOOTER_SPACE_SHIP_RECT = SHOOTER_SPACE_SHIP.get_rect(center = (500,300))
        WIN.blit(SHOOTER_SPACE_SHIP, SHOOTER_SPACE_SHIP_RECT)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()