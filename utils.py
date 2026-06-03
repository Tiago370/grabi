import sqlite3,os
from flask import session, render_template
from math import radians, sin, cos, sqrt, atan2

def db():return sqlite3.connect("pdv.db")

def init_db():
    caminho_base=os.path.dirname(os.path.abspath(__file__))
    caminho_schema=os.path.join(caminho_base,"schema.sql")
    caminho_db=os.path.join(caminho_base,"pdv.db")
    if not os.path.exists(caminho_db):
        conn=sqlite3.connect(caminho_db)
        c=conn.cursor()
        with open(caminho_schema,"r") as f:c.executescript(f.read())
        conn.commit()
        conn.close()


def calcular_total():
    return sum(i["sub_total"] for i in session["itens"])

def render_page(template, **kwargs):
    contexto = {}

    return render_template(
        template,
        **contexto,
        **kwargs
    )

def get_estabelecimento(latitude, longitude):
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
        distancia = haversine(latitude,longitude,est[3],est[4])
        if distancia < menor_distancia:
            menor_distancia = distancia
            mais_proximo = est

    if mais_proximo:
        estabelecimento = {}
        estabelecimento["cnpj"] = mais_proximo[5]
        estabelecimento["nome"] = mais_proximo[1]
        return estabelecimento
    return False
