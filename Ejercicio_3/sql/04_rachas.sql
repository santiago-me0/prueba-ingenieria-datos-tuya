-- ============================================================
-- Exercise 3 - Rachas
-- Customer balance streak calculation
-- ============================================================
--
-- Parameters:
--
--   :fecha_base
--       Historical point in time from which the analysis
--       must be performed.
--
--   :n
--       Minimum streak length required.
--
-- Final output:
--
--   identificacion
--   racha
--   fecha_fin
--   nivel
--
-- ============================================================


WITH RECURSIVE


-- ============================================================
-- 1. PARAMETERS
-- ============================================================

params AS (
    SELECT
        DATE(:fecha_base) AS fecha_base,
        CAST(:n AS INTEGER) AS n
),


-- ============================================================
-- 2. EFFECTIVE BASE DATE
-- ============================================================
--
-- fecha_base may be:
--
--   2024-06-15
--   2024-06-30
--   2025-01-31
--
-- Instead of generating artificial months beyond the source
-- horizon, the analysis uses the latest monthly cut available
-- in the dataset that is <= fecha_base.
--
-- Example:
--
-- fecha_base = 2024-06-15
-- effective cut = 2024-05-31
--
-- fecha_base = 2025-06-30
-- source ends = 2024-12-31
-- effective cut = 2024-12-31
--
-- ============================================================

effective_params AS (
    SELECT
        p.fecha_base,
        p.n,

        (
            SELECT MAX(h.corte_mes)
            FROM historia_prepared AS h
            WHERE DATE(h.corte_mes) <= p.fecha_base
        ) AS fecha_corte_base

    FROM params AS p
),


-- ============================================================
-- 3. CUSTOMER ANALYSIS LIMITS
-- ============================================================
--
-- A customer starts being evaluated from their first
-- appearance in history.
--
-- Therefore, months BEFORE the first appearance are never
-- generated as N0.
--
-- The final month is limited by:
--
--   1. fecha_base / available data horizon
--   2. fecha_retiro, when applicable
--
-- A monthly cut later than fecha_retiro must not be generated.
--
-- ============================================================

client_limits AS (
    SELECT
        h.identificacion,

        MIN(h.corte_mes) AS fecha_inicio,

        CASE
            -- Active customer: use the effective base cut.
            WHEN r.fecha_retiro IS NULL
                THEN p.fecha_corte_base

            -- Retired customer: use the earliest limit between
            -- fecha_base and the last month-end <= retirement.
            ELSE MIN(
                p.fecha_corte_base,

                CASE
                    -- Retirement occurred exactly at month-end.
                    WHEN DATE(r.fecha_retiro) =
                         DATE(
                             r.fecha_retiro,
                             'start of month',
                             '+1 month',
                             '-1 day'
                         )
                        THEN DATE(r.fecha_retiro)

                    -- Retirement occurred during the month.
                    -- The current month-end would be greater
                    -- than fecha_retiro, so use previous month.
                    ELSE DATE(
                        r.fecha_retiro,
                        'start of month',
                        '-1 day'
                    )
                END
            )
        END AS fecha_fin_permitida

    FROM historia_prepared AS h

    CROSS JOIN effective_params AS p

    LEFT JOIN retiros_prepared AS r
        ON r.identificacion = h.identificacion

    GROUP BY
        h.identificacion,
        r.fecha_retiro,
        p.fecha_corte_base
),


-- ============================================================
-- 4. MONTHLY CALENDAR BY CUSTOMER
-- ============================================================
--
-- Generate every month-end between:
--
--     first appearance
--          and
--     allowed final month
--
-- This makes missing months explicit.
--
-- Example:
--
-- 2024-01-31
-- 2024-02-29
-- [missing March]
-- 2024-04-30
--
-- becomes:
--
-- 2024-01-31
-- 2024-02-29
-- 2024-03-31
-- 2024-04-30
--
-- ============================================================

customer_calendar AS (
    -- First month.
    SELECT
        identificacion,
        fecha_inicio AS corte_mes,
        fecha_fin_permitida
    FROM client_limits
    WHERE DATE(fecha_inicio) <= DATE(fecha_fin_permitida)

    UNION ALL

    -- Following month-ends.
    SELECT
        identificacion,

        DATE(
            corte_mes,
            'start of month',
            '+2 months',
            '-1 day'
        ) AS corte_mes,

        fecha_fin_permitida

    FROM customer_calendar

    WHERE DATE(
              corte_mes,
              'start of month',
              '+2 months',
              '-1 day'
          ) <= DATE(fecha_fin_permitida)
),


