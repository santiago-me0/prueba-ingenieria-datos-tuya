-- ============================================================
-- Exercise 3 - Rachas
-- Data preparation and quarantine
-- ============================================================
--
-- This script prepares the source data used by the streak
-- calculation while preserving all original information in
-- the RAW tables.
--
-- Layers created:
--
--   data_quality_issues
--       Audit log describing detected source-data problems
--       and the resolution applied.
--
--   historia_quarantine
--       Source history records requiring review.
--
--   retiros_prepared
--       Retirement information prepared for business logic.
--
--   historia_prepared
--       Customer-month history ready for streak processing.
--
-- ============================================================


DROP TABLE IF EXISTS data_quality_issues;
DROP TABLE IF EXISTS historia_quarantine;
DROP TABLE IF EXISTS retiros_prepared;
DROP TABLE IF EXISTS historia_prepared;


-- ============================================================
-- 1. DATA QUALITY AUDIT
-- ============================================================

CREATE TABLE data_quality_issues (
    issue_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type     TEXT NOT NULL,
    identificacion TEXT,
    corte_mes      TEXT,
    details        TEXT NOT NULL,
    resolution     TEXT NOT NULL
);


-- ============================================================
-- 2. QUARANTINE
-- ============================================================
--
-- RAW is still the original source of truth.
--
-- This table provides an explicit collection of history
-- records that require review or were excluded from the
-- calculation.
--
-- One source record may theoretically have more than one
-- quality issue, therefore the primary key also includes
-- issue_type.
-- ============================================================

CREATE TABLE historia_quarantine (
    source_row_id  INTEGER NOT NULL,
    identificacion TEXT NOT NULL,
    corte_mes      TEXT NOT NULL,
    saldo          INTEGER NOT NULL,
    issue_type     TEXT NOT NULL,

    PRIMARY KEY (source_row_id, issue_type)
);


-- ============================================================
-- 3. EXACT DUPLICATES
-- ============================================================
--
-- Same customer, same month and same balance.
--
-- Because both records contain exactly the same business
-- information, keeping one occurrence is considered a safe
-- deterministic deduplication rule.
--
-- The original records remain available in historia_raw.
-- ============================================================

INSERT INTO data_quality_issues (
    issue_type,
    identificacion,
    corte_mes,
    details,
    resolution
)
SELECT
    'EXACT_DUPLICATE',
    identificacion,
    corte_mes,
    'Same customer, month and balance appears '
        || COUNT(*) || ' times. Balance=' || saldo,
    'DEDUPLICATED_KEEP_ONE'
FROM historia_raw
GROUP BY
    identificacion,
    corte_mes,
    saldo
HAVING COUNT(*) > 1;


-- ============================================================
-- 4. CONFLICTING CUSTOMER-MONTH BALANCES
-- ============================================================
--
-- Same customer and month but different balances.
--
-- These source rows are copied to quarantine because the
-- source does not provide enough information to determine
-- which value is objectively correct.
-- ============================================================

INSERT INTO historia_quarantine (
    source_row_id,
    identificacion,
    corte_mes,
    saldo,
    issue_type
)
SELECT
    h.row_id,
    h.identificacion,
    h.corte_mes,
    h.saldo,
    'CONFLICTING_BALANCE'
FROM historia_raw AS h
INNER JOIN (
    SELECT
        identificacion,
        corte_mes
    FROM historia_raw
    GROUP BY
        identificacion,
        corte_mes
    HAVING COUNT(DISTINCT saldo) > 1
) AS conflicts
    ON conflicts.identificacion = h.identificacion
   AND conflicts.corte_mes = h.corte_mes;


INSERT INTO data_quality_issues (
    issue_type,
    identificacion,
    corte_mes,
    details,
    resolution
)
SELECT
    'CONFLICTING_BALANCE',
    identificacion,
    corte_mes,
    'Different balances exist for the same customer-month. '
        || 'MIN=' || MIN(saldo)
        || ', MAX=' || MAX(saldo),
    'MAX_BALANCE_USED'
FROM historia_raw
GROUP BY
    identificacion,
    corte_mes
HAVING COUNT(DISTINCT saldo) > 1;


-- ============================================================
-- 5. RETIREMENT DUPLICATES
-- ============================================================
--
-- If multiple retirement dates exist, the earliest one is
-- selected as a conservative deterministic rule.
-- ============================================================

INSERT INTO data_quality_issues (
    issue_type,
    identificacion,
    corte_mes,
    details,
    resolution
)
SELECT
    'MULTIPLE_RETIREMENT_DATES',
    identificacion,
    NULL,
    'Multiple retirement records found. '
        || 'First=' || MIN(fecha_retiro)
        || ', Last=' || MAX(fecha_retiro),
    'EARLIEST_RETIREMENT_USED'
FROM retiros_raw
GROUP BY identificacion
HAVING COUNT(*) > 1;


CREATE TABLE retiros_prepared (
    identificacion     TEXT PRIMARY KEY,
    fecha_retiro       TEXT NOT NULL,
    preparation_status TEXT NOT NULL
);


INSERT INTO retiros_prepared (
    identificacion,
    fecha_retiro,
    preparation_status
)
SELECT
    identificacion,
    MIN(fecha_retiro),
    CASE
        WHEN COUNT(*) > 1
            THEN 'MULTIPLE_DATES_EARLIEST_USED'
        ELSE 'ORIGINAL'
    END
