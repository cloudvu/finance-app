import os
from types import TracebackType

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_name = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    check = db.execute("SELECT name FROM main.sqlite_master WHERE type='table'")
    #print(check)
    #print('stocks' not in check[0]['name'])
    if not any(c['name'] == 'stocks' for c in check):
        return render_template("index.html", user_name=user_name)

    stocks = db.execute("SELECT * FROM stocks WHERE user_id = ?", session["user_id"])
    
    #print(stocks)
    return render_template("index.html", stocks=stocks, user_name=user_name)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get('symbol')
        price = lookup(symbol)['price']
        
        if not request.form.get('ammount').isnumeric() or int(request.form.get('ammount')) % 100 != 0:
            return apology("The ammount is not a valid number, should be a multiple of 100", 501)
        ammount = int(request.form.get('ammount'))
        cost = price * int(ammount)
        current = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        print(cost)
        print(current)
        if cost > current[0]["cash"]:
            return apology("Not enough money", 999)
        else:
            db.execute("CREATE TABLE IF NOT EXISTS history (user_id TEXT NOT NULL, symbol TEXT NOT NULL, ammount INTEGER, currentprice REAL, type TEXT, time TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")
            db.execute("INSERT INTO history (user_id, symbol, ammount, currentprice, type, time) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], symbol, ammount, price, "buy", datetime.now())

            db.execute("UPDATE users SET cash = ? WHERE id = ?", current[0]["cash"] - cost, session["user_id"])
            db.execute("CREATE TABLE IF NOT EXISTS stocks (user_id TEXT NOT NULL, symbol TEXT NOT NULL, ammount INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")

            row = db.execute("SELECT * FROM stocks WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
            if len(row) == 0:
                db.execute("INSERT INTO stocks (user_id, symbol, ammount) VALUES (?, ?, ?)", session["user_id"], symbol, ammount)
            else:
                #print(row[0]["ammount"])
                ammount += row[0]["ammount"]
                db.execute("UPDATE stocks SET ammount = ? WHERE symbol = ? AND user_id = ?", ammount, symbol, session["user_id"])
            
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])
    user_name = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    return render_template("history.html", transactions=transactions, user_name=user_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        #print(symbol)
        result = lookup(symbol)
        #print(result)
        return render_template("quoted.html", result = result)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password") or request.form.get("repassword") != request.form.get("password"):
            return apology("password doesn't match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) == 1:
            return apology("username existed, choose another one!", 403)

        rows = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
  app.run()