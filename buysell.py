from cs50 import SQL
from datetime import datetime


db = SQL("sqlite:///finance.db")

def update_database(a, b, c, d, e, f):
    db.execute("CREATE TABLE IF NOT EXISTS history (user_id TEXT NOT NULL, symbol TEXT NOT NULL, ammount INTEGER, currentprice REAL, type TEXT, time TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")
    db.execute("INSERT INTO history (user_id, symbol, ammount, currentprice, type, time) VALUES (?, ?, ?, ?, ?, ?)", a, b, c, d, e, datetime.now())
    if e == "buy":
        db.execute("UPDATE users SET cash = ? WHERE id = ?", f["cash"] - c * d, a)
        db.execute("CREATE TABLE IF NOT EXISTS stocks (user_id TEXT NOT NULL, symbol TEXT NOT NULL, ammount INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")

        if len(row) == 0:
            db.execute("INSERT INTO stocks (user_id, symbol, ammount) VALUES (?, ?, ?)", a, b, c)
        else:
            #print(row[0]["ammount"])

            db.execute("UPDATE stocks SET ammount = ? WHERE symbol = ? AND user_id = ?", c +  f["ammount"], b, a)
    elif e == "sell":
        db.execute("UPDATE users SET cash = ? WHERE id = ?", f["cash"] + c * d, a)
        
        db.execute("UPDATE stocks SET ammount = ? WHERE symbol = ? AND user_id = ?", f["ammount"] - c, b, a)

    