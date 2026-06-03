import time
from flask import Blueprint, render_template, redirect, request, session
from utils import db, render_page, get_estabelecimento
consulta_bp = Blueprint("consulta", __name__)

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
            if not produto:
                return render_page("produto_nao_cadastrado.html")

            cnpj=session["estabelecimento_cnpj"]
            cur.execute("SELECT id, codigo, cnpj, valor FROM preco WHERE codigo = ? and cnpj = ?", (codigo,cnpj))
            preco = cur.fetchone()
            session["codigo"] = codigo
            if not preco:
                return render_page("produto_nao_monitorado.html") 
            else:
                return render_page("verificar_preco.html",preco=preco[3],produto=produto[2],estabelecimento=session["estabelecimento_nome"])

        if request.form.get("acao") == "cadastrar_preco":
            valor=request.form.get("preco")
            codigo=session["codigo"]
            cnpj=session["estabelecimento_cnpj"]
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
            codigo=session["codigo"]
            cnpj=session["estabelecimento_cnpj"]
            cur.execute("SELECT id, codigo, descricao FROM produto WHERE codigo = ?", (codigo,))
            produto = cur.fetchone()
            produto_descricao = produto[2]
            #buscar todos os preços
            cur.execute("SELECT e.nome,e.endereco,p.valor FROM estabelecimento e INNER JOIN preco p ON e.cnpj = p.cnpj WHERE p.codigo = ?", (codigo,))
            precos = cur.fetchall()
            lista_precos = []
            for preco in precos:
                estabelecimento = preco[0]
                endereco = preco[1]
                valor = preco[2]
                preco_obj ={"estabelecimento":estabelecimento,"endereco":endereco,"preco":valor}
                lista_precos.append(preco_obj)
            return render_page("comparacao_preco.html",precos=lista_precos)
            
        elif resposta == "nao":
            # mostrar tela de atualizaça de preço
            codigo=session["codigo"]
            #cur.execute("SELECT id, codigo, cnpj, valor FROM preco WHERE codigo = ?", (codigo,))
            #precos = cur.fetchoneA()

    if not session.get("estabelecimento_cnpj") or not session.get("estabelecimento_nome"):
        return render_page("set_estabelecimento.html")
    print('>>> Chamando render_page("consulta.html"...')
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
	
