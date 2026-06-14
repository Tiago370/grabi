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

class Produto(Model):
#    database = "catalogo.db"
    table = "produto"
    identity = "codigo"
    fields = ["codigo", "descricao"]

class Estabelecimento(Model):
    table = "estabelecimento"
    identity = "cnpj"
    fields = ["cnpj", "nome", "endereco", "latitude", "longitude"]

if __name__ == "__main__":
    Produto(
        codigo="123",
        descricao="Arroz Integral"
    ).save()

    Estabelecimento(
        cnpj="1234",
        nome="Teste Estabelecimento ORM 2",
        endereco="Av. Teste",
        latitude=0.123,
        longitude=1.234
    ).save()
