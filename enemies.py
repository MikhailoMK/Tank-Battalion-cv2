import numpy as np

class EnemyTank:
    def __init__(self, x, y, color, direction, tile_size, enemy_speed):
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.alive = True
        self.bullet = None
        self.tile_size = tile_size
        self.speed = enemy_speed
        self.last_direction_change = 0
        self.direction_change_interval = 1.0

    def shoot(self, Bullet):
        if self.bullet is None or not self.bullet.active:
            bx, by = self.x, self.y
            if self.direction == 0: by -= self.tile_size
            elif self.direction == 1: bx += self.tile_size
            elif self.direction == 2: by += self.tile_size
            elif self.direction == 3: bx -= self.tile_size
            self.bullet = Bullet(bx, by, self.direction)

def has_clear_path(start_x, start_y, target_x, target_y, level, tile_size, grid_size):
    dx = abs(target_x - start_x)
    dy = abs(target_y - start_y)
    sx = 1 if start_x < target_x else -1
    sy = 1 if start_y < target_y else -1
    err = dx - dy

    x, y = start_x, start_y
    while True:
        grid_x = int(x // tile_size)
        grid_y = int(y // tile_size)
        if 0 <= grid_x < len(level[0]) and 0 <= grid_y < len(level):
            if level[grid_y][grid_x] in [1, 2, 4]:
                return False
        if abs(x - target_x) < tile_size and abs(y - target_y) < tile_size:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return True

def check_collision(x, y, level, tile_size, grid_size):
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

def update_enemies(enemies, player, level, eagle_x, eagle_y, tile_size, grid_size, current_time, Bullet):
    for enemy in enemies:
        if not enemy.alive:
            continue

        if current_time - enemy.last_direction_change >= enemy.direction_change_interval:
            dx = eagle_x - enemy.x
            dy = eagle_y - enemy.y
            if abs(dx) > abs(dy):
                enemy.direction = 1 if dx > 0 else 3
            else:
                enemy.direction = 2 if dy > 0 else 0
            enemy.last_direction_change = current_time

        new_x, new_y = enemy.x, enemy.y
        if enemy.direction == 0:
            new_y -= enemy.speed
        elif enemy.direction == 1:
            new_x += enemy.speed
        elif enemy.direction == 2:
            new_y += enemy.speed
        elif enemy.direction == 3:
            new_x -= enemy.speed

        if check_collision(new_x, new_y, level, tile_size, grid_size):
            enemy.shoot(Bullet)
            directions = [0, 1, 2, 3]
            directions.remove(enemy.direction)
            enemy.direction = np.random.choice(directions)
        else:
            enemy.x, enemy.y = new_x, new_y

        if abs(enemy.x - player.x) < tile_size and has_clear_path(enemy.x + tile_size // 2, enemy.y + tile_size // 2, player.x, player.y, level, tile_size, grid_size):
            enemy.shoot(Bullet)
        elif abs(enemy.y - player.y) < tile_size and has_clear_path(enemy.x + tile_size // 2, enemy.y + tile_size // 2, player.x, player.y, level, tile_size, grid_size):
            enemy.shoot(Bullet)