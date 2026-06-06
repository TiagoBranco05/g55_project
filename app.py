from flask import Flask, render_template, request, session, redirect, url_for
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'classes'))
from airline import Airline
from promotion import Promotion
from reward import Reward
from redemption import Redemption
from userlogin import Userlogin

from subs.apps_gform import apps_gform
from subs.apps_userlogin import apps_userlogin
from subs.apps_plot import apps_plot
from subs.apps_plotly import apps_plotly

app = Flask(__name__)
app.secret_key = 'G55_SECRET_KEY'

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'G55.db')

Airline.load_db(DB_PATH)
Userlogin.read(DB_PATH)

def require_login():
    if not session.get("user"):
        return redirect(url_for("login"))
    return None

@app.route("/")
def home():
    return render_template("home.html",
                           ulogin=session.get("user"),
                           n_airlines=len(Airline.lst),
                           n_promotions=len(Promotion.lst),
                           n_rewards=len(Reward.lst),
                           n_redemptions=len(Redemption.lst))

@app.route("/login")
def login():
    return render_template("login.html", ulogin=session.get("user"), resul="")

@app.route("/logoff")
def logoff():
    session.pop("user", None)
    Userlogin.username = ""
    Userlogin.user_id = 0
    return render_template("home.html", ulogin=None,
                           n_airlines=len(Airline.lst),
                           n_promotions=len(Promotion.lst),
                           n_rewards=len(Reward.lst),
                           n_redemptions=len(Redemption.lst))

@app.route("/chklogin", methods=["post", "get"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]
    resul = Userlogin.chk_password(user, password)
    if resul == "Valid":
        session["user"] = user
        return redirect(url_for("home"))
    return render_template("login.html", user=user, password=password,
                           ulogin=session.get("user"), resul=resul)

@app.route("/gform/<cname>", methods=["post", "get"])
def gform(cname):
    redir = require_login()
    if redir: return redir
    return apps_gform(cname)

@app.route("/Userlogin", methods=["post", "get"])
def userlogin():
    redir = require_login()
    if redir: return redir
    return apps_userlogin()

@app.route("/plot", methods=["post", "get"])
def plot():
    redir = require_login()
    if redir: return redir
    return apps_plot()

@app.route("/plotly", methods=["post", "get"])
def plotly():
    redir = require_login()
    if redir: return redir
    return apps_plotly()

if __name__ == "__main__":
    app.run(debug=True)
