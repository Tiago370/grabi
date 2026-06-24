from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
from banco import Estabelecimento
mapa_bp = Blueprint("mapa", __name__)

@mapa_bp.route("/mapa",methods=["GET","POST"])
@mapa_bp.route("/mapa/",methods=["GET","POST"])
def mapa():
    estabelecimentos = Estabelecimento.get_all()
    print(estabelecimentos)
    pontos = []

    for e in estabelecimentos:
        if e.latitude and e.longitude:
            pontos.append({
                "nome": e.nome,
                "lat": float(e.latitude),
                "lng": float(e.longitude)
            })

    return render_template(
        "mapa.html",
        estabelecimentos=pontos
    )
