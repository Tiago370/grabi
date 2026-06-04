create table produto(
    id integer primary key autoincrement,
    codigo text not null unique,
    descricao text
);

create table venda(
    id integer primary key autoincrement,
    data text
);

create table item_venda(
    id integer primary key autoincrement,
    venda_id integer,
    produto_id integer,
    quantidade real,
    descricao text,
    preco_unit real,
    foreign key(venda_id) references venda(id),
    foreign key(produto_id) references produto(id)
);

create table pack(
    id integer primary key autoincrement,
    nome_pl text,
    nome_sg text,
    mnemonico text,
    quantidade integer,
    codigo text,
    produto_id integer,
    foreign key(produto_id) references produto(id)
);

create table estabelecimento(
    id integer primary key autoincrement,
    cnpj text not null unique,
    nome text,
    endereco text,
    latitude real,
    longitude real
);

create table input(
    id integer primary key autoincrement,
    estabelecimento_id integer,
    produto_id integer,
    criado_em integer,
    preco real,
    foreign key(produto_id) references produto(id),
    foreign key(estabelecimento_id) references estabelecimento(id)
);

CREATE TABLE preco(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL,
    cnpj TEXT NOT NULL,
    valor REAL NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (codigo, cnpj)
);
