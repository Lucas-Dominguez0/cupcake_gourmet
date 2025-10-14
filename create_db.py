# create_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

def create_tables(conn):
    c = conn.cursor()

    # usuários
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        address TEXT,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # produtos
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT,
        img TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # pedidos
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total REAL,
        payment_method TEXT,
        status TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')

    # itens do pedido
    c.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        qty INTEGER,
        price REAL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    ''')

    conn.commit()

def seed_products(conn):
    c = conn.cursor()
    products = [
        ("Cupcake Chocolate", 8.00, "Chocolate", "https://i.imgur.com/1bK7R9J.jpg"),
        ("Cupcake Baunilha", 7.50, "Baunilha", "https://i.imgur.com/ODdMZcV.jpg"),
        ("Cupcake Morango", 9.00, "Morango", "https://i.imgur.com/XH6t7tS.jpg"),
        ("Cupcake Chocolate Branco", 8.50, "Chocolate", "https://i.imgur.com/yPp2zZP.jpg"),
        ("Cupcake Baunilha com Frutas", 9.00, "Baunilha", "https://i.imgur.com/0pSJu5k.jpg"),
        ("Cupcake Morango com Chocolate", 9.50, "Morango", "https://i.imgur.com/6dK6xQH.jpg")
    ]
    # inserir sem duplicar
    for p in products:
        c.execute("SELECT id FROM products WHERE name = ?", (p[0],))
        if c.fetchone() is None:
            c.execute("INSERT INTO products (name, price, category, img) VALUES (?, ?, ?, ?)", p)
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_products(conn)
    conn.close()
    print(f"Banco criado em {DB_PATH.resolve()} com tabelas e produtos seed.")

if __name__ == "__main__":
    main()
