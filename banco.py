import sqlite3


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

        with cls.conn() as con:
            cursor = con.execute(
                f"""
                SELECT {colunas}
                FROM {cls.table}
                WHERE {cls.identity}=?
                """,
                (value,)
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

if __name__ == "__main__":
    Produto(
        codigo="1234"
    ).save()
    print(Produto.get("1234").__dict__)
    Produto(
        codigo="1234",
        descricao="Teste 1234"
    ).save()
    print(Produto.get("1234").__dict__)

    Estabelecimento(
        cnpj="1234",
        nome="Teste Estabelecimento ORM 2",
        endereco="Av. Teste",
        latitude=0.123,
        longitude=1.234
    ).save()
