-- ============================================================
-- Exercise 3 - Rachas
-- Database schema
-- ============================================================

DROP TABLE IF EXISTS historia_raw;
DROP TABLE IF EXISTS retiros_raw;


-- ------------------------------------------------------------
-- Raw monthly balance history
-- ------------------------------------------------------------
-- This table preserves the information received from the
-- source Excel file without deduplicating or modifying records.
--
-- No UNIQUE constraint is defined for
-- (identificacion, corte_mes) because duplicated records must
-- first be detected as part of the data-quality process.
-- ------------------------------------------------------------

CREATE TABLE historia_raw (
    row_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacion  TEXT NOT NULL,
    corte_mes       TEXT NOT NULL,
    saldo           INTEGER NOT NULL,

    CHECK (saldo >= 0),
    CHECK (date(corte_mes) IS NOT NULL)
);


-- ------------------------------------------------------------
-- Raw retirement information
-- ------------------------------------------------------------

CREATE TABLE retiros_raw (
    row_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacion  TEXT NOT NULL,
    fecha_retiro    TEXT NOT NULL,

    CHECK (date(fecha_retiro) IS NOT NULL)
);


-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------

CREATE INDEX idx_historia_identificacion
    ON historia_raw (identificacion);

CREATE INDEX idx_historia_corte_mes
    ON historia_raw (corte_mes);

CREATE INDEX idx_historia_cliente_mes
    ON historia_raw (identificacion, corte_mes);

CREATE INDEX idx_retiros_identificacion
    ON retiros_raw (identificacion);