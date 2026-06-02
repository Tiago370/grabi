from flask import Blueprint, render_template, redirect, request, session
from utils import db, calcular_total
from math import radians, sin, cos, sqrt, atan2
consulta_bp = Blueprint("consulta", __name__)

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
            estabelecimento = get_estabelecimento(latitude,longitude)
            if estabelecimento:
                session["estabelecimento_cnpj"] = estabelecimento["cnpj"]
                session["estabelecimento_nome"] = estabelecimento["nome"]

        if request.form.get("acao") == "go_atualizar_estabelecimento":
            return render_template("set_estabelecimento.html")

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
            session["codigo"] = codigo
            if not preco:
                return render_template("produto_nao_monitorado.html") 
            else:
                return render_template("verificar_preco.html",preco=preco[3],produto=produto[2],estabelecimento=session["estabelecimento_nome"])
            conn.close()
        if request.form.get("acao") == "cadastrar_preco":
            valor=request.form.get("preco")
            codigo=session["codigo"]
            cnpj=session["estabelecimento_cnpj"]
            conn=db();cur=conn.cursor()
            cur.execute(
                """
                INSERT INTO preco (codigo, cnpj, valor)
                VALUES (?, ?, ?)
                ON CONFLICT(codigo, cnpj)
                DO UPDATE SET valor = excluded.valor
                """,
                (codigo, cnpj, valor)
            )
            conn.commit()

    if request.form.get("acao") == "verificar_preco":
        resposta=request.form.get("resposta")
        if resposta == "sim":
            #mostrar comparação
            conn=db();cur=conn.cursor()
            codigo=session["codigo"]
            cnpj=session["estabelecimento_cnpj"]
            cur.execute("SELECT id, codigo, descricao FROM produto WHERE codigo = ?", (codigo,))
            produto = cur.fetchone()
            produto_descricao = produto[2]
            #buscar todos os preços
            cur.execute("SELECT e.nome,e.endereco,p.valor FROM estabelecimento e INNER JOIN preco p ON e.cnpj = p.cnpj WHERE p.codigo = ?", (codigo,))
            precos = cur.fetchall()
            print(precos)
            lista_precos = []
            for preco in precos:
                estabelecimento = preco[0]
                endereco = preco[1]
                valor = preco[2]
                preco_obj ={"estabelecimento":estabelecimento,"endereco":endereco,"preco":valor}
                lista_precos.append(preco_obj)
            print(lista_precos)
            return render_template("comparacao_preco.html",precos=lista_precos)
            
        elif resposta == "nao":
            # mostrar tela de atualizaça de preço
            conn=db();cur=conn.cursor()
            codigo=session["codigo"]
            #cur.execute("SELECT id, codigo, cnpj, valor FROM preco WHERE codigo = ?", (codigo,))
            #precos = cur.fetchoneA()

    if not session.get("estabelecimento_cnpj") or not session.get("estabelecimento_nome"):
        return render_template("set_estabelecimento.html")
    return render_template("consulta.html",estabelecimento=session["estabelecimento_nome"])
