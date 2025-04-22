from config import CELL_SIZE, BOARD_SIZE, SHOW_GRID, GAME_MODE

import pygame
import sys
import random
import math
import json

def initialize_board():
    
    num_pairs = (BOARD_SIZE * BOARD_SIZE) // 2
    entities = list(range(num_pairs)) * 2
    random.shuffle(entities)
    board = [entities[i * BOARD_SIZE:(i + 1) * BOARD_SIZE] for i in range(BOARD_SIZE)]
    return board

def get_pair_cells(board):
    
    pairs = set()
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            value = board[y][x]
            if x < BOARD_SIZE - 1 and board[y][x+1] == value:
                pairs.add((x, y))
                pairs.add((x+1, y))
            if y < BOARD_SIZE - 1 and board[y+1][x] == value:
                pairs.add((x, y))
                pairs.add((x, y+1))
    return pairs

def draw_board(screen, board, selected_cells, hovered_cell=None):
    
    colors = [
        (200, 100, 100),   
        (100, 200, 100),   
        (100, 100, 200),   
        (200, 200, 100),   
        (200, 100, 200),   
        (100, 200, 200),   
        (170, 150, 120),   
        (150, 150, 150)    
    ]
    font = pygame.font.SysFont(None, 36)
    pair_set = set()
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            current = board[y][x]
            if x < BOARD_SIZE - 1 and board[y][x + 1] == current:
                pair_set.add((x, y))
                pair_set.add((x + 1, y))
            if y < BOARD_SIZE - 1 and board[y + 1][x] == current:
                pair_set.add((x, y))
                pair_set.add((x, y + 1))
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            value = board[y][x]
            color = colors[value % len(colors)]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            if SHOW_GRID and (x, y) not in pair_set:
                pygame.draw.rect(screen, (0,0,0), rect, 2)
            txt = font.render(str(value), True, (0,0,0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
            if (x, y) in selected_cells:
                pygame.draw.rect(screen, (255,255,255), rect, 5)
    drawn = set()
    pair_border_color = (0,0,0)
    pair_border_thickness = 5
    pad = 5
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            current = board[y][x]
            if x < BOARD_SIZE - 1 and board[y][x+1] == current:
                pair = tuple(sorted(((x, y),(x+1,y))))
                if pair not in drawn:
                    drawn.add(pair)
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, 2*CELL_SIZE, CELL_SIZE)
                    inner_rect = rect.inflate(-pad*2, -pad*2)
                    pygame.draw.rect(screen, pair_border_color, inner_rect, pair_border_thickness)
            if y < BOARD_SIZE - 1 and board[y+1][x] == current:
                pair = tuple(sorted(((x, y),(x,y+1))))
                if pair not in drawn:
                    drawn.add(pair)
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, 2*CELL_SIZE)
                    inner_rect = rect.inflate(-pad*2, -pad*2)
                    pygame.draw.rect(screen, pair_border_color, inner_rect, pair_border_thickness)

    
    if not selected_cells and hovered_cell is not None:
        hx, hy = hovered_cell
        hovered_value = board[hy][hx]
        highlight_set = {(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if board[y][x] == hovered_value}
        
        blink = (math.sin(pygame.time.get_ticks() * 0.0025 * math.pi) + 1) / 2
        alpha = int(50 + 50 * blink)
        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, alpha))
        for (cx, cy) in highlight_set:
            cell_rect = pygame.Rect(cx * CELL_SIZE, cy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            screen.blit(overlay, cell_rect)

    
    if len(selected_cells) == 1 and hovered_cell is not None:
        sx, sy = selected_cells[0]
        hx, hy = hovered_cell
        diff = max(abs(hx - sx), abs(hy - sy))
        if diff == 0:
            diff = 1
        fx = sx + (diff if (hx - sx) >= 0 else -diff)
        fy = sy + (diff if (hy - sy) >= 0 else -diff)
        top_left = (min(sx, fx), min(sy, fy))
        bottom_right = (max(sx, fx), max(sy, fy))
        region_rect = pygame.Rect(top_left[0]*CELL_SIZE, top_left[1]*CELL_SIZE, (diff+1)*CELL_SIZE, (diff+1)*CELL_SIZE)
        pygame.draw.rect(screen, (255,255,255), region_rect, 3)

def ease_out_cubic(t):
    return 1 - (1 - t)**3

def animate_rotation(board, top_left, bottom_right, screen):
    x1, y1 = top_left
    x2, y2 = bottom_right
    side = x2 - x1 + 1
    region_size = side * CELL_SIZE

    anim_colors = [
        (200, 100, 100),   
        (100, 200, 100),   
        (100, 100, 200),   
        (200, 200, 100),   
        (200, 100, 200),   
        (100, 200, 200),   
        (170, 150, 120),   
        (150, 150, 150)    
    ]
    font = pygame.font.SysFont(None, 36)
    region_board = [ row[x1:x2+1] for row in board[y1:y2+1] ]
    anim_duration = 700
    start_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        elapsed = pygame.time.get_ticks() - start_time
        t = min(elapsed / anim_duration, 1)
        angle = ease_out_cubic(t) * 90

        region_surface = pygame.Surface((region_size, region_size))
        for i in range(side):
            for j in range(side):
                val = region_board[i][j]
                cell_color = anim_colors[val % len(anim_colors)]
                cell_rect = pygame.Rect(j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(region_surface, cell_color, cell_rect)
                pygame.draw.rect(region_surface, (0,0,0), cell_rect, 2)
                txt = font.render(str(val), True, (0,0,0))
                txt_rect = txt.get_rect(center=cell_rect.center)
                region_surface.blit(txt, txt_rect)

        rotated_surf = pygame.transform.rotate(region_surface, -angle)
        rot_rect = rotated_surf.get_rect(center=(x1*CELL_SIZE + region_size//2, y1*CELL_SIZE + region_size//2))

        screen.fill((255,255,255))
        draw_board(screen, board, [])
        screen.blit(rotated_surf, rot_rect)
        pygame.display.flip()
        clock.tick(30)  

        if t >= 1:
            break

    board = rotate_square(board, top_left, bottom_right)
    return board

def rotate_square(board, top_left, bottom_right):
    x1, y1 = top_left
    x2, y2 = bottom_right
    side = x2 - x1 + 1
    if side != (y2 - y1 + 1) or x1 < 0 or y1 < 0 or x2 >= BOARD_SIZE or y2 >= BOARD_SIZE:
        print("Warning: 選択された領域が正方形ではないか、はみ出しています。")
        return board
    square = [row[x1:x2 + 1] for row in board[y1:y2 + 1]]
    rotated = list(zip(*square[::-1]))
    for i in range(side):
        board[y1 + i][x1:x2 + 1] = rotated[i]
    return board

def count_pairs(board):
    count = 0
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            current = board[y][x]
            if x < BOARD_SIZE - 1 and board[y][x + 1] == current:
                count += 1
            if y < BOARD_SIZE - 1 and board[y + 1][x] == current:
                count += 1
    return count

def interface_run():
    global BOARD_SIZE  
    pygame.init()
    screen = pygame.display.set_mode((CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE))
    pygame.display.set_caption("高専プロコン シミュレーション")
    selected = []
    clock = pygame.time.Clock()

    
    if GAME_MODE["problemInput"] == "Import":
        try:
            with open("./problem.json", encoding="utf-8") as f:
                p_data = json.load(f)
            if p_data.get("problem") and p_data["problem"].get("field"):
                field = p_data["problem"]["field"]
                if "size" in field and "entities" in field:
                    BOARD_SIZE = field["size"]  
                    board = field["entities"]
                    screen = pygame.display.set_mode((CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE))  
                else:
                    print("Warning: 不正なフィールドデータです。ランダム生成に切り替えます。")
                    board = initialize_board()
            else:
                print("Warning: 不正な問題フォーマットです。ランダム生成に切り替えます。")
                board = initialize_board()
        except Exception as e:
            print("Problem.json の読み込みに失敗しました:", e)
            board = initialize_board()
    else:
        board = initialize_board()

    
    if GAME_MODE["operation"] == "RePlay":
        try:
            with open(r"./best_ops.json", encoding="utf-8") as f:
                data = json.load(f)
            ops = data.get("ops", [])
            
            if "size" in data:
                BOARD_SIZE = data["size"]
                screen = pygame.display.set_mode((CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE))
        except Exception as e:
            print("data.json の読み込みに失敗しました:", e)
            ops = []

        for op in ops:
            x = op.get("x")
            y = op.get("y")
            n = op.get("n")
            if x is None or y is None or n is None:
                print("Warning: 無効な操作が含まれています。")
                continue
            top_left = (x, y)
            bottom_right = (x + n - 1, y + n - 1)
            if bottom_right[0] < BOARD_SIZE and bottom_right[1] < BOARD_SIZE:
                board = animate_rotation(board, top_left, bottom_right, screen)
                print("現在のペア数:", count_pairs(board))
                pygame.time.wait(500)
            else:
                print("Warning: 操作が盤面外です。", op)

        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.fill((255, 255, 255))
            draw_board(screen, board, [])
            pygame.display.flip()
            clock.tick(30)
    else:
        
        while True:
            hovered_cell = None
            mx, my = pygame.mouse.get_pos()
            hovered_cell = (mx // CELL_SIZE, my // CELL_SIZE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    cell = (mx // CELL_SIZE, my // CELL_SIZE)
                    if len(selected) == 0:
                        selected.append(cell)
                    elif len(selected) == 1:
                        selected.append(cell)
                        sx, sy = selected[0]
                        ex, ey = selected[1]
                        diff = max(abs(ex - sx), abs(ey - sy))
                        if diff == 0:
                            diff = 1
                        fx = sx + (diff if (ex-sx) >= 0 else -diff)
                        fy = sy + (diff if (ey-sy) >= 0 else -diff)
                        top_left = (min(sx, fx), min(sy, fy))
                        bottom_right = (max(sx, fx), max(sy, fy))
                        if bottom_right[0] < BOARD_SIZE and bottom_right[1] < BOARD_SIZE:
                            board = animate_rotation(board, top_left, bottom_right, screen)
                            print("現在のペア数:", count_pairs(board))
                        else:
                            print("Warning: 選択された園が盤面からはみ出しています。")
                        selected = []
            screen.fill((255, 255, 255))
            draw_board(screen, board, selected, hovered_cell)
            pygame.display.flip()
            clock.tick(30)



