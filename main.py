import json
import sqlite3
from customtkinter import *
import pygame
import random
from queue import Queue
import time
import os


conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        field_data TEXT,
        covered_field TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        resultOfgame TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

conn.commit()

def save_game_result(user_id, result):
    cursor.execute('INSERT INTO results (user_id, resultOfgame) VALUES (?, ?)', (user_id, result))
    conn.commit()
    print("Game result saved!")

def save_game(user_id, field_data, cover_field):
    serialized_field_data = json.dumps(field_data)
    serialized_cover_field = json.dumps(cover_field)

    cursor.execute('SELECT COUNT(*) FROM games WHERE user_id = ?', (user_id,))
    saved_games_count = cursor.fetchone()[0]

    if saved_games_count >= 1:
        cursor.execute('SELECT id FROM games WHERE user_id = ? ORDER BY id ASC LIMIT 1', (user_id,))
        oldest_game_id = cursor.fetchone()[0]

        cursor.execute('UPDATE games SET field_data = ?, covered_field = ? WHERE id = ?',
                       (serialized_field_data, serialized_cover_field, oldest_game_id))
        conn.commit()
        print("Oldest save updated!")
    else:
        cursor.execute('INSERT INTO games (user_id, field_data, covered_field) VALUES (?, ?, ?)',
                       (user_id, serialized_field_data, serialized_cover_field))
        conn.commit()
        print("Game saved!")

def register():
    new_username = input_new_username.get()
    new_password = input_new_password.get()

    cursor.execute('SELECT * FROM users WHERE username = ?', (new_username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Username already exists. Please choose a different username.")
    else:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, new_password))
        conn.commit()
        print("Registration successful!")
        show_login_form()

def login():
    global user_id

    username = input_username.get()
    password = input_password.get()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        print("Login successful!")
        app.withdraw()
        menu.deiconify()
    else:
        print("Invalid username or password.")
def show_login_form():
    reg.withdraw()
    app.deiconify()

def new_game():
    menu.withdraw()
    menu_level.deiconify()

