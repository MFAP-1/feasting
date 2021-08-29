# Program that creates the Feasting ! website. by MFAP-1 v1.0.0

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup#, usd

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
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///feasting.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Important Global lists:
OCASIOES = ["After", "Bar", "Breakfast", "Brunch", "Cafe", "Dessert", "Dinner", "Late-nite", "Lunch", "Snack"]
CATEGORIAS = ["Barbecue", "Cake(s)", "Candy", "Chinese", "Churros", "Cookie", "Crepe", "Croissant",   
                "Drinks", "Fancy", "Finger-food", "Fish", "Fried", "Gelato", "Hamburger", "Healthy", 
                "Hot dog", "Ice Cream", "Mexican", "Mineira(BR)", "Nordestina(BR)", "Pasta", "Pastry", "Pizza", 
                "Sandwich", "Seafood", "Spanish", "Sushi", "Traditional", "Uruguayan"]
# OCASIOES = ["After", "Almoço", "Barzinho","Café da manhã", "Jantar", "Lanche", "Sobremesa"]
# CATEGORIAS = ["Chinesa", "Churrasco", "Churros", "Cookie", "Crepe", "Croissant", "Doceria",
#             "Drinks", "Espanhola", "Fancy", "Fritos", "Frutos do mar", "Gelatto", "Hamburguer",
#             "Massas", "Mexicana", "Mineira", "Nordestina", "Pastel", "Pescado", "Petiscos",
#             "Pizza", "Sanduiche", "Saudável", "Sorvete", "Sushi", "Tradicional", "Uruguaia"]


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Getting the datetime:
    now = datetime.now()
    
    # Selecting the complete table for the logged-in user:
    table = db.execute("SELECT nome_lugar, cidade, idas, tipo, refeicao, nota, comentario FROM active_places WHERE users_id=:user_id",
                        user_id=session["user_id"])
    
    # Rendering the results:
    return render_template("index.html", now=now.strftime("%d/%m/%Y %H:%M:%S"), 
                            table=table) #cash=usd(cash_available), total=usd(total_portfolio))


@app.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    """Inserir novos lugares"""
    # Prompting the user for the input thru insert.html
    if request.method == "GET":
        return render_template("insert.html", CATEGORIAS=CATEGORIAS, OCASIOES=OCASIOES)
    else:
        # Verificando se o usuário entrou com algo inválido para categoria ou ocasioes.
        if request.form.get("tipo") not in CATEGORIAS or request.form.get("refeicao") not in OCASIOES:
            return apology("Please, insert a valid type/occasion.")
            
        # Querying the database para testar se o lugar já existe na db:
        table = db.execute("SELECT nome_lugar FROM active_places WHERE users_id=:v1 AND nome_lugar=:v2", 
                            v1=session["user_id"], v2=request.form.get("nome_lugar"))

        # Caso em que o lugar já existe na lista do usuário:
        if table != []:
            return apology("Sorry. That place already is in the database. Use the menu 'Update'.")
            
        # Caso em que o lugar ainda NÃO existe na lista do usuário:
        else:
            # Adicionando o lugar na database:
            db.execute("INSERT INTO active_places (users_id, nome_lugar, cidade, idas, tipo, refeicao, nota, comentario) VALUES(:v1, :v2, :v3, :v4, :v5, :v6, :v7, :v8)", 
                        v1=session["user_id"], v2=request.form.get("nome_lugar"), v3=request.form.get("cidade"), v4=request.form.get("idas"), 
                        v5=request.form.get("tipo"), v6=request.form.get("refeicao"), v7=request.form.get("nota"), v8=request.form.get("comentario"))
            
            # Redirecionando o usuário para homepage    
            return redirect("/")


# @app.route("/history")
# @login_required
# def history():
#     """Show history of transactions"""
#     # Selecting the complete history table for the logged-in user:
#     table = db.execute("SELECT symbol, stock_name, shares, price, total, datetime FROM history WHERE user_id=:user_id",
#                         user_id=session["user_id"])
    
    # Rendering the results:
    # return render_template("history.html", table=table)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to homepage
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


# @app.route("/quote", methods=["GET", "POST"])
# @login_required
# def quote():
#     """Get stock quote."""
#     # Prompting the user for the input thru quote.html
#     if request.method == "GET":
#         return render_template("quote.html")
#     else:
#         # Checking if the user entered an invalid stock symbol or Null.
#         if lookup(request.form.get("symbol")) == None: 
#             return apology("Please insert a valid symbol.")
            
