import cv2
import numpy as np
import time
import copy
from levels import LEVELS
from enemies import EnemyTank, update_enemies
from menu import show_menu
from end_screens import draw_game_over, draw_win

scale_factor = 1
tile_size = 16 * scale_factor
tank_speed = 2 * scale_factor
base_enemy_speed = 0.5 * scale_factor
bullet_speed = 4 * scale_factor
enemy_spawn_interval = 2
max_enemies = 20

black = (0, 0, 0)
white = (255, 255, 255)
yellow = (0, 255, 255)
blue = (255, 0, 0)
red = (0, 0, 255)
green = (0, 255, 0)
gray = (128, 128, 128)

background_image = cv2.imread("pct/tank_fon.jpg")
player_tank_img = cv2.imread("pct/tank_gg.png", cv2.IMREAD_UNCHANGED)
enemy_tank_img = cv2.imread("pct/tank_enemy.png", cv2.IMREAD_UNCHANGED)
brick_wall_img = cv2.imread("pct/stena_kirpich.jpg")
steel_wall_img = cv2.imread("pct/stena_stalnaya.jpg")

for img, name in [(background_image, "tank_fon.jpg"), 
                 (player_tank_img, "tank_gg.png"),
                 (enemy_tank_img, "tank_enemy.png"),
                 (brick_wall_img, "stena_kirpich.jpg"),
                 (steel_wall_img, "stena_stalnaya.jpg")]:
    if img is None:
        print(f"Ошибка: Не удалось загрузить {name}. Убедитесь, что файл находится в папке pct/")
        exit()