def easy_game():
    global ROWS, COLS, BOMBS, SIZE
    menu_level.withdraw()
    WIDTH, HEIGHT = 500, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SHOWN)
    ROWS, COLS = 9, 9
    BOMBS = 10
    SIZE = int((WIDTH // ROWS))
    main(False, 0,0)

def medium_game():
    global ROWS, COLS, BOMBS, SIZE
    menu_level.withdraw()
    WIDTH, HEIGHT = 500, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SHOWN)
    ROWS, COLS = 16, 16
    BOMBS = 40
    SIZE = int((WIDTH // ROWS))
    main(False, 0,0)

def advanced_game():
    global ROWS, COLS, BOMBS, SIZE
    menu_level.withdraw()
    WIDTH, HEIGHT = 925, 800
    win = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SHOWN)
    ROWS, COLS = 16, 30
    BOMBS = 90
    SIZE = int((500 // ROWS))
    main(False, 0,0)
def load_game():
    global user_id,SIZE

    cursor.execute('SELECT field_data, covered_field FROM games WHERE user_id = ? ORDER BY id DESC', (user_id,))
    saved_game = cursor.fetchone()

    if saved_game:
        serialized_field_data, serialized_covered_field = saved_game
        field_data = json.loads(serialized_field_data)
        saved_covered_field = json.loads(serialized_covered_field)

        if field_data and saved_covered_field:
            TF = True
            menu.withdraw()

            lenth = len(saved_covered_field[0])
            if lenth > 25 :
                WIDTH, HEIGHT = 925, 800
                SIZE = int((500 // 16))
            elif lenth > 10:
                WIDTH, HEIGHT = 500, 600
                SIZE = int((500 // 16))
            else:
                WIDTH, HEIGHT = 500, 600
                SIZE = int((500 // 9))
            win = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SHOWN)
            main(TF, field_data, saved_covered_field)
    else:
        print("No saved game found.")


def rat_games():
    global user_id

    cursor.execute('SELECT resultOfgame FROM results WHERE user_id = ? ORDER BY id DESC LIMIT 10', (user_id,))
    user_results = cursor.fetchall()

    for widget in rating_window.winfo_children():
        widget.destroy()

    label_title = CTkLabel(master=rating_window, text="Last 10 Game Results:", font=("Arial", 16), text_color="white")
    label_title.pack()

    for result in user_results:
        result_text = f"Result: {result[0]}"
        label_result = CTkLabel(master=rating_window, text=result_text, font=("Arial", 12), text_color="white")
        label_result.pack()

    btn_back = CTkButton(master=rating_window, text="Back", corner_radius=32, hover_color="#6666FF",width=50,
                         command=back_to_menu)
    btn_back.place(relx=0.965, rely=0.05, anchor="center")

    rating_window.deiconify()
    menu.withdraw()

def back_to_menu():
    menu.deiconify()
    rating_window.withdraw()


def show_register_form():
    app.withdraw()
    reg.deiconify()

app = CTk()
app.geometry("500x400")

label_username = CTkLabel(master=app, text="Username", font=("Arial", 16), text_color="white")
input_username = CTkEntry(master=app, corner_radius=32, width=300, text_color="white")
label_password = CTkLabel(master=app, text="Password", font=("Arial", 16), text_color="white")
input_password = CTkEntry(master=app, corner_radius=32, width=300, text_color="white")
btn_login = CTkButton(master=app, text="Login", corner_radius=32, hover_color="#6666FF", command=login)
btn_change_register = CTkButton(master=app, text="Register", corner_radius=32, text_color="white",
                                fg_color="transparent", hover_color="black", command=show_register_form)

label_username.place(relx=0.3, rely=0.22, anchor="center")
input_username.place(relx=0.5, rely=0.3, anchor="center")
label_password.place(relx=0.3, rely=0.42, anchor="center")
input_password.place(relx=0.5, rely=0.5, anchor="center")
btn_login.place(relx=0.5, rely=0.6, anchor="center")
btn_change_register.place(relx=0.5, rely=0.7, anchor="center")


reg = CTk()
reg.geometry("500x400")

label_new_username = CTkLabel(master=reg, text="New Username", font=("Arial", 16), text_color="white")
input_new_username = CTkEntry(master=reg, corner_radius=32, width=300, text_color="white")
label_new_password = CTkLabel(master=reg, text="New Password", font=("Arial", 16), text_color="white")
input_new_password = CTkEntry(master=reg, corner_radius=32, width=300, text_color="white")
btn_register = CTkButton(master=reg, text="Create account", corner_radius=32, hover_color="#6666FF", command=register)
btn_back_to_login = CTkButton(master=reg, text="Login", corner_radius=32, text_color="white",
                              fg_color="transparent", hover_color="black", command=show_login_form)

label_new_username.place(relx=0.3, rely=0.22, anchor="center")
input_new_username.place(relx=0.5, rely=0.3, anchor="center")
label_new_password.place(relx=0.3, rely=0.42, anchor="center")
input_new_password.place(relx=0.5, rely=0.5, anchor="center")
btn_register.place(relx=0.5, rely=0.6, anchor="center")
btn_back_to_login.place(relx=0.5, rely=0.7, anchor="center")

reg.withdraw()

menu = CTk()
menu.geometry("500x400")

btn_menu = CTkButton(master=menu, text="New Game", corner_radius=32, hover_color="#6666FF", command=new_game)
btn_menu_saved = CTkButton(master=menu, text="Saved Game", corner_radius=32, hover_color="#6666FF",command=load_game)
btn_menu_rat = CTkButton(master=menu, text="Rating", corner_radius=32, hover_color="#6666FF", command=rat_games)

btn_menu.place(relx=0.5, rely=0.35, anchor="center")
btn_menu_rat.place(relx=0.5, rely=0.5, anchor="center")
btn_menu_saved.place(relx=0.5, rely=0.65, anchor="center")

menu_level = CTk()
menu_level.geometry("500x400")

btn_easy = CTkButton(master=menu_level, text="Новачок", corner_radius=32, hover_color="#6666FF", command=easy_game)
btn_medium = CTkButton(master=menu_level, text="Любитель", corner_radius=32, hover_color="#6666FF",command=medium_game)
btn_advanced = CTkButton(master=menu_level, text="Професіонал", corner_radius=32, hover_color="#6666FF", command=advanced_game)

btn_easy.place(relx=0.5, rely=0.35, anchor="center")
btn_medium.place(relx=0.5, rely=0.5, anchor="center")
btn_advanced.place(relx=0.5, rely=0.65, anchor="center")

rating_window = CTk()
rating_window.geometry("500x400")

pygame.init()

WIDTH, HEIGHT = 500, 600
win = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.HIDDEN)
pygame.display.set_caption("Minesweeper")

BG_COLOR = "white"
ROWS, COLS = 10, 10
BOMBS = 15

SIZE = int((WIDTH // ROWS))

NUM_FONT = pygame.font.SysFont('comicsans', 30)
LOST_FONT = pygame.font.SysFont('comicsans', 40)
TIME_FONT = pygame.font.SysFont('comicsans', 20)
BOMBS_FONT = pygame.font.SysFont('comicsans', 30)

NUM_COLORS = {1: "black", 2: "green", 3: "red", 4: "orange", 5: "yellow", 6: "purple", 7: "blue", 8: "pink"}

RECT_COLOR = (200, 200, 200)
CLICKED_RECT_COLOR = (140, 140, 140)
FLAG_RECT_COLOR = "green"
BOMB_COLOR = "red"
bombs_text = BOMBS_FONT.render(f"Bombs: {BOMBS}", 1, "black")
win.blit(bombs_text, (WIDTH - bombs_text.get_width() - 10, HEIGHT - bombs_text.get_height()))

flag_image = pygame.image.load(os.path.join(os.path.dirname(__file__), 'flag.jpg'))
flag_image = pygame.transform.scale(flag_image, (SIZE, SIZE))

def get_neighbors(row, col, rows, cols):
    neighbors = []

    if row > 0:  # up
        neighbors.append((row - 1, col))
    if row < rows - 1:  # down
        neighbors.append((row + 1, col))
    if col > 0:  # left
        neighbors.append((row, col - 1))
    if col < cols - 1:  # right
        neighbors.append((row, col + 1))

    if row > 0 and col > 0:
        neighbors.append((row - 1, col - 1))
    if row < rows - 1 and col < cols - 1:
        neighbors.append((row + 1, col + 1))
    if row < rows - 1 and col > 0:
        neighbors.append((row + 1, col - 1))
    if row > 0 and col < cols - 1:
        neighbors.append((row - 1, col + 1))

    return neighbors


def create_mine_field(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mines_positions = set()
    while len(mines_positions) < mines:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mines_positions:
            continue

        mines_positions.add(pos)
        field[row][col] = -1

    for mine in mines_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if field[r][c] != -1:
                field[r][c] += 1
    return field



def draw(win, field, cover_field, current_time, result_message=None, flags=None):
    win.fill(BG_COLOR)

    save_text = TIME_FONT.render("Save Game", 1, "white")
    save_button_x = WIDTH - save_text.get_width() - 40
    save_button_y = HEIGHT - save_text.get_height() - 10
    pygame.draw.rect(win, "black", (save_button_x-10, save_button_y-10,save_button_x + save_text.get_width(),save_button_y + save_text.get_height()))
    win.blit(save_text, (save_button_x, save_button_y))

    time_text = TIME_FONT.render(f"TIME Elapsed: {round(current_time)}", 1, "black")
    win.blit(time_text, (10, HEIGHT - time_text.get_height()))

    if flags is not None:
        bombs_left_text = TIME_FONT.render(f"Bombs Left: {flags}", 1, "black")
        win.blit(bombs_left_text, (10, HEIGHT - bombs_left_text.get_height() - 30))

    for i, row in enumerate(field):
        y = SIZE * i
        for j, value in enumerate(row):
            x = SIZE * j

            is_covered = cover_field[i][j] == 0
            is_flag = cover_field[i][j] == -2
            is_bomb = value == -1

            if is_flag:
                win.blit(flag_image, (x, y))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue

            if is_covered:
                pygame.draw.rect(win, RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                continue
            else:
                pygame.draw.rect(win, CLICKED_RECT_COLOR, (x, y, SIZE, SIZE))
                pygame.draw.rect(win, "black", (x, y, SIZE, SIZE), 2)
                if is_bomb:
                    pygame.draw.circle(win, BOMB_COLOR, (x + SIZE / 2, y + SIZE / 2), SIZE / 2 - 4)

                if value > 0:
                    text = NUM_FONT.render(str(value), 1, NUM_COLORS[value])
                    win.blit(text, (x + (SIZE / 2 - text.get_width() / 2),
                                    y + (SIZE / 2 - text.get_height() / 2)))

    if result_message:
        text = LOST_FONT.render(result_message, 1, "black")
        win.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))

    pygame.display.update()



def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // SIZE)
    col = int(mx // SIZE)

    return row, col


def uncover_from_pos(row, col, cover_field, field):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():
        current = q.get()

        neighbors = get_neighbors(*current, ROWS, COLS)
        for r, c in neighbors:
            if (r, c) in visited:
                continue

            value = field[r][c]
            if value == 0 and cover_field[r][c] != -2:
                q.put((r, c))

            if cover_field[r][c] != -2:
                cover_field[r][c] = 1
            visited.add((r, c))

def draw_lost(win, text):
    text = LOST_FONT.render(text, 1, "black")
    win.blit(text, (WIDTH / 2 - text.get_width() / 2,
                    HEIGHT / 2 - text.get_height() / 2))
    pygame.display.update()

def draw_won(win, text):
    text = LOST_FONT.render(text, 1, "black")
    win.blit(text, (WIDTH / 2 - text.get_width() / 2,
                    HEIGHT / 2 - text.get_height() / 2))
    pygame.display.update()


def check_win(cover_field, field):
    for i in range(ROWS):
        for j in range(COLS):
            if cover_field[i][j] == 0 and field[i][j] != -1:
                return False
    return True


def main(TF,saved_field,saved_covered_field):
    print("main start")
    print(ROWS,COLS)
    run = True
    print(TF)
    if TF == False:
        print("We create field")
        field = create_mine_field(ROWS, COLS, BOMBS)
        cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    else:
        print("We load field")
        field = saved_field
        cover_field = saved_covered_field
    print(field)

    print(cover_field)
    save_text = TIME_FONT.render("Save Game", 1, "black")
    flags = BOMBS
    clicks = 0
    lost = False
    won = False
    start_time = 0
    saving = False


    while run:
        if start_time > 0:
            current_time = time.time() - start_time
        else:
            current_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    save_button_x = WIDTH - save_text.get_width() - 10
                    save_button_y = HEIGHT - save_text.get_height() - 5
                    if (save_button_x - 10) < mx < (save_button_x + save_text.get_width() + 10) \
                            and (save_button_y - 5) < my < (save_button_y + save_text.get_height() + 5):
                        saving = True


            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue

                mouse_pressed = pygame.mouse.get_pressed()
                if mouse_pressed[0] and cover_field[row][col] != -2:
                    cover_field[row][col] = 1

                    if field[row][col] == -1:
                        lost = True

                    if clicks == 0 or field[row][col] == 0:
                        uncover_from_pos(row, col, cover_field, field)
                    if clicks == 0:
                        start_time = time.time()
                    clicks += 1
                elif mouse_pressed[2]:
                    if cover_field[row][col] == -2:
                        cover_field[row][col] = 0
                        flags += 1
                    elif (flags > 0):
                        flags -= 1
                        cover_field[row][col] = -2

        if saving:
            save_game(user_id, field,cover_field)
            saving = False



        if lost:

            save_game_result(user_id, 'Lost')
            draw(win, field, cover_field, current_time, "YOU LOST! Try again...", flags=flags)
            pygame.time.delay(5000)

            field = create_mine_field(ROWS, COLS, BOMBS)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = BOMBS
            clicks = 0
            lost = False

        if check_win(cover_field, field):
            save_game_result(user_id, 'Win')
            draw(win, field, cover_field, current_time, "YOU WIN!", flags=flags)
            pygame.time.delay(5000)

            field = create_mine_field(ROWS, COLS, BOMBS)
            cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            flags = BOMBS
            clicks = 0
            won = False

        draw(win, field, cover_field, current_time, flags=flags)

    pygame.quit()

app.mainloop()

