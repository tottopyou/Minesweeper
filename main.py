import sqlite3
from customtkinter import *

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

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
    username = input_username.get()
    password = input_password.get()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    if user:
        print("Login successful!")
    else:
        print("Invalid username or password.")
def show_login_form():
    reg.withdraw()
    app.deiconify()

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

app.mainloop()