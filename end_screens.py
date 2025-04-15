import cv2
import numpy as np

def draw_game_over(frame, background_image, brick_wall_img, steel_wall_img, player_tank_img, enemy_tank_img, tile_size, overlay_image_alpha, white, score):
    window_width, window_height = frame.shape[1], frame.shape[0]
    frame[:] = 0

    game_over_grid = [
        [[0, 2, 2, 2, 0], [1, 0, 0, 0, 0], [1, 0, 0, 4, 4], [1, 0, 0, 0, 3], [0, 1, 1, 1, 0]],
        [[0, 1, 1, 1, 0], [2, 0, 0, 0, 1], [2, 2, 2, 2, 2], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1]],
        [[1, 0, 0, 0, 1], [1, 1, 0, 1, 1], [1, 0, 4, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 3]],
        [[2, 2, 2, 2, 2], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0], [2, 2, 2, 2, 2]],
        [[0, 1, 1, 1, 0], [1, 0, 0, 0, 1], [1, 0, 0, 0, 4], [1, 0, 0, 0, 1], [0, 1, 1, 1, 0]],
        [[1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [0, 2, 0, 1, 0], [0, 0, 1, 0, 0]],
        [[1, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1]],
        [[1, 1, 1, 1, 0], [1, 0, 0, 0, 1], [2, 2, 2, 2, 0], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1]],
    ]

    tile_size_scaled = tile_size
    letter_width = 5 * tile_size_scaled
    letter_height = 5 * tile_size_scaled
    spacing = tile_size_scaled
    start_x = (window_width - (4 * letter_width + 3 * spacing)) // 2
    start_y = (window_height - (2 * letter_height + spacing)) // 2

    for letter_idx, letter in enumerate(game_over_grid):
        row = letter_idx // 4
        col = letter_idx % 4
        pos_x = start_x + col * (letter_width + spacing)
        pos_y = start_y + row * (letter_height + spacing)

        if pos_x < 0 or pos_y < 0 or pos_x + letter_width > window_width or pos_y + letter_height > window_height:
            continue

        for y in range(5):
            for x in range(5):
                if letter[y][x] == 0:
                    continue
                px = pos_x + x * tile_size_scaled
                py = pos_y + y * tile_size_scaled
                if letter[y][x] == 1:
                    resized_img = cv2.resize(brick_wall_img, (tile_size_scaled, tile_size_scaled))
                    frame[py:py + tile_size_scaled, px:px + tile_size_scaled] = resized_img
                elif letter[y][x] == 2:
                    resized_img = cv2.resize(steel_wall_img, (tile_size_scaled, tile_size_scaled))
                    frame[py:py + tile_size_scaled, px:px + tile_size_scaled] = resized_img
                elif letter[y][x] == 3:
                    frame = overlay_image_alpha(frame, cv2.resize(player_tank_img, (tile_size_scaled, tile_size_scaled)), px, py, 0)
                elif letter[y][x] == 4:
                    frame = overlay_image_alpha(frame, cv2.resize(enemy_tank_img, (tile_size_scaled, tile_size_scaled)), px, py, 0)

    cv2.putText(frame, f"Score: {score}", (window_width // 2 - 50, start_y + 2 * letter_height + spacing + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)
    cv2.putText(frame, "Press Q, Space, Esc, or Enter to exit", (window_width // 2 - 150, window_height - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 1)

def draw_win(frame, score, background_image, player_tank_img, tile_size, overlay_image_alpha, white):
    window_width, window_height = frame.shape[1], frame.shape[0]
    frame[:] = 0

    win_grid = [
        [[3, 0, 0, 0, 3], [3, 0, 0, 0, 3], [3, 0, 3, 0, 3], [3, 3, 0, 3, 3], [3, 0, 0, 0, 3]],
        [[0, 3, 3, 3, 0], [0, 0, 3, 0, 0], [0, 0, 3, 0, 0], [0, 0, 3, 0, 0], [0, 3, 3, 3, 0]],
        [[3, 0, 0, 0, 3], [3, 3, 0, 0, 3], [3, 0, 3, 0, 3], [3, 0, 0, 3, 3], [3, 0, 0, 0, 3]],
    ]

    tile_size_scaled = tile_size * 2
    letter_width = 5 * tile_size_scaled
    letter_height = 5 * tile_size_scaled
    spacing = tile_size_scaled
    start_x = (window_width - (3 * letter_width + 2 * spacing)) // 2
    start_y = (window_height - letter_height - 50) // 2

    for letter_idx, letter in enumerate(win_grid):
        pos_x = start_x + letter_idx * (letter_width + spacing)
        pos_y = start_y

        if pos_x < 0 or pos_y < 0 or pos_x + letter_width > window_width or pos_y + letter_height > window_height:
            continue

        for y in range(5):
            for x in range(5):
                if letter[y][x] == 0:
                    continue
                px = pos_x + x * tile_size_scaled
                py = pos_y + y * tile_size_scaled
                frame = overlay_image_alpha(frame, cv2.resize(player_tank_img, (tile_size_scaled, tile_size_scaled)), px, py, 0)

    cv2.putText(frame, f"Score: {score}", (window_width // 2 - 50, start_y + letter_height + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, white, 2)
    cv2.putText(frame, "Press Q, Space, Esc, or Enter to exit", (window_width // 2 - 150, window_height - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 1)