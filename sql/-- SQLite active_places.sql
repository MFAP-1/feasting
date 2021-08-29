-- SQLite
    CREATE TABLE IF NOT EXISTS 'active_places' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'users_id' INTEGER NOT NULL, 'nome_lugar' TEXT NOT NULL, 'cidade' TEXT NOT NULL, 'idas' INTEGER NOT NULL, 'tipo' TEXT NOT NULL, 'refeicao' TEXT NOT NULL, 'nota' NUMERIC NOT NULL, 'comentario' TEXT NOT NULL);
    CREATE UNIQUE INDEX 'id' ON "active_stocks" ("id");