-- ============================================================
-- 5. COMPLETE MONTHLY SERIES
-- ============================================================
--
-- Join the generated calendar against the real history.
--
-- Missing month:
--
--     saldo = 0
--
-- according to the business rule defined by the exercise.
--
-- imputed_n0 is preserved internally for traceability.
--
-- ============================================================

monthly_series AS (
    SELECT
        c.identificacion,
        c.corte_mes,

        COALESCE(
            h.saldo,
            0
        ) AS saldo,

        CASE
            WHEN h.identificacion IS NULL
                THEN 1
            ELSE 0
        END AS imputed_n0

    FROM customer_calendar AS c

    LEFT JOIN historia_prepared AS h
        ON h.identificacion = c.identificacion
       AND h.corte_mes = c.corte_mes
),


-- ============================================================
-- 6. BALANCE LEVEL CLASSIFICATION
-- ============================================================
--
-- N0: saldo >= 0          and < 300,000
-- N1: saldo >= 300,000    and < 1,000,000
-- N2: saldo >= 1,000,000  and < 3,000,000
-- N3: saldo >= 3,000,000  and < 5,000,000
-- N4: saldo >= 5,000,000
--
-- Missing months were assigned saldo = 0, therefore they
-- naturally become N0.
--
-- ============================================================

classified AS (
    SELECT
        identificacion,
        corte_mes,
        saldo,
        imputed_n0,

        CASE
            WHEN saldo >= 0
             AND saldo < 300000
                THEN 'N0'

            WHEN saldo >= 300000
             AND saldo < 1000000
                THEN 'N1'

            WHEN saldo >= 1000000
             AND saldo < 3000000
                THEN 'N2'

            WHEN saldo >= 3000000
             AND saldo < 5000000
                THEN 'N3'

            WHEN saldo >= 5000000
                THEN 'N4'
        END AS nivel

    FROM monthly_series
),


-- ============================================================
-- 7. DETECT STREAK BOUNDARIES
-- ============================================================
--
-- Compare each level against the previous month.
--
-- ============================================================

streak_boundaries AS (
    SELECT
        identificacion,
        corte_mes,
        saldo,
        nivel,
        imputed_n0,

        CASE
            WHEN LAG(nivel) OVER (
                PARTITION BY identificacion
                ORDER BY corte_mes
            ) = nivel
                THEN 0

            ELSE 1
        END AS new_streak

    FROM classified
),


-- ============================================================
-- 8. ASSIGN STREAK GROUPS
-- ============================================================
--
-- Cumulative sum transforms each change into an "island".
--
-- ============================================================

streak_groups AS (
    SELECT
        identificacion,
        corte_mes,
        saldo,
        nivel,
        imputed_n0,

        SUM(new_streak) OVER (
            PARTITION BY identificacion
            ORDER BY corte_mes
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS streak_group

    FROM streak_boundaries
),


-- ============================================================
-- 9. CALCULATE STREAKS
-- ============================================================

streaks AS (
    SELECT
        identificacion,
        nivel,
        streak_group,

        COUNT(*) AS racha,

        MIN(corte_mes) AS fecha_inicio,
        MAX(corte_mes) AS fecha_fin,

        -- Internal audit information.
        SUM(imputed_n0) AS meses_imputados

    FROM streak_groups

    GROUP BY
        identificacion,
        nivel,
        streak_group
),


-- ============================================================
-- 10. MINIMUM STREAK FILTER
-- ============================================================
--
-- Only streaks with length >= n are eligible.
--
-- ============================================================

eligible_streaks AS (
    SELECT
        s.identificacion,
        s.nivel,
        s.racha,
        s.fecha_inicio,
        s.fecha_fin,
        s.meses_imputados

    FROM streaks AS s

    CROSS JOIN effective_params AS p

    WHERE s.racha >= p.n
),


-- ============================================================
-- 11. BUSINESS-RULE RANKING
-- ============================================================
--
-- Requirement:
--
-- 1. Select the longest streak.
--
-- 2. If more than one streak has the same maximum length,
--    select the one whose end date is the most recent,
--    while still being <= fecha_base.
--
-- ROW_NUMBER guarantees one selected streak per customer.
--
-- ============================================================

ranked_streaks AS (
    SELECT
        identificacion,
        racha,
        fecha_fin,
        nivel,

        ROW_NUMBER() OVER (
            PARTITION BY identificacion
            ORDER BY
                racha DESC,
                fecha_fin DESC
        ) AS rn

    FROM eligible_streaks
)


-- ============================================================
-- 12. FINAL RESULT
-- ============================================================

SELECT
    identificacion,
    racha,
    fecha_fin,
    nivel

FROM ranked_streaks

WHERE rn = 1

ORDER BY identificacion;