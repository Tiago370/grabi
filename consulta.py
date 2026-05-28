from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
consulta_bp = Blueprint("consulta", __name__)

@consulta_bp.route("/consulta",methods=["GET","POST"])
@consulta_bp.route("/consulta/",methods=["GET","POST"])
def consulta():
    produto = False
    codigo = ""
    descricao = False
    if request.method=="POST":
        conn=db();c=conn.cursor()
        codigo = request.form["codigo"]
        produto=c.execute("select id,descricao from produto where codigo=?",(codigo,)).fetchone();conn.close()
        if produto:
            descricao = produto[1]

    return render_template("consulta.html", descricao=descricao,codigo=codigo)
