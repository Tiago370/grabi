from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, request, session, abort
from utils import db, calcular_total, render_page
from banco import Estabelecimento, Preco, Produto
from consulta import tempo_decorrido
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

    if not estabelecimento:
        abort(404)

    inicio = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")

    precos = Preco.filter(
        order_by="updated_at DESC",
        limit=100
    )

    precos_full = []
    for preco in precos:
        produto = Produto.get(preco.codigo)
        combinado = produto | preco.__dict__
        combinado["updated_at"] = tempo_decorrido(combinado["updated_at"])
        if combinado["codigo"] != combinado["descricao"]:
            precos_full.append(combinado)

    return render_page("mostrar_estabelecimento.html", estabelecimento=estabelecimento, precos=precos_full)
