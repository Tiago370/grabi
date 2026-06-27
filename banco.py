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

    @classmethod
    def get_all(cls):
        with cls.conn() as con:
            con.row_factory = sqlite3.Row
            rows = con.execute(
                f"SELECT {','.join(cls.fields)} FROM {cls.table}"
            ).fetchall()

        return [cls(**dict(row)) for row in rows]

    @classmethod
    def filter(cls, where="", params=()):
        colunas = "*" if not cls.fields else ",".join(cls.fields)
        query = f"SELECT {colunas} FROM {cls.table}"

        if where:
            query += f" WHERE {where}"

        with cls.conn() as con:
            con.row_factory = sqlite3.Row
            rows = con.execute(query, params).fetchall()

        return [cls(**dict(row)) for row in rows]

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def between(cls, campo, inicio=None, fim=None):
        filtros = []
        params = []

        if inicio:
            filtros.append(f"{campo} >= ?")
            params.append(inicio)

        if fim:
            filtros.append(f"{campo} <= ?")
            params.append(fim)

        return cls.filter(
            " AND ".join(filtros),
            tuple(params)
        )

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
    pass
