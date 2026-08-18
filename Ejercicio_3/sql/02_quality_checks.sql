-- ============================================================
-- Exercise 3 - Rachas
-- Data quality checks
-- ============================================================
--
-- These queries validate the source data before calculating
-- customer streaks.
--
-- The RAW tables are never modified by this script.
-- ============================================================


-- ------------------------------------------------------------
-- Q01 - Total records
-- ------------------------------------------------------------

SELECT
    'historia_raw' AS table_name,
    COUNT(*) AS total_records
FROM historia_raw

UNION ALL

SELECT
    'retiros_raw' AS table_name,
    COUNT(*) AS total_records
FROM retiros_raw;


-- ------------------------------------------------------------
-- Q02 - Null or empty identifiers
-- ------------------------------------------------------------

SELECT
    row_id,
    identificacion,
    corte_mes,
    saldo
FROM historia_raw
WHERE identificacion IS NULL
   OR TRIM(identificacion) = '';


-- ------------------------------------------------------------
-- Q03 - Invalid or null monthly dates
-- ------------------------------------------------------------

SELECT
    row_id,
    identificacion,
    corte_mes,
    saldo
FROM historia_raw
WHERE corte_mes IS NULL
   OR DATE(corte_mes) IS NULL;


-- ------------------------------------------------------------
-- Q04 - Invalid balances
-- ------------------------------------------------------------
-- According to the exercise, debt levels start at saldo >= 0.
-- Negative values therefore fall outside the expected domain.
-- ------------------------------------------------------------

SELECT
    row_id,
    identificacion,
    corte_mes,
    saldo
FROM historia_raw
WHERE saldo IS NULL
   OR saldo < 0;


-- ------------------------------------------------------------
-- Q05 - Monthly cut must be the last day of the month
-- ------------------------------------------------------------
-- Example:
-- 2024-01-31 -> valid
-- 2024-01-15 -> invalid
-- ------------------------------------------------------------

SELECT
    row_id,
    identificacion,
    corte_mes,
    saldo
FROM historia_raw
WHERE corte_mes <>
      DATE(corte_mes, 'start of month', '+1 month', '-1 day');


-- ------------------------------------------------------------
-- Q06 - Exact duplicate history records
-- ------------------------------------------------------------
--
-- Same customer, same month and same balance.
-- These records can be safely deduplicated during preparation
-- because they contain exactly the same business information.
-- ------------------------------------------------------------

SELECT
    identificacion,
    corte_mes,
    saldo,
    COUNT(*) AS occurrences
FROM historia_raw
GROUP BY
    identificacion,
    corte_mes,
    saldo
HAVING COUNT(*) > 1
ORDER BY
    identificacion,
    corte_mes;


-- ------------------------------------------------------------
-- Q07 - Conflicting customer-month records
-- ------------------------------------------------------------
--
-- Same customer and same month with more than one balance.

-- ------------------------------------------------------------

SELECT
    identificacion,
    corte_mes,
    COUNT(*) AS records,
    COUNT(DISTINCT saldo) AS distinct_balances,
    MIN(saldo) AS min_balance,
    MAX(saldo) AS max_balance
FROM historia_raw
GROUP BY
    identificacion,
    corte_mes
HAVING COUNT(DISTINCT saldo) > 1
ORDER BY
    identificacion,
    corte_mes;


-- ------------------------------------------------------------
-- Q08 - Duplicate retirement records
-- ------------------------------------------------------------

SELECT
    identificacion,
    COUNT(*) AS records,
    MIN(fecha_retiro) AS first_retirement_date,
    MAX(fecha_retiro) AS last_retirement_date
FROM retiros_raw
GROUP BY identificacion
HAVING COUNT(*) > 1
ORDER BY identificacion;


-- ------------------------------------------------------------
-- Q09 - Retirement customers without matching history
-- ------------------------------------------------------------

SELECT
    r.row_id,
    r.identificacion,
    r.fecha_retiro
FROM retiros_raw AS r
LEFT JOIN historia_raw AS h
    ON h.identificacion = r.identificacion
WHERE h.identificacion IS NULL
ORDER BY
    r.identificacion;


-- ------------------------------------------------------------
-- Q10 - History records after retirement
-- ------------------------------------------------------------

SELECT
    h.row_id,
    h.identificacion,
    h.corte_mes,
    h.saldo,
    r.fecha_retiro
FROM historia_raw AS h
INNER JOIN retiros_raw AS r
    ON r.identificacion = h.identificacion
WHERE DATE(h.corte_mes) > DATE(r.fecha_retiro)
ORDER BY
    h.identificacion,
    h.corte_mes;


-- ------------------------------------------------------------
-- Q11 - Summary: records after retirement
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS records_after_retirement
FROM historia_raw AS h
INNER JOIN retiros_raw AS r
    ON r.identificacion = h.identificacion
WHERE DATE(h.corte_mes) > DATE(r.fecha_retiro);


-- ------------------------------------------------------------
-- Q12 - History date range
-- ------------------------------------------------------------

SELECT
    MIN(corte_mes) AS min_month,
    MAX(corte_mes) AS max_month,
    COUNT(DISTINCT corte_mes) AS distinct_months
FROM historia_raw;


-- ------------------------------------------------------------
-- Q13 - Number of customers
-- ------------------------------------------------------------

SELECT
    COUNT(DISTINCT identificacion) AS distinct_customers
FROM historia_raw;


-- ------------------------------------------------------------
-- Q14 - Customer-month duplicate summary
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS duplicated_customer_months
FROM (
    SELECT
        identificacion,
        corte_mes
    FROM historia_raw
    GROUP BY
        identificacion,
        corte_mes
    HAVING COUNT(*) > 1
);


-- ------------------------------------------------------------
-- Q15 - Overall quality summary
-- ------------------------------------------------------------
--
-- This final query provides a compact summary that can be used
-- to validate the input before running the business logic.
-- ------------------------------------------------------------

SELECT
    (
        SELECT COUNT(*)
        FROM historia_raw
    ) AS history_records,

    (
        SELECT COUNT(DISTINCT identificacion)
        FROM historia_raw
    ) AS customers,

    (
        SELECT COUNT(DISTINCT corte_mes)
        FROM historia_raw
    ) AS months,

    (
        SELECT COUNT(*)
        FROM (
            SELECT
                identificacion,
                corte_mes
            FROM historia_raw
            GROUP BY
                identificacion,
                corte_mes
            HAVING COUNT(*) > 1
        )
    ) AS duplicated_customer_months,

    (
        SELECT COUNT(*)
        FROM (
            SELECT
                identificacion,
                corte_mes
            FROM historia_raw
            GROUP BY
                identificacion,
                corte_mes
            HAVING COUNT(DISTINCT saldo) > 1
        )
    ) AS conflicting_customer_months,

    (
        SELECT COUNT(*)
        FROM historia_raw AS h
        INNER JOIN retiros_raw AS r
            ON r.identificacion = h.identificacion
        WHERE DATE(h.corte_mes) > DATE(r.fecha_retiro)
    ) AS records_after_retirement,

    (
        SELECT COUNT(*)
        FROM retiros_raw AS r
        LEFT JOIN historia_raw AS h
            ON h.identificacion = r.identificacion
        WHERE h.identificacion IS NULL
    ) AS retirements_without_history;