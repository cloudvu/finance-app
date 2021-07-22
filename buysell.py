from cs50 import SQL
from datetime import datetime


db = SQL("sqlite:///finance.db")

def update_database(a, b, c, d, e, f, g):
    # Create history table if not exists
    db.execute("CREATE TABLE IF NOT EXISTS history (user_id TEXT NOT NULL, symbol TEXT NOT NULL, ammount INTEGER, currentprice REAL, type TEXT, time TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")
    # Update history table with session[user_id], symbol of stock, amount of stock, the current looked up price, sell/buy, and the current time
    db.execute("INSERT INTO history (user_id, symbol, ammount, currentprice, type, time) VALUES (?, ?, ?, ?, ?, ?)", a, b, c, d, e, datetime.now())
    
    print(f)
    print(e)
    if e == "buy":
        db.execute("UPDATE users SET cash = ? WHERE id = ?", g["cash"] - c * d, a)
        db.execute("CREATE TABLE IF NOT EXISTS stocks (user_id TEXT NOT NULL, symbol TEXT NOT NULL, ammount INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")
        
        db.execute("UPDATE stocks SET ammount = ? WHERE symbol = ? AND user_id = ?", c +  f["ammount"], b, a)

    elif e == "sell":
        db.execute("UPDATE users SET cash = ? WHERE id = ?", g["cash"] + c * d, a)
        
        db.execute("UPDATE stocks SET ammount = ? WHERE symbol = ? AND user_id = ?", f["ammount"] - c, b, a)

    