CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
);

CREATE TABLE medicamento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100)
);

CREATE TABLE lembrete (
    id SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuario(id),
    id_medicamento INT REFERENCES medicamento(id),
    horario TIME,
);

