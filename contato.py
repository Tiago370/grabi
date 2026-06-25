from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
contato_bp = Blueprint("contato", __name__)

@contato_bp.route("/contato",methods=["GET","POST"])
@contato_bp.route("/contato/",methods=["GET","POST"])
def contato():

    return render_template("contato.html")
