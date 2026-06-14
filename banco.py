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

if __name__ == "__main__":
    Produto(
        codigo="123",
        descricao="Arroz Integral"
    ).save()
