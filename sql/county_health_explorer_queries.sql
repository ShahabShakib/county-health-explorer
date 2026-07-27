-- County Health Explorer
-- Demonstration Queries
-- Author: Shahab Shakib
-- Purpose: Demonstrates filtering, aggregation, joins, and note management

USE mydb;

-- Query 1:
-- Lists the highest crude-prevalence counties for arthritis in 2023.

SELECT
    state_abbr,
    county_name,
    measure_name,
    data_value_type_name,
    data_value,
    data_value_unit
FROM vw_county_health_details
WHERE year = 2023
  AND measure_id = 'ARTHRITIS'
  AND data_value_type_name = 'Crude prevalence'
  AND data_value IS NOT NULL
ORDER BY data_value DESC
LIMIT 10;

-- Query 2:
-- Calculates the average 2023 crude prevalence for each state
-- for the selected measure.

SELECT
    state_abbr,
    state_name,
    ROUND(AVG(data_value), 2) AS average_crude_prevalence,
    data_value_unit
FROM vw_county_health_details
WHERE year = 2023
  AND measure_id = 'ARTHRITIS'
  AND data_value_type_name = 'Crude prevalence'
  AND data_value IS NOT NULL
GROUP BY
    state_abbr,
    state_name,
    data_value_unit
ORDER BY average_crude_prevalence DESC;


-- Query 3:
-- Compares crude and age-adjusted prevalence for arthritis
-- within each county in 2023.

SELECT
    state_abbr,
    county_name,
    MAX(
        CASE
            WHEN data_value_type_name = 'Crude prevalence'
            THEN data_value
        END
    ) AS crude_prevalence,
    MAX(
        CASE
            WHEN data_value_type_name = 'Age-adjusted prevalence'
            THEN data_value
        END
    ) AS age_adjusted_prevalence,
    ROUND(
        MAX(
            CASE
                WHEN data_value_type_name = 'Crude prevalence'
                THEN data_value
            END
        )
        -
        MAX(
            CASE
                WHEN data_value_type_name = 'Age-adjusted prevalence'
                THEN data_value
            END
        ),
        2
    ) AS prevalence_difference
FROM vw_county_health_details
WHERE year = 2023
  AND measure_id = 'ARTHRITIS'
  AND data_value IS NOT NULL
GROUP BY
    state_abbr,
    county_name
HAVING crude_prevalence IS NOT NULL
   AND age_adjusted_prevalence IS NOT NULL
ORDER BY prevalence_difference DESC
LIMIT 10;


-- Query 4:
-- Counts county-level records by public-health category and year.

SELECT
    year,
    category_name,
    COUNT(*) AS record_count
FROM vw_county_health_details
GROUP BY
    year,
    category_name
ORDER BY
    year,
    record_count DESC;


-- Query 5:
-- Finds counties whose 2023 crude obesity prevalence is above
-- the average crude obesity prevalence for their state.

SELECT
    d.state_abbr,
    d.county_name,
    d.data_value AS county_obesity_prevalence,
    state_avg.average_obesity_prevalence,
    ROUND(
        d.data_value - state_avg.average_obesity_prevalence,
        2
    ) AS amount_above_state_average
FROM vw_county_health_details AS d
JOIN (
    SELECT
        state_abbr,
        AVG(data_value) AS average_obesity_prevalence
    FROM vw_county_health_details
    WHERE year = 2023
      AND measure_id = 'OBESITY'
      AND data_value_type_name = 'Crude prevalence'
      AND data_value IS NOT NULL
    GROUP BY state_abbr
) AS state_avg
    ON d.state_abbr = state_avg.state_abbr
WHERE d.year = 2023
  AND d.measure_id = 'OBESITY'
  AND d.data_value_type_name = 'Crude prevalence'
  AND d.data_value IS NOT NULL
  AND d.data_value > state_avg.average_obesity_prevalence
ORDER BY amount_above_state_average DESC
LIMIT 10;


-- Query 6:
-- Shows the number of counties represented in each state.

SELECT
    s.state_abbr,
    s.state_name,
    COUNT(c.county_id) AS county_count
FROM State AS s
LEFT JOIN County AS c
    ON s.state_id = c.state_id
GROUP BY
    s.state_abbr,
    s.state_name
ORDER BY county_count DESC, s.state_abbr;


-- Query 7:
-- Finds counties with the highest 2023 crude diabetes prevalence.

SELECT
    state_abbr,
    county_name,
    data_value AS diabetes_prevalence,
    data_value_unit
FROM vw_county_health_details
WHERE year = 2023
  AND measure_id = 'DIABETES'
  AND data_value_type_name = 'Crude prevalence'
  AND data_value IS NOT NULL
ORDER BY data_value DESC
LIMIT 10;

-- Query 8:
-- Lists counties with missing 2023 crude prevalence values
-- and identifies the affected measure.

SELECT
    state_abbr,
    county_name,
    measure_id,
    measure_name,
    data_value_type_name
FROM vw_county_health_details
WHERE year = 2023
  AND data_value_type_name = 'Crude prevalence'
  AND data_value IS NULL
ORDER BY
    state_abbr,
    county_name,
    measure_name
LIMIT 25;

-- Query 9:
-- Summarizes the number of suppressed county estimates by state
-- for 2023 crude prevalence records.

SELECT
    state_abbr,
    COUNT(*) AS suppressed_record_count
FROM vw_county_health_details
WHERE year = 2023
  AND data_value_type_name = 'Crude prevalence'
  AND data_value IS NULL
GROUP BY state_abbr
ORDER BY suppressed_record_count DESC;

-- Query 10:
-- Returns the county-level health record count by measure
-- for 2023 and highlights measures with the widest coverage.

SELECT
    measure_id,
    measure_name,
    COUNT(*) AS record_count,
    COUNT(DISTINCT location_id) AS county_count
FROM vw_county_health_details
WHERE year = 2023
GROUP BY
    measure_id,
    measure_name
ORDER BY
    county_count DESC,
    measure_name;
