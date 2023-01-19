import os
import datetime
import io
import numpy as np
import matplotlib.pyplot as plt
import requests
import smtplib
import ssl
import urllib.request
import asyncio
import urllib.error
import time
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from matplotlib.ticker import FormatStrFormatter
from bs4 import BeautifulSoup
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, usd, real
from forms import RegisterForm
from Naked.toolshed.shell import execute_js, muterun_js
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigCanvas


# Configure application
app = Flask(__name__)
# app.scheduler = apscheduler.schedulers.background.BackgroundScheduler()
# app.scheduler.start()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
Session(app)

db = SQL("sqlite:///site.db")
# users = id, username, hash
# emails_cadastrados = comprador_id, email
# lista = comprador_id, titulo_produto, info, data
# lista_de_links = comprador_id, link, data
# historico_de_precos = comprador_id, link, price, day, data
# db.execute("CREATE TABLE precos_desejados (comprador_id INTEGER, price TEXT NOT NULL, data TEXT NOT NULL, FOREIGN KEY(comprador_id) REFERENCES users(id))")
# db.execute("CREATE TABLE lista (comprador_id INTEGER, titulo_produto TEXT NOT NULL, info TEXT NOT NULL, data TEXT NOT NULL, FOREIGN KEY(comprador_id) REFERENCES users(id))")

"""
async def async_get_data():
    print("assincrono")
    await asyncio.sleep(1)
    return 'Done!'

@app.route("/data")
async def get_data():
    data = await async_get_data()
    return data
"""


@app.after_request  # Code source = pset9 CS50. Finance
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/foo", methods=["GET"])
@login_required
def background():
    user = session["username"]
    remetente = session["remetente"]
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
    #  ========================== QUAIS SÃO OS PRODUTOS DA WL? =======================================================
    produtos = db.execute("SELECT titulo_produto FROM lista WHERE comprador_id = ? ORDER BY data", session['user_id'])
    lista_produtos = []
    for produto in produtos:
        response = produto['titulo_produto']
        lista_produtos.append(response)
    #  ================================================================================================================
    #  ========================== QUAIS SÃO OS LINKS DOS PRODUTOS DA WL? ==========================================
    links = db.execute("SELECT link FROM lista_de_links WHERE comprador_id = ? ORDER BY data", session['user_id'])
    lista_links = []
    for link in links:
        response = link['link']
        lista_links.append(response)
    #  =============================================================================================================
    #  ========================== QUAIS SÃO OS PREÇOS DOS PRODUTOS DA WL DESEJADOS? ==================================
    precos = db.execute("SELECT price FROM precos_desejados WHERE comprador_id = ? ORDER BY data", session['user_id'])
    lista_precos = []
    for preco in precos:
        response = preco['price']
        lista_precos.append(response)
    #  =============================================================================================================
    def teste(user, remetente, lista_produtos, lista_links, lista_precos, headers):
        i = 0
        for link in lista_links:
            page = requests.get(link, headers=headers)
            bs = BeautifulSoup(page.content, 'html.parser')
            price = bs.find("span", {"class": "catalog-detail-price-value", "data-field": "finalPrice", "itemprop": "price"}).get_text()
            price = float(price.strip().replace(",", ".").replace("R$ ", ""))
            if price <= float(lista_precos[i]):
                mande_email(remetente, user, link, lista_produtos[i], price)
            i += 1

    def mande_email(remetente, user, link, produto, price):

        EMAIL_ADDRESS = "dftrack.mail@gmail.com"
        EMAIL_PASSWORD = "fjzdlytigomtylqa"

        msg = EmailMessage()
        msg['Subject'] = 'Price drop!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = remetente
        html_message = open('templates/email_body.html').read()
        html_message = html_message.replace('{{user}}',user).replace('{{produto}}',produto).replace('{{link}}',link).replace('{{price}}',str(price))
        msg.set_content(html_message, subtype='html')
        #msg.set_content(f'Hey, {user}! {produto} is R${price} now! Check it: {link} :D')


        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            try:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
            except Exception as e:
                print(e)

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=teste, args=[user, remetente, lista_produtos, lista_links, lista_precos, headers], trigger="interval", seconds=86400)
    scheduler.start()
    return redirect(url_for('index'))


@app.route("/", methods=["GET"])
@login_required
def index():
    data = db.execute("SELECT * FROM lista WHERE comprador_id = ? ORDER BY titulo_produto", session["user_id"])
        # lista_links = db.execute("SELECT link FROM lista_de_links WHERE comprador_id = ?", session["user_id"])
        # lista_precos = []
        # for link in lista_links:
        #   response = muterun_js('static/preco.js', link['link'])
        #   preco = response.stdout.decode('utf-8')
        #   lista_precos.append(preco)
        # print(lista_precos)
    return render_template("inicial.html", user = session["username"], data = data)


