import pygame
from pygame import mixer
mixer.init()

import random
import time
import os

WIDTH = 1000
HEIGHT = 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

#background display
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("325doc", "background-black.png")), (WIDTH, HEIGHT))

#player & laser
MAIN_SHIP = pygame.image.load(os.path.join("325doc", "Xiangmin_Jiao_Web_Photo1.png"))
MAIN_LASER = pygame.image.load(os.path.join("325doc", "pixel_laser_yellow.png"))

#enemy wolfies & lasers
SHIP1 = pygame.image.load(os.path.join("325doc", "wolfie1.png"))
LASER1 = pygame.image.load(os.path.join("325doc", "pixel_laser_red.png"))
SHIP2 = pygame.image.load(os.path.join("325doc", "wolfie2.png"))
LASER2 = pygame.image.load(os.path.join("325doc", "pixel_laser_green.png"))
SHIP3 = pygame.image.load(os.path.join("325doc", "wolfie3.png"))
LASER3 = pygame.image.load(os.path.join("325doc", "pixel_laser_blue.png"))

#general lasers
class Laser:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
    def move(self, speed):
        self.y += speed
    def screen_cutoff(self, height):
        return not (height >= self.y >= 0)
    def collision(self, obj):
        return collide(self, obj)

#general ships
class Ship:
    SHOOTING_COOLDOWN = 25

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, speed, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.screen_cutoff(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.SHOOTING_COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()

#player's ship
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_image = MAIN_SHIP
        self.laser_image = MAIN_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health

    def move_lasers(self, speed, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.screen_cutoff(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_image.get_height() + 10,
            self.ship_image.get_width() * (self.health / self.max_health), 10))

#enemy ships
class Enemy(Ship):
    MAP = {"ONE": (SHIP1, LASER1), "TWO": (SHIP2, LASER2), "THREE": (SHIP3, LASER3)}

    def __init__(self, x, y, map, health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.MAP[map]
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, speed):
        self.y += speed

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

pygame.font.init()
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.Font(os.path.join("325doc","slkscr.ttf"), 40)
    lost_font = pygame.font.Font(os.path.join("325doc","slkscr.ttf"), 60)
    lvl_font = pygame.font.Font(os.path.join("325doc", "slkscr.ttf"), 80)

    enemies = []
    wave_length = 5
    enemy_speed = 1

    player_speed = 6
    player_laser_speed = 10
    enemy_laser_speed = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WINDOW.blit(BACKGROUND, (0, 0))
        # draw text
        lives_label = main_font.render(f"remaining defense: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WINDOW.blit(lives_label, (13, 10))
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if lost:
            lost_sound = pygame.mixer.Sound(os.path.join("325doc", "game_over.mp3"))
            lost_sound.set_volume(0.6)
            lost_sound.play()
            lost_label = lost_font.render("you suck! get good :(", 1, (255, 255, 255))
            WINDOW.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

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
            lvl_label = lvl_font.render(f"level: {level}", 1, (255, 255, 255))
            WINDOW.blit(lvl_label, (WIDTH / 2 - lvl_label.get_width() / 2, 350))
            pygame.display.update()
            pygame.time.delay(1200)

            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["ONE", "TWO", "THREE"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
#control direction
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_speed > 0:  # left
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.x + player_speed + player.get_width() < WIDTH:  # right
            player.x += player_speed
        if keys[pygame.K_UP] and player.y - player_speed > 0:  # up
            player.y -= player_speed
        if keys[pygame.K_DOWN] and player.y + player_speed + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()
            laser_sound = pygame.mixer.Sound(os.path.join("325doc", "lasergunsound_cutted.mp3"))
            laser_sound.set_volume(0.15)
            laser_sound.play()

        for enemy in enemies[:]:
            enemy.move(enemy_speed)
            enemy.move_lasers(enemy_laser_speed, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 5
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                defense_sound = pygame.mixer.Sound(os.path.join("325doc", "buzzer_sound_effect.mp3"))
                defense_sound.set_volume(0.4)
                defense_sound.play()
                enemies.remove(enemy)

        player.move_lasers(-player_laser_speed, enemies)

#background music
mixer.music.load(os.path.join("325doc", "Another_Medium_Loop.mp3"))
mixer.music.set_volume(0.2)
mixer.music.play(loops=-1)

def main_menu():
    title_font = pygame.font.Font(os.path.join("325doc","slkscrb.ttf"), 60)
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("click to start...", 1, (255, 255, 255))
        WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
game.run()
