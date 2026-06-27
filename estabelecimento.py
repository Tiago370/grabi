from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, request, session, abort
from utils import db, calcular_total, render_page
from banco import Estabelecimento, Preco
estabelecimento_bp = Blueprint("estabelecimento", __name__)

@estabelecimento_bp.route("/estabelecimento",methods=["GET","POST"])
@estabelecimento_bp.route("/estabelecimento/",methods=["GET","POST"])
def estabelecimento():
    if not session.get("admin"):
        return redirect("/")
    if request.method=="POST":
        if request.method=="POST":
            nome=request.form["nome"]
            endereco=request.form["endereco"]
            latitude=request.form["latitude"]
            longitude=request.form.get("longitude")
            cnpj=request.form.get("cnpj")
            Estabelecimento(cnpj=cnpj,nome=nome,endereco=endereco,latitude=latitude,longitude=longitude).save()
            return redirect("/")
    return render_template("estabelecimento.html")

@estabelecimento_bp.route("/estabelecimento/<cnpj>/",methods=["GET"])
def mostrar_estabelecimento(cnpj):
    estabelecimento = Estabelecimento.get(cnpj)
    print(estabelecimento)

#    if not estabelecimento:
#        abort(404)

    limite_recente = datetime.utcnow() - timedelta(days=7)

    precos = Preco.get_all()

    return render_page("mostrar_estabelecimento.html", estabelecimento=estabelecimento, precos=precos)
