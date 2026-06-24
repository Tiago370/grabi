from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total

tutorial_bp = Blueprint("tutorial", __name__)

@tutorial_bp.route("/tutorial",methods=["GET","POST"])
@tutorial_bp.route("/tutorial/",methods=["GET","POST"])
def tutorial():
    return render_template("tutorial.html")

