import sqlite3

conn = sqlite3.connect("database.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

# Создание таблицы
cursor.execute("""CREATE TABLE IF NOT EXISTS users
                  (id integer PRIMARY KEY,
                   tg_id integer,
                   lastans date)
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS learning
                  (user_id int,
                   word text,
                   cnt int,
                   lastans date,
                   PRIMARY KEY (user_id, word),
                   FOREIGN KEY (user_id) REFERENCES users (tg_id))
               """)