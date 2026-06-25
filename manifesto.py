from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
manifesto_bp = Blueprint("manifesto", __name__)

@manifesto_bp.route("/manifesto",methods=["GET","POST"])
@manifesto_bp.route("/manifesto/",methods=["GET","POST"])
def manifesto():

    return render_template("manifesto.html")
