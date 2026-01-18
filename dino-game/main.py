import pygame
import sys

pygame.init()

# ------------------ SETTINGS ------------------
WIDTH, HEIGHT = 800, 400
GROUND_Y = 300
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ------------------ SCREEN ------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 42)

# ------------------ LOAD IMAGES ------------------
dino_img = pygame.transform.scale(
    pygame.image.load("assets/dino.png").convert_alpha(), (50, 50)
)
alien_img = pygame.transform.scale(
    pygame.image.load("assets/monster.png").convert_alpha(), (40, 40)
)
cactus_img = pygame.transform.scale(
    pygame.image.load("assets/cactus.png").convert_alpha(), (35, 50)
)
fireball_img = pygame.transform.scale(
    pygame.image.load("assets/fireball.png").convert_alpha(), (20, 10)
)

# ------------------ GAME CONSTANTS ------------------
GRAVITY = 1
JUMP_POWER = -18
OBSTACLE_SPEED = 6

DOUBLE_TAP_TIME = 200  # ms

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1400)

# ------------------ RESET FUNCTION ------------------
def reset_game():
    global dino, dino_vel_y, on_ground
    global monsters, cactuses, fireballs
    global game_over
    global waiting_for_second_tap, first_tap_time, action_committed

    dino = pygame.Rect(80, GROUND_Y - 50, 50, 50)
    dino_vel_y = 0
    on_ground = True

    monsters = []
    cactuses = []
    fireballs = []

    waiting_for_second_tap = False
    first_tap_time = 0
    action_committed = False

    game_over = False

reset_game()

# ------------------ GAME LOOP ------------------
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == SPAWN_EVENT and not game_over:
            # Randomly spawn monster or cactus
            if pygame.time.get_ticks() % 2 == 0:
                monster = pygame.Rect(WIDTH, GROUND_Y - 40, 40, 40)
                monsters.append(monster)
            else:
                cactus = pygame.Rect(WIDTH, GROUND_Y - 50, 35, 50)
                cactuses.append(cactus)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()

            if event.key == pygame.K_SPACE and not game_over:
                current_time = pygame.time.get_ticks()

                # SECOND TAP → SHOOT
                if (
                    waiting_for_second_tap
                    and not action_committed
                    and current_time - first_tap_time <= DOUBLE_TAP_TIME
                ):
                    if on_ground:
                        dino_vel_y = JUMP_POWER
                        on_ground = False

                    action_committed = True
                    waiting_for_second_tap = False

                # FIRST TAP → WAIT
                elif not waiting_for_second_tap:
                    waiting_for_second_tap = True
                    first_tap_time = current_time
                    action_committed = False

    # -------- CONFIRM SINGLE TAP (JUMP) --------
    if waiting_for_second_tap and not action_committed:
        current_time = pygame.time.get_ticks()
        if current_time - first_tap_time > DOUBLE_TAP_TIME:
            fireball = pygame.Rect(
                dino.right, dino.centery - 5, 20, 10
            )
            fireballs.append(fireball)

            action_committed = True
            waiting_for_second_tap = False

    # -------- DINO PHYSICS --------
    if not game_over:
        dino_vel_y += GRAVITY
        dino.y += dino_vel_y

        if dino.bottom >= GROUND_Y:
            dino.bottom = GROUND_Y
            dino_vel_y = 0
            on_ground = True

    # -------- MOVE MONSTERS --------
    for monster in monsters[:]:
        monster.x -= OBSTACLE_SPEED
        if monster.right < 0:
            monsters.remove(monster)

        if dino.colliderect(monster):
            game_over = True

    # -------- MOVE CACTUSES --------
    for cactus in cactuses[:]:
        cactus.x -= OBSTACLE_SPEED
        if cactus.right < 0:
            cactuses.remove(cactus)

        if dino.colliderect(cactus):
            game_over = True

    # -------- MOVE FIREBALLS --------
    for fireball in fireballs[:]:
        fireball.x += 10
        if fireball.left > WIDTH:
            fireballs.remove(fireball)

        for monster in monsters[:]:
            if fireball.colliderect(monster):
                monsters.remove(monster)
                fireballs.remove(fireball)
                break

    # -------- DRAW --------
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    screen.blit(dino_img, dino)

    for monster in monsters:
        screen.blit(alien_img, monster)

    for cactus in cactuses:
        screen.blit(cactus_img, cactus)

    for fireball in fireballs:
        screen.blit(fireball_img, fireball)

    if game_over:
        screen.blit(
            font.render("GAME OVER", True, BLACK),
            (WIDTH // 2 - 100, HEIGHT // 2 - 30),
        )
        screen.blit(
            font.render("Press R to Restart", True, BLACK),
            (WIDTH // 2 - 160, HEIGHT // 2 + 10),
        )

    pygame.display.update()