@app.route("/remove/<string:data>")
@login_required
def remove(data):
    db.execute("DELETE FROM lista WHERE data = ? AND comprador_id = ?", data, session["user_id"])
    db.execute("DELETE FROM lista_de_links WHERE data = ? AND comprador_id = ?", data, session["user_id"])
    db.execute("DELETE FROM historico_de_precos WHERE data = ? AND comprador_id = ?", data, session["user_id"])
    db.execute("DELETE FROM precos_desejados WHERE data = ? AND comprador_id = ?", data, session["user_id"])

    return redirect(url_for('index'))


@app.route("/att/<string:data>", methods=["GET", "POST"])
@login_required
def att(data):
    quem_eu_quero_atualizar = data
    print("A DATA DO NOME A ATUALUZAR")
    print(quem_eu_quero_atualizar)
    if request.method == "POST":
        nome_atualizado = request.form.get("novo_nome")
        db.execute("UPDATE lista SET titulo_produto = ? WHERE comprador_id = ? AND data = ?", nome_atualizado, session['user_id'], quem_eu_quero_atualizar)
        print(nome_atualizado)
        return redirect(url_for('index'))
    else:
        return render_template('att.html', quem_eu_quero_atualizar = quem_eu_quero_atualizar)


@app.route("/login", methods=["GET", "POST"]) # Code source = pset9 CS50. Finance
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
        session["username"] = rows[0]["username"]

        #  ========================== QUEM VAI RECEBER O EMAIL? USUÁRIO =========================================
        remetente = db.execute("SELECT email FROM emails_cadastrados WHERE comprador_id = ?", session['user_id'])
        session["remetente"] = remetente[0]["email"]
        #  ======================================================================================================

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    formulario = RegisterForm()
    if formulario.validate_on_submit():

        username = formulario.username.data  # informação fornecida no formulário
        password_hash = formulario.password1.data
        email = formulario.email.data
        numero = len(db.execute("SELECT username FROM users WHERE username == :username", username = username))
        numero_email = len(db.execute("SELECT email FROM emails_cadastrados WHERE email == :email", email = email))

        if numero == 0 and numero_email == 0:

            password_hash = generate_password_hash(password_hash,  method ='pbkdf2:sha1', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)
            usuario = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["usuario"] = usuario[0]["id"]
            db.execute("INSERT INTO emails_cadastrados (email, comprador_id) VALUES (?, ?)", email, session["usuario"])
            return redirect(url_for('index'))

        if numero != 0:  # verifica se o username já está em uso
            return render_template("userrepetido.html", mensagem = "Username is already in use, choose another one.")
        if numero_email != 0:  # verifica se o email já está em uso
            return render_template("userrepetido.html", mensagem = "E-mail already registered.")

    if formulario.errors != {}:  # se há erros
        for err_msg in formulario.errors.values():
            flash(f'An error has occurred: {err_msg}', category ='danger')
    return render_template("register.html", form = formulario)


@app.route("/logout")  # Code source = pset9 CS50. Finance
def logout():
    session.clear()
    return redirect("/")