FROM retiros_raw
GROUP BY identificacion;


-- ============================================================
-- 6. RETIREMENTS WITHOUT HISTORY
-- ============================================================
-- A retirement is considered related to history only when
-- the identifier matches exactly.
-- ============================================================

INSERT INTO data_quality_issues (
    issue_type,
    identificacion,
    corte_mes,
    details,
    resolution
)
SELECT
    'RETIREMENT_WITHOUT_HISTORY',
    r.identificacion,
    NULL,
    'Retirement identifier has no exact match in history.',
    'NO_MATCH_NO_INFERENCE'
FROM retiros_prepared AS r
LEFT JOIN historia_raw AS h
    ON h.identificacion = r.identificacion
WHERE h.identificacion IS NULL;


-- ============================================================
-- 7. HISTORY AFTER RETIREMENT
-- ============================================================
--
-- Records whose monthly cut is later than the retirement
-- date are preserved in RAW and copied to quarantine.
--
-- They will not participate in the streak calculation.
-- ============================================================

INSERT INTO historia_quarantine (
    source_row_id,
    identificacion,
    corte_mes,
    saldo,
    issue_type
)
SELECT
    h.row_id,
    h.identificacion,
    h.corte_mes,
    h.saldo,
    'POST_RETIREMENT_RECORD'
FROM historia_raw AS h
INNER JOIN retiros_prepared AS r
    ON r.identificacion = h.identificacion
WHERE DATE(h.corte_mes) > DATE(r.fecha_retiro);


INSERT INTO data_quality_issues (
    issue_type,
    identificacion,
    corte_mes,
    details,
    resolution
)
SELECT
    'POST_RETIREMENT_RECORD',
    h.identificacion,
    h.corte_mes,
    'History record exists after retirement date '
        || r.fecha_retiro
        || '. Balance=' || h.saldo,
    'EXCLUDED_FROM_STREAK_CALCULATION'
FROM historia_raw AS h
INNER JOIN retiros_prepared AS r
    ON r.identificacion = h.identificacion
WHERE DATE(h.corte_mes) > DATE(r.fecha_retiro);


-- ============================================================
-- 8. PREPARED HISTORY
-- ============================================================
--
-- Rules:
--
-- 1. Records after retirement are excluded.
--
-- 2. Exact duplicates become one customer-month record.
--
-- 3. When different balances exist for the same customer-month,
--    MAX(saldo) is used as an explicit conservative fallback
--    rule so that debt is not underestimated.
--
--    The conflict remains registered in quarantine and in the
--    quality audit. In a production environment this fallback
--    could instead be replaced by source-system priority,
--    ingestion timestamp or manual resolution.
-- ============================================================

CREATE TABLE historia_prepared (
    identificacion     TEXT NOT NULL,
    corte_mes          TEXT NOT NULL,
    saldo              INTEGER NOT NULL,
    preparation_status TEXT NOT NULL,

    PRIMARY KEY (
        identificacion,
        corte_mes
    )
);


INSERT INTO historia_prepared (
    identificacion,
    corte_mes,
    saldo,
    preparation_status
)
SELECT
    h.identificacion,
    h.corte_mes,

    -- Conservative deterministic fallback for conflicting
    -- balances.
    MAX(h.saldo) AS saldo,

    CASE
        WHEN COUNT(DISTINCT h.saldo) > 1
            THEN 'CONFLICT_RESOLVED_MAX_BALANCE'

        WHEN COUNT(*) > 1
            THEN 'DEDUPLICATED_EXACT'

        ELSE 'ORIGINAL'
    END AS preparation_status

FROM historia_raw AS h

LEFT JOIN retiros_prepared AS r
    ON r.identificacion = h.identificacion

WHERE
    r.fecha_retiro IS NULL
    OR DATE(h.corte_mes) <= DATE(r.fecha_retiro)

GROUP BY
    h.identificacion,
    h.corte_mes;


-- ============================================================
-- 9. INDEXES
-- ============================================================

CREATE INDEX idx_historia_prepared_cliente_mes
    ON historia_prepared (
        identificacion,
        corte_mes
    );

CREATE INDEX idx_historia_prepared_corte
    ON historia_prepared (
        corte_mes
    );

CREATE INDEX idx_quality_issues_type
    ON data_quality_issues (
        issue_type
    );


-- ============================================================
-- 10. VALIDATION SUMMARY
-- ============================================================

SELECT
    'historia_raw' AS dataset,
    COUNT(*) AS records
FROM historia_raw

UNION ALL

SELECT
    'historia_prepared',
    COUNT(*)
FROM historia_prepared

UNION ALL

SELECT
    'historia_quarantine',
    COUNT(*)
FROM historia_quarantine;


-- ------------------------------------------------------------
-- Prepared-data status
-- ------------------------------------------------------------

SELECT
    preparation_status,
    COUNT(*) AS records
FROM historia_prepared
GROUP BY preparation_status
ORDER BY preparation_status;


-- ------------------------------------------------------------
-- Quality issues
-- ------------------------------------------------------------

SELECT
    issue_type,
    COUNT(*) AS occurrences
FROM data_quality_issues
GROUP BY issue_type
ORDER BY issue_type;