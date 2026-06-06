from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
estabelecimento_bp = Blueprint("estabelecimento", __name__)

@estabelecimento_bp.route("/estabelecimento",methods=["GET","POST"])
@estabelecimento_bp.route("/estabelecimento/",methods=["GET","POST"])
def estabelecimento():
    if not session.get("admin"):
        return redirect("/")
    if request.method=="POST":
        conn=db();c=conn.cursor()
        if request.method=="POST":
            nome=request.form["nome"]
            endereco=request.form["endereco"]
            latitude=request.form["latitude"]
            longitude=request.form.get("longitude")
            cnpj=request.form.get("cnpj")
            c.execute("insert into estabelecimento(nome,endereco,latitude,longitude,cnpj) values(?,?,?,?,?)",(nome,endereco,latitude,longitude,cnpj))
            conn.commit();conn.close();return redirect("/")
    return render_template("estabelecimento.html")
