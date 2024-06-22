import pygame
import random
import math
import time

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# 색상 정의
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# 플레이어 설정
player_size = 25
player_speed = 10

# 적 설정
enemy_size = 30

# 총알 설정
bullet_size = 15
bullet_speed = 20

# 게임 초기화 함수
def init_game():
    global player_pos, enemies, bullets, level, start_time, shield_active, shield_pos, shield_generated, max_enemies_dict, max_enemies, restart_text, game_over, speed_ranges, shield_created
    player_pos = [screen_width // 2, screen_height // 2]
    enemies = []
    bullets = []
    level = 1
    start_time = time.time()
    shield_active = False
    shield_pos = None
    shield_generated = False
    max_enemies_dict = {1: 3, 2: 5, 3: 6, 4: 8, 5: 10}
    max_enemies = max_enemies_dict[level]
    restart_text = False
    game_over = False
    speed_ranges = {
        1: (2, 3),
        2: (2, 4),
        3: (2, 5),
        4: (2, 6),
        5: (3, 7)
    }
    shield_created = False

def create_enemy(level):
    side = random.choice(['left', 'right', 'top', 'bottom'])
    speed = random.randint(speed_ranges[level][0], speed_ranges[level][1])  # 단계별 속도 설정
    if side == 'left':
        return [0, random.randint(0, screen_height - enemy_size), speed]
    elif side == 'right':
        return [screen_width - enemy_size, random.randint(0, screen_height - enemy_size), speed]
    elif side == 'top':
        return [random.randint(0, screen_width - enemy_size), 0, speed]
    elif side == 'bottom':
        return [random.randint(0, screen_width - enemy_size), screen_height - enemy_size, speed]

def fire_bullet(player_pos, target_pos):
    angle = math.atan2(target_pos[1] - player_pos[1], target_pos[0] - player_pos[0])
    bullet_dx = bullet_speed * math.cos(angle)
    bullet_dy = bullet_speed * math.sin(angle)
    bullet_pos = [player_pos[0] + player_size // 2 - bullet_size // 2, player_pos[1] + player_size // 2 - bullet_size // 2]
    bullets.append((bullet_pos, bullet_dx, bullet_dy))

def move_towards_player(enemy_pos, player_pos, enemy_speed):
    angle = math.atan2(player_pos[1] - enemy_pos[1], player_pos[0] - enemy_pos[0])
    enemy_pos[0] += int(enemy_speed * math.cos(angle))
    enemy_pos[1] += int(enemy_speed * math.sin(angle))

# 충돌 검사 함수
def check_collision(obj1_pos, obj1_size, obj2_pos, obj2_size):
    if (obj1_pos[0] < obj2_pos[0] + obj2_size and
        obj1_pos[0] + obj1_size > obj2_pos[0] and
        obj1_pos[1] < obj2_pos[1] + obj2_size and
        obj1_pos[1] + obj1_size > obj2_pos[1]):
        return True
    return False

# 화면에 텍스트 표시 함수
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

# 게임 루프
clock = pygame.time.Clock()
running = True
init_game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()  # 게임 종료
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                init_game()  # 게임 초기화
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            target_pos = pygame.mouse.get_pos()
            fire_bullet(player_pos, target_pos)

    if not game_over:
        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time > 30:  # 30초마다 단계 증가
            level += 1
            start_time = current_time

            if level > 5:
                draw_text("You Win! Press 'R' to restart", pygame.font.Font(None, 36), black, screen, screen_width // 2, screen_height // 2)
                pygame.display.update()
                pygame.time.wait(3000)
                game_over = True
            else:
                max_enemies = max_enemies_dict[level]
                shield_active = False
                shield_pos = None
                shield_generated = False
                shield_created = False  # 새로운 단계에서는 보호막 생성 여부를 다시 설정

        # 플레이어 움직임
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_pos[0] > 0:
            player_pos[0] -= player_speed
        if keys[pygame.K_d] and player_pos[0] < screen_width - player_size:
            player_pos[0] += player_speed
        if keys[pygame.K_w] and player_pos[1] > 0:
            player_pos[1] -= player_speed
        if keys[pygame.K_s] and player_pos[1] < screen_height - player_size:
            player_pos[1] += player_speed

        # 적 생성
        if len(enemies) < max_enemies:
            enemy_pos = create_enemy(level)
            enemies.append(enemy_pos)

        # 적 이동
        for enemy in enemies:
            move_towards_player(enemy, player_pos, enemy[2])  # 적의 속도를 enemy[2]로 사용

        # 적이 화면을 벗어나면 제거
        enemies = [enemy for enemy in enemies if 0 <= enemy[0] <= screen_width - enemy_size and 0 <= enemy[1] <= screen_height - enemy_size]

        # 충돌 검사 (플레이어와 적)
        for enemy in enemies:
            if check_collision(player_pos, player_size, enemy, enemy_size):
                if shield_active:
                    shield_active = False
                    enemies.remove(enemy)
                else:
                    game_over = True

        # 총알 이동
        for bullet in bullets:
            bullet[0][0] += bullet[1]
            bullet[0][1] += bullet[2]
            # 적과의 충돌 검사
            for enemy in enemies:
                if check_collision(bullet[0], bullet_size, enemy, enemy_size):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    break

            # 화면을 벗어난 총알 제거
            if bullet[0][0] > screen_width or bullet[0][0] < 0 or bullet[0][1] > screen_height or bullet[0][1] < 0:
                bullets.remove(bullet)

        # 보호막 생성 (단계당 한 번)
        if not shield_created and not shield_active:
            shield_pos = [random.randint(0, screen_width - player_size), random.randint(0, screen_height - player_size)]
            shield_generated = True
            shield_created = True

        # 플레이어와 보호막 충돌 검사
        if shield_generated and shield_pos:
            if check_collision(player_pos, player_size, shield_pos, player_size):
                shield_active = True
                shield_pos = None
                shield_generated = False

        # 화면 업데이트
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, black, (player_pos[0], player_pos[1], player_size, player_size))
        for enemy in enemies:
            pygame.draw.rect(screen, red, (enemy[0], enemy[1], enemy_size, enemy_size))
        for bullet in bullets:
            pygame.draw.rect(screen, black, (bullet[0][0], bullet[0][1], bullet_size, bullet_size))

        # 보호막 표시
        if shield_generated and shield_pos:
            pygame.draw.rect(screen, blue, (shield_pos[0], shield_pos[1], player_size, player_size))

        if game_over and not restart_text:
            draw_text("Game Over. Press 'R' to restart", pygame.font.Font(None, 36), black, screen, screen_width // 2, screen_height // 2)
            restart_text = True

        pygame.display.update()
        clock.tick(30)

pygame.quit()