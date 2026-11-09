-- Banco de dados do CaronaEscolar (SQLite)
CREATE TABLE IF NOT EXISTS usuarios (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    tipo       TEXT NOT NULL CHECK (tipo IN ('motorista', 'passageiro'))
);

CREATE TABLE IF NOT EXISTS escolas (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    nome     TEXT NOT NULL UNIQUE,
    endereco TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS viagens (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    motorista_id INTEGER NOT NULL REFERENCES usuarios(id),
    escola_id    INTEGER NOT NULL REFERENCES escolas(id),
    tipo         TEXT NOT NULL CHECK (tipo IN ('carona', 'van')),
    origem       TEXT NOT NULL,
    horario      TEXT NOT NULL,
    vagas        INTEGER NOT NULL CHECK (vagas > 0)
);

CREATE TABLE IF NOT EXISTS reservas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    viagem_id    INTEGER NOT NULL REFERENCES viagens(id),
    passageiro_id INTEGER NOT NULL REFERENCES usuarios(id),
    criada_em    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (viagem_id, passageiro_id)
);

INSERT OR IGNORE INTO escolas (nome, endereco) VALUES
    ('Colégio Estadual Central', 'Av. Brasil, 1000'),
    ('Escola Municipal Santos Dumont', 'Rua das Flores, 250'),
    ('Instituto Federal - Campus Norte', 'Rod. PR-317, km 5');
