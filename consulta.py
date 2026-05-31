from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
from math import radians, sin, cos, sqrt, atan2
consulta_bp = Blueprint("consulta", __name__)

@consulta_bp.route("/consulta",methods=["GET","POST"])
@consulta_bp.route("/consulta/",methods=["GET","POST"])
def consulta():
    produto = False
    codigo = ""
    descricao = False

    if request.method=="POST":
        if request.form.get("acao") == "atualizar_estabelecimento":
            latitude=float(request.form.get("latitude"))
            longitude=float(request.form.get("longitude"))
            print(f">>> {latitude}, {longitude}", flush=True)

            def haversine(lat1, lon1, lat2, lon2):
                R = 6371.0
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                return R * c

            conn = db()
            c = conn.cursor()
            c.execute("SELECT id,nome,endereco,latitude,longitude,cnpj FROM estabelecimento")
            estabelecimentos = c.fetchall()

            mais_proximo = None
            menor_distancia = float("inf")

            for est in estabelecimentos:
                distancia = haversine(
                    latitude,
                    longitude,
                    est[3],
                    est[4]
                )

                if distancia < menor_distancia:
                    menor_distancia = distancia
                    mais_proximo = est

            if mais_proximo:
                session["estabelecimento_cnpj"] = mais_proximo[5]
                print(
                    f"Mais próximo: {mais_proximo[5]} ({menor_distancia:.2f} km)",
                    flush=True
              )
        if request.form.get("acao") == "consultar_preco":
            codigo=request.form.get("codigo")
            print("código", codigo)
            conn=db();cur=conn.cursor()
            cur.execute("SELECT id, codigo, descricao FROM produto WHERE codigo = ?", (codigo,))
            produto = cur.fetchone()
            print(produto)
            if not produto:
                return render_template("produto_nao_cadastrado.html")

            cnpj=session["estabelecimento_cnpj"]
            print(f">>> cnpj: {cnpj}, codigo: {codigo}", flush=True)
            cur.execute("SELECT id, codigo, cnpj, valor FROM preco WHERE codigo = ? and cnpj = ?", (codigo,cnpj))
            preco = cur.fetchone()
            if not preco:
                return render_template("produto_nao_monitorado.html") 
            conn.close()
    if not session.get("estabelecimento_cnpj"):
        return render_template("set_estabelecimento.html")
    return render_template("consulta.html")
