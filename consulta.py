import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, request, session
from utils import db, render_page, get_estabelecimento
from dotenv import load_dotenv
import os

consulta_bp = Blueprint("consulta", __name__)

load_dotenv()
SENHA_ADMIN = os.getenv("SENHA_ADMIN")

def tempo_decorrido(data_str):
    data = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
    data = data - timedelta(hours=3)
    diff = datetime.now() - data

    segundos = int(diff.total_seconds())

    if segundos < 60:
        return "agora mesmo"

    if segundos < 3600:
        return f"há {segundos // 60} min"

    if segundos < 86400:
        return f"há {segundos // 3600} h"

    dias = segundos // 86400

    if dias == 1:
        return "ontem"

    return f"há {dias} dias"

def comparacao_preco(codigo, cnpj):
    conn=db();cur=conn.cursor()
    #mostrar comparação
    cur.execute("SELECT id, codigo, descricao FROM produto WHERE codigo = ?", (codigo,))
    produto = cur.fetchone()
    produto_descricao = produto[2] or produto[1]
    #buscar todos os preços
    cur.execute("SELECT e.nome,e.endereco,p.valor,p.updated_at FROM estabelecimento e INNER JOIN preco p ON e.cnpj = p.cnpj WHERE p.codigo = ?", (codigo,))
    precos = cur.fetchall()
    lista_precos = []
    for preco in precos:
        estabelecimento = preco[0]
        endereco = preco[1]
        valor = preco[2]
        atualizado_em = tempo_decorrido(preco[3])
        preco_obj ={"estabelecimento":estabelecimento,"endereco":endereco,"preco":valor,"atualizado_em":atualizado_em}
        lista_precos.append(preco_obj)
    return render_page("comparacao_preco.html",precos=lista_precos,produto=produto_descricao)

@consulta_bp.route("/consulta",methods=["GET","POST"])
@consulta_bp.route("/consulta/",methods=["GET","POST"])
def consulta():
    produto = False
    codigo = ""
    descricao = False

    if request.method=="POST":
        conn=db();cur=conn.cursor()
        if request.form.get("acao") == "atualizar_estabelecimento":
            latitude=float(request.form.get("latitude"))
            longitude=float(request.form.get("longitude"))
            estabelecimento = get_estabelecimento(latitude,longitude)
            if estabelecimento:
                session["estabelecimento_cnpj"] = estabelecimento["cnpj"]
                session["estabelecimento_nome"] = estabelecimento["nome"]

        if request.form.get("acao") == "go_atualizar_estabelecimento":
            return render_page("set_estabelecimento.html")

        if request.form.get("acao") == "consultar_preco":
            codigo=request.form.get("codigo")
            cur.execute("SELECT id, codigo, descricao FROM produto WHERE codigo = ?", (codigo,))
            produto = cur.fetchone()
            session["codigo"] = codigo
            if not produto:
                return render_page("produto_nao_cadastrado.html")

            produto_descricao = produto[2] or produto[1]
            cnpj=session["estabelecimento_cnpj"]
            cur.execute("SELECT id, codigo, cnpj, valor FROM preco WHERE codigo = ? and cnpj = ?", (codigo,cnpj))
            preco = cur.fetchone()
            if not preco:
                return render_page("produto_nao_monitorado.html") 
            else:
                return render_page("verificar_preco.html",preco=preco[3],produto=produto_descricao,estabelecimento=session["estabelecimento_nome"])

        if request.form.get("acao") == "cadastrar_preco":
            valor=request.form.get("preco")
            codigo=session["codigo"]
            cnpj=session["estabelecimento_cnpj"]
            cur.execute(
                """
                INSERT INTO preco (codigo, cnpj, valor)
                VALUES (?, ?, ?)
                ON CONFLICT(codigo, cnpj)
                DO UPDATE SET valor = excluded.valor,
                updated_at = CURRENT_TIMESTAMP
                """,
                (codigo, cnpj, valor)
            )
            conn.commit()
            conn.close()
            return comparacao_preco(codigo, cnpj)

        if request.form.get("acao") == "cadastrar_produto_preco":
            valor=request.form.get("preco")
            codigo=session["codigo"]
            cnpj=session["estabelecimento_cnpj"]
            cur.execute(
                """
                INSERT INTO produto (codigo)
                VALUES (?)
                """,
                (codigo,)
            )
            cur.execute(
                """
                INSERT INTO preco (codigo, cnpj, valor)
                VALUES (?, ?, ?)
                ON CONFLICT(codigo, cnpj)
                DO UPDATE SET valor = excluded.valor,
                updated_at = CURRENT_TIMESTAMP
                """,
	                (codigo, cnpj, valor)
            )
            conn.commit()
            conn.close()
            return comparacao_preco(codigo, cnpj)

    if request.form.get("acao") == "verificar_preco":
        resposta=request.form.get("resposta")
        codigo=session["codigo"]
        cnpj=session["estabelecimento_cnpj"]
        if session.get("admin"):
            novo_nome=request.form.get("novo_nome")
            cur.execute(
                """
                UPDATE produto
                SET descricao = ?
                WHERE codigo = ?;
                """,
                (novo_nome,codigo)
            )
            conn.commit()
        if resposta == "sim":
            return comparacao_preco(codigo, cnpj)
        elif resposta == "nao":
            cur.execute("SELECT id, codigo, cnpj, valor FROM preco WHERE codigo = ? and cnpj = ?", (codigo,cnpj))
            preco = cur.fetchone()
            preco_atual = preco[3]
            cur.execute("SELECT id, codigo, descricao FROM produto WHERE codigo = ?", (codigo,))
            produto = cur.fetchone()
            produto_descricao = produto[2] or produto[1]
            return render_page("atualizar_preco.html", preco_atual=preco_atual, produto=produto_descricao)

    if request.form.get("acao") == "atualizar_preco":
        codigo=session["codigo"]
        cnpj=session["estabelecimento_cnpj"]
        novo_preco=request.form.get("novo_preco")
        cur.execute(
                """
                UPDATE preco
		SET valor = ?,
    		updated_at = CURRENT_TIMESTAMP
		WHERE codigo = ? AND cnpj = ?;
                """,
            (novo_preco, codigo, cnpj))
        conn.commit()
        conn.close()
        return comparacao_preco(codigo, cnpj) 

    if not session.get("estabelecimento_cnpj") or not session.get("estabelecimento_nome"):
        return render_page("set_estabelecimento.html")
    return render_page("consulta.html",estabelecimento=session["estabelecimento_nome"])

@consulta_bp.route("/atualizar_estabelecimento",methods=["POST"])
def atualizar_estabelecimento():
    dados = request.get_json()
    latitude = dados["latitude"]
    longitude= dados["longitude"]
    estabelecimento = get_estabelecimento(latitude,longitude)
    if estabelecimento:
        session["estabelecimento_cnpj"] = estabelecimento["cnpj"]
        session["estabelecimento_nome"] = estabelecimento["nome"]
        session["timestamp_localizacao"] = time.time() 

    return "", 204
	
@consulta_bp.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("senha") == SENHA_ADMIN:
            session["admin"] = True
            return redirect("/")
        else:
            fail = True
            return render_template("admin.html", fail=fail)
    return render_template("admin.html")

@consulta_bp.route("/logout_admin")
def logout_admin():
    session.pop("admin", None)
    return redirect("/")