player_tank_img = cv2.resize(player_tank_img, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
enemy_tank_img = cv2.resize(enemy_tank_img, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
brick_wall_img = cv2.resize(brick_wall_img, (tile_size, tile_size), interpolation=cv2.INTER_AREA)
steel_wall_img = cv2.resize(steel_wall_img, (tile_size, tile_size), interpolation=cv2.INTER_AREA)

class Tank:
    def __init__(self, x, y, color, direction=0, is_player=False):
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.is_player = is_player
        self.alive = True
        self.bullet = None
        self.invincible = False
        self.invincible_start = 0
        self.visible = True

    def move(self, dx, dy, level):
        new_x = self.x + dx
        new_y = self.y + dy
        if not check_collision(new_x, new_y, level):
            self.x = new_x
            self.y = new_y

    def shoot(self):
        if self.invincible:
            return
        if self.bullet is None or not self.bullet.active:
            bx, by = self.x, self.y
            if self.direction == 0: by -= tile_size
            elif self.direction == 1: bx += tile_size
            elif self.direction == 2: by += tile_size
            elif self.direction == 3: bx -= tile_size
            self.bullet = Bullet(bx, by, self.direction)

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.active = True

    def move(self):
        if self.direction == 0: self.y -= bullet_speed
        elif self.direction == 1: self.x += bullet_speed
        elif self.direction == 2: self.y += bullet_speed
        elif self.direction == 3: self.x -= bullet_speed
        if self.x < 0 or self.x > game_field_width or self.y < 0 or self.y > game_field_height:
            self.active = False

def check_collision(x, y, level):
    corners = [
        (x, y),
        (x + tile_size - 1, y),
        (x, y + tile_size - 1),
        (x + tile_size - 1, y + tile_size - 1)
    ]
    for corner_x, corner_y in corners:
        grid_x = int(corner_x // tile_size)
        grid_y = int(corner_y // tile_size)
        if grid_x < 0 or grid_x >= len(level[0]) or grid_y < 0 or grid_y >= len(level):
            return True
        if level[grid_y][grid_x] in [1, 2, 4]:
            return True
    return False

def overlay_image_alpha(img, img_overlay, x, y, direction):
    if direction == 0:
        rotated = img_overlay
    elif direction == 1:
        rotated = cv2.rotate(img_overlay, cv2.ROTATE_90_CLOCKWISE)
    elif direction == 2:
        rotated = cv2.rotate(img_overlay, cv2.ROTATE_180)
    elif direction == 3:
        rotated = cv2.rotate(img_overlay, cv2.ROTATE_90_COUNTERCLOCKWISE)

    h, w = rotated.shape[:2]
    x, y = int(x), int(y)

    if x < 0 or y < 0 or x + w > img.shape[1] or y + h > img.shape[0]:
        return img

    if rotated.shape[2] == 4:
        alpha = rotated[:, :, 3] / 255.0
        color = rotated[:, :, :3]
        
        roi = img[y:y+h, x:x+w]
        for c in range(0, 3):
            roi[:, :, c] = roi[:, :, c] * (1 - alpha) + color[:, :, c] * alpha
        img[y:y+h, x:x+w] = roi
    else:
        img[y:y+h, x:x+w] = rotated

    return img

def draw_game(frame, player, enemies, level, base_alive, score, lives, current_level, enemies_left):
    window_width = frame.shape[1]
    window_height = frame.shape[0]
    background = cv2.resize(background_image, (window_width, window_height), interpolation=cv2.INTER_AREA)
    frame[:] = background

    game_frame = np.zeros((game_field_height, game_field_width, 3), dtype=np.uint8)
    
    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[y][x] == 1:
                game_frame[y*tile_size:(y+1)*tile_size, x*tile_size:(x+1)*tile_size] = brick_wall_img
            elif level[y][x] == 2:
                game_frame[y*tile_size:(y+1)*tile_size, x*tile_size:(x+1)*tile_size] = steel_wall_img
            elif level[y][x] == 4:
                temp = brick_wall_img.copy()
                temp = (temp * 0.5).astype(np.uint8)
                game_frame[y*tile_size:(y+1)*tile_size, x*tile_size:(x+1)*tile_size] = temp
            elif level[y][x] == 3 and base_alive:
                cv2.rectangle(game_frame, (x * tile_size, y * tile_size),
                            ((x + 1) * tile_size, (y + 1) * tile_size), green, -1)

    if player.alive and (not player.invincible or player.visible):
        game_frame = overlay_image_alpha(game_frame, player_tank_img, player.x, player.y, player.direction)

    for enemy in enemies:
        if enemy.alive:
            game_frame = overlay_image_alpha(game_frame, enemy_tank_img, enemy.x, enemy.y, enemy.direction)

    if player.bullet and player.bullet.active:
        cv2.circle(game_frame, (int(player.bullet.x + tile_size // 2), int(player.bullet.y + tile_size // 2)), 3 * scale_factor, white, -1)
    for enemy in enemies:
        if enemy.bullet and enemy.bullet.active:
            cv2.circle(game_frame, (int(enemy.bullet.x + tile_size // 2), int(enemy.bullet.y + tile_size // 2)), 3 * scale_factor, white, -1)

    cv2.rectangle(game_frame, (0, 0), (game_field_width - 1, game_field_height - 1), green, 2 * scale_factor)

    offset_x = (window_width - game_field_width) // 2
    offset_y = (window_height - game_field_height) // 2
    frame[offset_y:offset_y + game_field_height, offset_x:offset_x + game_field_width] = game_frame

    cv2.rectangle(frame, (window_width // 2 - 80 * scale_factor, 10 * scale_factor - 10 * scale_factor),
                  (window_width // 2 + 80 * scale_factor, 30 * scale_factor + 10 * scale_factor), black, -1)
    cv2.rectangle(frame, (window_width // 2 - 80 * scale_factor, 10 * scale_factor - 10 * scale_factor),
                  (window_width // 2 + 80 * scale_factor, 30 * scale_factor + 10 * scale_factor), white, 2 * scale_factor)
    cv2.putText(frame, f"score: {score}", (window_width // 2 - 70 * scale_factor, 30 * scale_factor), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7 * scale_factor, white, 2 * scale_factor)

    cv2.rectangle(frame, (offset_x + 10 * scale_factor, window_height - 30 * scale_factor),
                  (offset_x + 10 * scale_factor + tile_size, window_height - 30 * scale_factor + tile_size), yellow, -1)
    cv2.putText(frame, f"x {lives}", (offset_x + 30 * scale_factor, window_height - 20 * scale_factor), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7 * scale_factor, white, 2 * scale_factor)
    cv2.putText(frame, f"level: {current_level + 1}", (offset_x + game_field_width // 2 - 20 * scale_factor, window_height - 20 * scale_factor), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7 * scale_factor, white, 2 * scale_factor)
    cv2.rectangle(frame, (offset_x + game_field_width - 90 * scale_factor, window_height - 30 * scale_factor),
                  (offset_x + game_field_width - 90 * scale_factor + tile_size, window_height - 30 * scale_factor + tile_size), blue, -1)
    cv2.putText(frame, f"x {enemies_left}", (offset_x + game_field_width - 70 * scale_factor, window_height - 20 * scale_factor), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7 * scale_factor, white, 2 * scale_factor)

def handle_bullets(player, enemies, level, base_alive):
    score = 0
    hit = False
    current_time = time.time()
    if player.bullet and player.bullet.active:
        bx, by = player.bullet.x // tile_size, player.bullet.y // tile_size
        if 0 <= bx < len(level[0]) and 0 <= by < len(level):
            if level[int(by)][int(bx)] == 1:
                level[int(by)][int(bx)] = 4
                player.bullet.active = False
            elif level[int(by)][int(bx)] == 4:
                level[int(by)][int(bx)] = 0
                player.bullet.active = False
            elif level[int(by)][int(bx)] == 3 and base_alive:
                base_alive = False
                player.bullet.active = False
            elif level[int(by)][int(bx)] == 2:
                player.bullet.active = False
        for enemy in enemies:
            if enemy.alive and abs(player.bullet.x - enemy.x) < tile_size and abs(player.bullet.y - enemy.y) < tile_size:
                enemy.alive = False
                player.bullet.active = False
                score += 100
        player.bullet.move()
    for enemy in enemies:
        if enemy.bullet and enemy.bullet.active:
            bx, by = enemy.bullet.x // tile_size, enemy.bullet.y // tile_size
            if 0 <= bx < len(level[0]) and 0 <= by < len(level):
                if level[int(by)][int(bx)] == 1:
                    level[int(by)][int(bx)] = 4
                    enemy.bullet.active = False
                elif level[int(by)][int(bx)] == 4:
                    level[int(by)][int(bx)] = 0
                    enemy.bullet.active = False
                elif level[int(by)][int(bx)] == 3 and base_alive:
                    base_alive = False
                    enemy.bullet.active = False
                elif level[int(by)][int(bx)] == 2:
                    enemy.bullet.active = False
            if player.alive and not player.invincible and abs(enemy.bullet.x - player.x) < tile_size and abs(enemy.bullet.y - player.y) < tile_size:
                player.invincible = True
                player.invincible_start = current_time
                enemy.bullet.active = False
                hit = True
            enemy.bullet.move()
    if player.invincible:
        if current_time - player.invincible_start >= 1:
            player.invincible = False
            player.visible = True
        else:
            player.visible = int(current_time * 10) % 2 == 0
    return score, base_alive, hit

def wait_for_exit():
    while True:
        key = cv2.waitKey(0)
        if key in [ord('q'), ord('й'), 27, 32, 13]:
            return True

def main():
    cv2.namedWindow("Tank Battalion", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Tank Battalion", 1000, 562)
    fullscreen = False

    selected_level = show_menu(1000, 562, background_image, len(LEVELS))
    if selected_level == -1:
        cv2.destroyAllWindows()
        return

    score = 0
    lives = 3
    current_level = selected_level

    while current_level < len(LEVELS):
        level = copy.deepcopy(LEVELS[current_level])
        
        grid_size = (len(level[0]), len(level))
        global game_field_width, game_field_height
        game_field_width = grid_size[0] * tile_size
        game_field_height = grid_size[1] * tile_size
        frame = np.zeros((562, 1000, 3), dtype=np.uint8)
        
        eagle_x, eagle_y = None, None
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 3:
                    eagle_x, eagle_y = x, y
                    break
            if eagle_x is not None:
                break
        
        player_x = eagle_x * tile_size
        player_y = (eagle_y - 2) * tile_size
        player = Tank(player_x, player_y, yellow, 0, True)
        
        enemies = []
        base_alive = True
        last_spawn = time.time()
        enemies_killed = 0
        enemies_spawned = 0
        enemies_left = max_enemies
        enemy_speed = base_enemy_speed + (current_level * (tank_speed - base_enemy_speed) / 9)
        if current_level >= 10:
            enemy_speed += ((current_level - 9) * (tank_speed * 0.5) / 10)

        while True:
            draw_game(frame, player, enemies, level, base_alive, score, lives, current_level, enemies_left)
            cv2.imshow("Tank Battalion", frame)
            key = cv2.waitKey(30)

            if key in [ord('w'), ord('ц'), 2490368, 82, 72]:
                player.direction = 0
                player.move(0, -tank_speed, level)
            elif key in [ord('s'), ord('ы'), 2621440, 84, 80]:
                player.direction = 2
                player.move(0, tank_speed, level)
            elif key in [ord('a'), ord('ф'), 2424832, 81, 75]:
                player.direction = 3
                player.move(-tank_speed, 0, level)
            elif key in [ord('d'), ord('в'), 2555904, 83, 77]:
                player.direction = 1
                player.move(tank_speed, 0, level)
            elif key in [ord(' '), 32]:
                player.shoot()
            elif key in [ord('q'), ord('й'), 27]:
                cv2.destroyAllWindows()
                return
            elif key == ord('f'):
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty("Tank Battalion", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty("Tank Battalion", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow("Tank Battalion", 1000, 562)

            if time.time() - last_spawn > enemy_spawn_interval and len([e for e in enemies if e.alive]) < 4 and enemies_spawned < max_enemies:
                spawn_x = np.random.choice([2, grid_size[0]-2]) * tile_size
                spawn_y = 2 * tile_size
                while check_collision(spawn_x, spawn_y, level):
                    spawn_x = np.random.choice([2, grid_size[0]-2]) * tile_size
                    spawn_y = 2 * tile_size
                enemies.append(EnemyTank(spawn_x, spawn_y, blue, np.random.randint(0, 4), tile_size, enemy_speed))
                last_spawn = time.time()
                enemies_spawned += 1

            eagle_center_x = eagle_x * tile_size + tile_size // 2
            eagle_center_y = eagle_y * tile_size + tile_size // 2
            update_enemies(enemies, player, level, eagle_center_x, eagle_center_y, tile_size, grid_size, time.time(), Bullet)

            added_score, base_alive, hit = handle_bullets(player, enemies, level, base_alive)
            score += added_score
            enemies_killed += added_score // 100
            enemies_left = max_enemies - enemies_killed

            if hit:
                lives -= 1
                if lives <= 0:
                    draw_game_over(frame, background_image, brick_wall_img, steel_wall_img, player_tank_img, enemy_tank_img, tile_size, overlay_image_alpha, white, score)
                    cv2.imshow("Tank Battalion", frame)
                    wait_for_exit()
                    cv2.destroyAllWindows()
                    return

            if enemies_killed >= max_enemies:
                current_level += 1
                break

            if not base_alive:
                draw_game_over(frame, background_image, brick_wall_img, steel_wall_img, player_tank_img, enemy_tank_img, tile_size, overlay_image_alpha, white, score)
                cv2.imshow("Tank Battalion", frame)
                wait_for_exit()
                cv2.destroyAllWindows()
                return

    draw_win(frame, score, background_image, player_tank_img, tile_size, overlay_image_alpha, white)
    cv2.imshow("Tank Battalion", frame)
    wait_for_exit()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()