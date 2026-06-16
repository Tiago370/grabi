import sqlite3
from datetime import datetime

class Model:
    table = ""
    identity = None
    fields = []
    database = "hml.db"

    @classmethod
    def conn(cls):
        return sqlite3.connect(cls.database)

    def __init__(self, **kwargs):
        for f in self.fields:
            setattr(self, f, kwargs.get(f))

    def save(self):
        valores = [getattr(self, f) for f in self.fields]
        colunas = ",".join(self.fields)
        placeholders = ",".join("?" for _ in valores)

        with self.conn() as con:
            con.execute(
                f"""
                INSERT OR REPLACE
                INTO {self.table}
                ({colunas})
                VALUES ({placeholders})
                """,
                valores
            )

    @classmethod
    def get(cls, value):
        colunas = "*" if not cls.fields else ",".join(cls.fields)

        if isinstance(cls.identity, (list, tuple)):
            if not isinstance(value, (list, tuple)):
                raise ValueError("value deve ser lista/tupla quando identity tiver múltiplos campos")

            if len(value) != len(cls.identity):
                raise ValueError("Quantidade de valores diferente da quantidade de campos identity")

            where = " AND ".join(f"{campo}=?" for campo in cls.identity)
            params = tuple(value)

        else:
            where = f"{cls.identity}=?"
            params = (value,)

        with cls.conn() as con:
            cursor = con.execute(
                f"""
                SELECT {colunas}
                FROM {cls.table}
                WHERE {where}
                """,
                params
            )

            row = cursor.fetchone()

            if not row:
                return None

            if cls.fields:
                dados = dict(zip(cls.fields, row))
            else:
                dados = dict(zip([c[0] for c in cursor.description], row))

        return cls(**dados).__dict__

class Produto(Model):
#    database = "catalogo.db"
    table = "produto"
    identity = "codigo"
    fields = ["codigo", "descricao"]

    @classmethod
    def get(cls, value):
        produto = super().get(value)

        if produto and not produto["descricao"]:
            produto["descricao"] = produto["codigo"]

        return produto

class Estabelecimento(Model):
    table = "estabelecimento"
    identity = "cnpj"
    fields = ["cnpj", "nome", "endereco", "latitude", "longitude"]

class Historico(Model):
    table = "historico"
    identity = ["codigo","cnpj","updated_at"]
    fields = ["codigo","cnpj","valor","updated_at"]

    def save(self):
        return super().save()

class Preco(Model):
    table = "preco"
    identity = ["codigo","cnpj"]
    fields = ["codigo","cnpj","valor","updated_at"]

    def save(self):
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Historico(
            codigo=self.codigo,
            cnpj=self.cnpj,
            valor=self.valor,
            updated_at=self.updated_at
        ).save()
        return super().save()

class GrupoProdutoRel(Model):
    table = "grupo_produto_rel"
    identity = ["slug_id","codigo"]
    fields = ["slug_id","codigo"]

class GrupoProduto(Model):
    table = "grupo_produto"
    identity = "slug_id"
    fields = ["slug_id","nome"]

    def add_produto(slug_id,codigo):
        GrupoProdutoRel(slug_id=slug_id,codigo=codigo)

    def produtos(slug_id):
        pass

if __name__ == "__main__":
    Produto(
        codigo="1234"
    ).save()
    print(Produto.get("1234"))
    Produto(
        codigo="1234",
        descricao="Teste 1234"
    ).save()
    print(Produto.get("1234"))

    Estabelecimento(
        cnpj="1234",
        nome="Teste Estabelecimento ORM 2",
        endereco="Av. Teste",
        latitude=0.123,
        longitude=1.234
    ).save()
    Preco(
        cnpj="123",
        codigo="122",
        valor=1.81,
    ).save()
    GrupoProduto(
        slug_id="arroz-branco",
        nome="Arroz Branco",
    ).save()
    print(GrupoProduto.get("arroz-branco"))
    GrupoProdutoRel(
        slug_id="arroz-branco",
        codigo="4",
    ).save()
    print(GrupoProdutoRel.get(("arroz-branco","4")))
    GrupoProduto.add_produto("arroz-branco","4")
    print(GrupoProduto.produtos("arroz-branco"))
