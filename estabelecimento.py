from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
from banco import Estabelecimento
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