@app.route("/wishlist", methods=["GET", "POST"])
@login_required
def wishlist():
    """create wishlist."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        linque = request.form.get("linque")
        search_domain = 'https://www.dafiti.com.br/'
        if search_domain in linque:
            response = muterun_js('static/file.js',linque)  # Pega o titulo do produto
            test = response.stdout.decode('utf-8')
            data = datetime.datetime.now()
            information = "You added the product " + test + "to your WishList on " + str(data)
            db.execute("INSERT INTO lista (comprador_id, titulo_produto, info, data) VALUES (?, ?, ?, ?)", session["user_id"], test, information, data)
            db.execute("INSERT INTO lista_de_links (comprador_id, link, data) VALUES (?, ?, ?)", session["user_id"], linque, data)
            price = ''
            db.execute("INSERT INTO precos_desejados (price, data, comprador_id) VALUES (?, ?, ?)", price, data, session['user_id'])
            print(test)
            return redirect(url_for('index'))
        else:
            return apology("Enter a valid Dafiti product link", 403)
    else:
        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("wishlist.html")


@app.route("/prices", methods=["GET", "POST"])
@login_required
def prices():
    produtos = (db.execute("SELECT titulo_produto, data FROM lista WHERE comprador_id = ? ORDER BY titulo_produto", session['user_id']))

    if request.method == "POST":
        produto_data = request.form.get("produto")
        session["DATA"] = produto_data
        link = (db.execute("SELECT link FROM lista_de_links WHERE comprador_id = ? AND data = ?", session['user_id'], produto_data))
        titulo = (db.execute("SELECT titulo_produto FROM lista WHERE comprador_id = ? AND data = ?", session['user_id'], produto_data))
        session["url"] = link[0]["link"]
        url = session["url"]

        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
        page = requests.get(url, headers=headers)
        bs = BeautifulSoup(page.content, 'html.parser')
        price = bs.find("span", {"class": "catalog-detail-price-value", "data-field": "finalPrice", "itemprop": "price"}).get_text()
        price = float(price.strip().replace(",", ".").replace("R$ ", ""))
        now = datetime.datetime.now()

        db.execute("INSERT INTO historico_de_precos (comprador_id, link, price, day, data) VALUES (?, ?, ?, ?, ?)", session["user_id"], url, price, now, produto_data)
        data_prices = (db.execute("SELECT * FROM historico_de_precos WHERE comprador_id = ? AND link = ?", session['user_id'], url))

        return render_template("price-information.html", link = link, titulo=titulo, price=real(price).replace(".", ","), data_prices=data_prices)
    else:  # metodo = Get
        return render_template("prices.html", produtos=produtos)


@app.route("/view", methods=["GET", "POST"])
@login_required
def view():
    produto_data = session["DATA"]
    print(produto_data)
    dias = db.execute("SELECT day FROM historico_de_precos WHERE comprador_id = ? AND data = ? ORDER BY day", session["user_id"], produto_data)
    precos = db.execute("SELECT price FROM historico_de_precos WHERE comprador_id = ? AND data = ? ORDER BY day", session["user_id"], produto_data)

    lista_dias = []
    lista_preco = []

    for dia in dias:
       response = dia['day']
       lista_dias.append(response)
    print(lista_dias)

    for preco in precos:
       response = preco['price']
       lista_preco.append(float(response))
    print(lista_preco)

    fig, ax = plt.subplots()
    ax.plot(lista_dias, lista_preco, '#5800FF')
    ax.get_xaxis().set_ticks([])
    ax.set_yticks(lista_preco)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    # plt.xticks(rotation=90, ha='right')

    ax.set(xlabel='Date', ylabel="Price (R$)",
       title='Price history', autoscale_on=True)
    ax.grid(alpha = 0.2)
    ax.set_aspect('auto')


    """
    fig = plt.figure(figsize=(10, 5))

    # creating the bar plot
    plt.bar(lista_dias, lista_preco, color='maroon',
            width=0.4)

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Price history")
    """

    FigCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    plt.tight_layout()

    return send_file(img, mimetype ='img/png')


@app.route("/email", methods=["GET", "POST"])
@login_required
def email():
    produtos = (db.execute("SELECT titulo_produto, data FROM lista WHERE comprador_id = ? ORDER BY data", session['user_id']))
    precos = (db.execute("SELECT price, data FROM precos_desejados WHERE comprador_id = ? ORDER BY data", session['user_id']))
    if request.method == "POST":
        lista_datas = []
        lista_precos_desejados = []

        for data in produtos:
            response = data['data']
            lista_datas.append(response)
        print(lista_datas)

        for data in lista_datas:
            response = request.form.get(data)
            lista_precos_desejados.append(response)
            if response != '':
                db.execute("UPDATE precos_desejados SET price = ? WHERE comprador_id = ? AND data = ?", response, session['user_id'], data)
        print(lista_precos_desejados)

        return redirect("/email")
    else:  # metodo = Get
        return render_template("email.html", produtos = produtos, precos = precos)


"""

#  ========================== QUEM VAI RECEBER O EMAIL? USUÁRIO =========================================
remetente = db.execute("SELECT email FROM emails_cadastrados WHERE comprador_id = ?", session['user_id'])
session["remetente"] = remetente[0]["email"]
email_do_user = session["remetente"]
#  ======================================================================================================

#  ========================== QUAIS SÃO OS PRODUTOS DA WL? =======================================================
produtos = db.execute("SELECT titulo_produto FROM lista WHERE comprador_id = ? ORDER BY data", session['user_id'])
lista_produtos = []
for produto in produtos:
    response = produto['titulo_produto']
    lista_produtos.append(response)
print(lista_produtos)
#  ================================================================================================================

#  ========================== QUAIS SÃO OS LINKS DOS PRODUTOS DA WL? ==========================================
links = db.execute("SELECT link FROM lista_de_links WHERE comprador_id = ? ORDER BY data", session['user_id'])
lista_links = []
for link in links:
    response = link['link']
    lista_links.append(response)
print(lista_links)
#  =============================================================================================================

#  ========================== QUAIS SÃO OS PREÇOS DOS PRODUTOS DA WL DESEJADOS? ==================================
precos = db.execute("SELECT price FROM precos_desejados WHERE comprador_id = ? ORDER BY data", session['user_id'])
lista_precos = []
for preco in precos:
    response = preco['price']
    lista_precos.append(response)
print(lista_precos)
#  =============================================================================================================

msg = Message('Price drop!', sender = ('DFTracker', 'dftrack.mail@gmail.com'), recipients = ['dftrack.mail@gmail.com'])
msg.html = render_template('email_body.html', user=session["username"], produto=produto, preco=preco)
mail.send(msg)


headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

while True:
    page = requests.get(url, headers=headers)
    bs = BeautifulSoup(page.content, 'html.parser')
    price = bs.find("span", {"class": "catalog-detail-price-value", "data-field": "finalPrice", "itemprop": "price"}).get_text()
    price = float(price.strip().replace(",", ".").replace("R$ ", ""))

    if price <= preco_desejado:
        email
    time.sleep(86400)

"""

