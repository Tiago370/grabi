from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
from dotenv import load_dotenv
import os

doacao_bp = Blueprint("doacao", __name__)

@doacao_bp.route("/doacao",methods=["GET","POST"])
@doacao_bp.route("/doacao/",methods=["GET","POST"])
def doacao():
    load_dotenv()
    PIX_KEY_ANY = os.getenv("PIX_KEY_ANY")
    PIX_KEY_1_REAL = os.getenv("PIX_KEY_1_REAL")
    return render_template("doacao.html",PIX_KEY_ANY=PIX_KEY_ANY,PIX_KEY_1_REAL=PIX_KEY_1_REAL)

