import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

PASTA = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(PASTA, "caronaescolar.db")

app = Flask(__name__)
app.secret_key = "troque-esta-chave"


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def fechar_banco(_):
    conexao = g.pop("db", None)
    if conexao:
        conexao.close()


def iniciar_banco():
    with sqlite3.connect(DB) as c:
        c.executescript(open(os.path.join(PASTA, "schema.sql"), encoding="utf-8").read())


def usuario_atual():
    uid = session.get("uid")
    if not uid:
        return None
    return db().execute("SELECT * FROM usuarios WHERE id = ?", (uid,)).fetchone()


@app.context_processor
def contexto():
    return {"usuario": usuario_atual()}


@app.route("/")
def index():
    escola = request.args.get("escola", "")
    viagens = db().execute(
        """SELECT v.*, e.nome AS escola, u.nome AS motorista,
                  v.vagas - COUNT(r.id) AS livres
           FROM viagens v
           JOIN escolas e ON e.id = v.escola_id
           JOIN usuarios u ON u.id = v.motorista_id
           LEFT JOIN reservas r ON r.viagem_id = v.id
           WHERE (? = '' OR v.escola_id = ?)
           GROUP BY v.id ORDER BY v.horario""", (escola, escola)).fetchall()
    escolas = db().execute("SELECT * FROM escolas ORDER BY nome").fetchall()
    return render_template("index.html", viagens=viagens, escolas=escolas, filtro=escola)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        f = request.form
        try:
            cur = db().execute(
                "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
                (f["nome"], f["email"].lower(), generate_password_hash(f["senha"]), f["tipo"]))
            db().commit()
            session["uid"] = cur.lastrowid
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Esse e-mail já está cadastrado.")
    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = db().execute("SELECT * FROM usuarios WHERE email = ?",
                         (request.form["email"].lower(),)).fetchone()
        if u and check_password_hash(u["senha_hash"], request.form["senha"]):
            session["uid"] = u["id"]
            return redirect("/")
        flash("E-mail ou senha incorretos.")
    return render_template("login.html")


@app.route("/sair")
def sair():
    session.clear()
    return redirect("/")


@app.route("/viagens/nova", methods=["GET", "POST"])
def nova_viagem():
    u = usuario_atual()
    if not u or u["tipo"] != "motorista":
        flash("Entre como motorista para oferecer viagens.")
        return redirect("/login")
    if request.method == "POST":
        f = request.form
        db().execute(
            """INSERT INTO viagens (motorista_id, escola_id, tipo, origem, horario, vagas)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (u["id"], f["escola_id"], f["tipo"], f["origem"], f["horario"], f["vagas"]))
        db().commit()
        flash("Viagem cadastrada!")
        return redirect("/minhas")
    escolas = db().execute("SELECT * FROM escolas ORDER BY nome").fetchall()
    return render_template("nova.html", escolas=escolas)


@app.route("/reservar/<int:vid>", methods=["POST"])
def reservar(vid):
    u = usuario_atual()
    if not u or u["tipo"] != "passageiro":
        flash("Entre como passageiro para reservar uma vaga.")
        return redirect("/login")
    livres = db().execute(
        """SELECT v.vagas - COUNT(r.id) FROM viagens v
           LEFT JOIN reservas r ON r.viagem_id = v.id WHERE v.id = ?""", (vid,)).fetchone()[0]
    if not livres or livres <= 0:
        flash("Não há vagas nessa viagem.")
        return redirect("/")
    try:
        db().execute("INSERT INTO reservas (viagem_id, passageiro_id) VALUES (?, ?)", (vid, u["id"]))
        db().commit()
        flash("Vaga reservada!")
    except sqlite3.IntegrityError:
        flash("Você já reservou essa viagem.")
    return redirect("/minhas")


@app.route("/cancelar/<int:rid>", methods=["POST"])
def cancelar(rid):
    u = usuario_atual()
    if u:
        db().execute("DELETE FROM reservas WHERE id = ? AND passageiro_id = ?", (rid, u["id"]))
        db().commit()
        flash("Reserva cancelada.")
    return redirect("/minhas")


@app.route("/minhas")
def minhas():
    u = usuario_atual()
    if not u:
        return redirect("/login")
    if u["tipo"] == "passageiro":
        itens = db().execute(
            """SELECT r.id, v.tipo, v.origem, v.horario, e.nome AS escola, m.nome AS motorista
               FROM reservas r JOIN viagens v ON v.id = r.viagem_id
               JOIN escolas e ON e.id = v.escola_id JOIN usuarios m ON m.id = v.motorista_id
               WHERE r.passageiro_id = ? ORDER BY v.horario""", (u["id"],)).fetchall()
    else:
        itens = db().execute(
            """SELECT v.tipo, v.origem, v.horario, v.vagas, e.nome AS escola,
                      GROUP_CONCAT(p.nome, ', ') AS passageiros
               FROM viagens v JOIN escolas e ON e.id = v.escola_id
               LEFT JOIN reservas r ON r.viagem_id = v.id
               LEFT JOIN usuarios p ON p.id = r.passageiro_id
               WHERE v.motorista_id = ? GROUP BY v.id ORDER BY v.horario""", (u["id"],)).fetchall()
    return render_template("minhas.html", itens=itens)


iniciar_banco()

if __name__ == "__main__":
    app.run(debug=True)