#         # Rendering the result quotation
#         else:
#             now = datetime.now()
#             return render_template("quoted.html", now=now.strftime("%d/%m/%Y %H:%M:%S"), quotation=lookup(request.form.get("symbol")))


@app.route("/results", methods=["GET", "POST"])
@login_required
def results():
    # PSELECT tipo, SUM(idas) FROM active_places WHERE users_id=1 GROUP BY tipo
    if request.method == "GET":
        # Querying the database for selecting active symbols from the table for the logged-in user:
        table1 = db.execute("SELECT tipo, SUM(idas) FROM active_places WHERE users_id=:v1 GROUP BY tipo",
                            v1=session["user_id"])
        table2 = db.execute("SELECT refeicao, SUM(idas) FROM active_places WHERE users_id=:v1 GROUP BY refeicao",
                            v1=session["user_id"])
        table3 = db.execute("SELECT cidade, SUM(idas) FROM active_places WHERE users_id=:v1 GROUP BY cidade",
                            v1=session["user_id"])
        list1 = []
        list2 = []
        len2 = 0
        for row in table3:
            list1.append(row["cidade"])
            list2.append(int(row["SUM(idas)"]))
            len2 += int(row["SUM(idas)"])
        len1=len(list1)
        return render_template("results.html", table1=table1, table2=table2, list1=list1,list2=list2,
                                len1=len1, len2=len2)
    else:
        return apology("WORK IN PROGRESS") # TO DO


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Checking if the username isn't blank:
        if not username:
            return apology("Please, insert a username.")
        
        # Checking if username already exists in the database:
        if db.execute("SELECT username FROM users WHERE username=:name", name=username) != []:
            return apology("Sorry. Username is taken.") 
            
        # Checking if the password isn't blank:
        if not password:
            return apology("Please, insert a password.")
            
        # Checking if the passcodes match each other:
        elif password != request.form.get("confirmation"):
            return apology("Password do not match.")
            
        # Storing the username and hashed password into the database (after passing thru all tests.)
        p_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :p_hash)", username=username, p_hash=p_hash)
        
        # Redirect user to login form (mainpage)
        return redirect("/")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Atualizar a lista de lugares"""
    # Prompting the user for the input thru update.html
    if request.method == "GET":
        
        # Querying the database for selecting active symbols from the table for the logged-in user:
        table = db.execute("SELECT nome_lugar FROM active_places WHERE users_id=:v1",
                            v1=session["user_id"])
    
        # Rendering the update's page interface:
        return render_template("update.html", table=table)

    # Caso onde entrou no "Add + 1". Logo, adicionar 1 no lugar da database:
    # elif request.form.action == 'add1':
    # elif 'add1' in request.form:
    #     return apology("entrou no add+1")
    #     db.execute("UPDATE active_places SET idas = idas + 1 WHERE users_id=:v1 AND nome_lugar=:v2", 
    #                 v1=session["user_id"], v2=request.form.get("nome_lugar"))
    #     return redirect("/")  

    else:
        # Caso onde a atualização levará a 0 o número de idas. Logo, deletar o lugar da database:
        if int(request.form.get("idas")) == 0:
            db.execute("DELETE FROM active_places WHERE users_id=:v1 AND nome_lugar=:v2", 
                        v1=session["user_id"], v2=request.form.get("nome_lugar"))
            return redirect("/")
        
        # Caso onde atualizou-se com um novo valor de idas:
        else:
            db.execute("UPDATE active_places SET idas=:v1 WHERE users_id=:v2 AND nome_lugar=:v3", 
                        v1=request.form.get("idas"), v2=session["user_id"], v3=request.form.get("nome_lugar"))
                        
        # Storing the transaction to the HISTORY database:
        # db.execute("INSERT INTO history (user_id, symbol, stock_name, shares, price, total) VALUES(:v1, :v2, :v3, :v4, :v5, :v6)", 
                        # v1=session["user_id"], v2=quotation["symbol"], v3=quotation["name"], v4=-selling_amount, v5=round(current_price,2), v6=round(total,2))
        
        # Redirecionando o usuário para homepage    
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)