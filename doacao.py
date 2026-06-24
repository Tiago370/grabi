from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
doacao_bp = Blueprint("doacao", __name__)

@doacao_bp.route("/doacao",methods=["GET","POST"])
@doacao_bp.route("/doacao/",methods=["GET","POST"])
def doacao():

    return render_template("doacao.html")
