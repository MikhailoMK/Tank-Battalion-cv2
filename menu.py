import cv2
import numpy as np

def show_menu(window_width, window_height, background_image, total_levels):
    frame = np.zeros((window_height, window_width, 3), dtype=np.uint8)
    background = cv2.resize(background_image, (window_width, window_height), interpolation=cv2.INTER_AREA)
    frame[:] = background

    cv2.putText(frame, "TANK BATTALION", (window_width // 2 - 150, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.putText(frame, "Select Level:", (window_width // 2 - 100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    levels_per_row = (total_levels + 1) // 2
    selected_level = 0
    mouse_hovered_level = -1

    def get_level_position(level_idx):
        row = level_idx // levels_per_row
        col = level_idx % levels_per_row
        x = window_width // 4 + col * 100
        y = 250 + row * 60
        return x, y

    def mouse_callback(event, x, y, flags, param):
        nonlocal selected_level, mouse_hovered_level
        mouse_hovered_level = -1
        for i in range(total_levels):
            lx, ly = get_level_position(i)
            if lx - 50 <= x <= lx + 50 and ly - 20 <= y <= ly + 20:
                mouse_hovered_level = i
                if event == cv2.EVENT_LBUTTONDOWN:
                    selected_level = i
                    return selected_level
                break
        return None

    cv2.setMouseCallback("Tank Battalion", mouse_callback)

    while True:
        frame_copy = frame.copy()
        
        for i in range(total_levels):
            level_text = f"Level {i + 1}"
            x, y = get_level_position(i)
            color = (0, 255, 255) if i == selected_level else (255, 255, 0) if i == mouse_hovered_level else (255, 255, 255)
            cv2.putText(frame_copy, level_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        cv2.putText(frame_copy, "Use WASD or Mouse, ENTER to start", 
                    (window_width // 2 - 150, window_height - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("Tank Battalion", frame_copy)
        key = cv2.waitKey(30)

        if key in [ord('w'), ord('ц'), 2490368, 82, 72]:
            selected_level = (selected_level - levels_per_row) % total_levels
        elif key in [ord('s'), ord('ы'), 2621440, 84, 80]:
            selected_level = (selected_level + levels_per_row) % total_levels
        elif key in [ord('a'), ord('ф'), 2424832, 81, 75]:
            selected_level = (selected_level - 1) % total_levels
        elif key in [ord('d'), ord('в'), 2555904, 83, 77]:
            selected_level = (selected_level + 1) % total_levels
        elif key in [13, 32]:
            return selected_level
        elif key in [ord('q'), ord('й'), 27]:
            return -1