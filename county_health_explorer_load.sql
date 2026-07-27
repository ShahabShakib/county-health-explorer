USE mydb;


-- 1. USERNOTE VALIDATION AND TIMESTAMP BEHAVIOR
-- Author: Shahab Shakib
-- Restricts UserNote priority and status to valid values.

ALTER TABLE UserNote
MODIFY priority_level ENUM(
    'Low',
    'Medium',
    'High'
) NULL;

ALTER TABLE UserNote
MODIFY status ENUM(
    'Open',
    'In Progress',
    'Closed'
) NULL;


-- Author: Shahab Shakib
-- Automatically records when a UserNote row is updated.

ALTER TABLE UserNote
MODIFY updated_at DATETIME
DEFAULT CURRENT_TIMESTAMP
ON UPDATE CURRENT_TIMESTAMP;


-- 2. CLEAR PREVIOUS NORMALIZED DATA
-- Author: Shahab Shakib
-- Records are removed in child-to-parent order to preserve
-- referential integrity.

DELETE FROM UserNote;
DELETE FROM CountyHealthRecord;
DELETE FROM County;
DELETE FROM Measure;
DELETE FROM DataValueType;
DELETE FROM Category;
DELETE FROM State;


-- Reset numeric auto-increment values for reproducible IDs.

ALTER TABLE UserNote AUTO_INCREMENT = 1;
ALTER TABLE CountyHealthRecord AUTO_INCREMENT = 1;
ALTER TABLE County AUTO_INCREMENT = 1;
ALTER TABLE Category AUTO_INCREMENT = 1;
ALTER TABLE State AUTO_INCREMENT = 1;


-- 3. LOAD STATE
-- Author: Shahab Shakib
-- Loads one row for each state or reporting area represented
-- in the source data.

INSERT INTO State (
    state_abbr,
    state_name
)
SELECT DISTINCT
    TRIM(StateAbbr) AS state_abbr,
    TRIM(StateDesc) AS state_name
FROM places_county_staging
WHERE NULLIF(TRIM(StateAbbr), '') IS NOT NULL
  AND NULLIF(TRIM(StateDesc), '') IS NOT NULL
ORDER BY state_abbr;


-- 4. LOAD CATEGORY
-- Author: Shahab Shakib
-- Loads the distinct public-health measure categories.

INSERT INTO Category (
    category_name
)
SELECT DISTINCT
    TRIM(Category) AS category_name
FROM places_county_staging
WHERE NULLIF(TRIM(Category), '') IS NOT NULL
ORDER BY category_name;


-- 5. LOAD DATA VALUE TYPE
-- Author: Shahab Shakib
-- Loads the source data-value classifications, including crude
-- and age-adjusted prevalence.

INSERT INTO DataValueType (
    data_value_type_id,
    data_value_type_name,
    data_value_unit
)
SELECT DISTINCT
    TRIM(DataValueTypeID) AS data_value_type_id,
    TRIM(Data_Value_Type) AS data_value_type_name,
    NULLIF(TRIM(Data_Value_Unit), '') AS data_value_unit
FROM places_county_staging
WHERE NULLIF(TRIM(DataValueTypeID), '') IS NOT NULL;


-- 6. LOAD MEASURE
-- Author: Shahab Shakib
-- Loads the distinct health measures and connects each measure
-- to its category.

INSERT INTO Measure (
    measure_id,
    measure_name,
    short_question_text,
    category_id
)
SELECT DISTINCT
    TRIM(s.MeasureId) AS measure_id,
    TRIM(s.Measure) AS measure_name,
    NULLIF(TRIM(s.Short_Question_Text), '') AS short_question_text,
    c.category_id
FROM places_county_staging AS s
JOIN Category AS c
    ON c.category_name = TRIM(s.Category)
WHERE NULLIF(TRIM(s.MeasureId), '') IS NOT NULL;


-- Author: Shahab Shakib
-- Corrects a text-encoding artifact in the colorectal screening
-- measure name.

UPDATE Measure
SET measure_name =
    'Colorectal cancer screening among adults aged 45–75 years'
WHERE measure_id = 'COLON_SCREEN';


-- 7. LOAD COUNTY
-- Author: Shahab Shakib
-- Loads one row per county/location and extracts longitude and
-- latitude from the source WKT POINT value.
--
-- WKT format:
--   POINT (longitude latitude)

INSERT INTO County (
    location_id,
    county_name,
    state_id,
    total_population,
    total_pop_18plus,
    latitude,
    longitude
)
SELECT
    TRIM(s.LocationID) AS location_id,
    TRIM(s.LocationName) AS county_name,
    st.state_id,

    MAX(
        CAST(
            NULLIF(TRIM(s.TotalPopulation), '')
            AS UNSIGNED
        )
    ) AS total_population,

    MAX(
        CAST(
            NULLIF(TRIM(s.TotalPop18plus), '')
            AS UNSIGNED
        )
    ) AS total_pop_18plus,

    MAX(
        CAST(
            NULLIF(
                TRIM(
                    TRAILING ')' FROM
                    SUBSTRING_INDEX(
                        TRIM(s.Geolocation),
                        ' ',
                        -1
                    )
                ),
                ''
            )
            AS DECIMAL(9,6)
        )
    ) AS latitude,

    MAX(
        CAST(
            NULLIF(
                TRIM(
                    LEADING '(' FROM
                    SUBSTRING_INDEX(
                        SUBSTRING_INDEX(
                            TRIM(s.Geolocation),
                            ' ',
                            2
                        ),
                        ' ',
                        -1
                    )
                ),
                ''
            )
            AS DECIMAL(9,6)
        )
    ) AS longitude

FROM places_county_staging AS s
JOIN State AS st
    ON st.state_abbr = TRIM(s.StateAbbr)

WHERE NULLIF(TRIM(s.LocationID), '') IS NOT NULL
  AND NULLIF(TRIM(s.LocationName), '') IS NOT NULL

GROUP BY
    TRIM(s.LocationID),
    TRIM(s.LocationName),
    st.state_id;


-- 8. LOAD COUNTY HEALTH RECORDS
-- Author: Shahab Shakib
-- Loads county-level health records from the CDC PLACES staging
-- table.
--
-- The source contains 80 national United States summary rows
-- with LocationID 59 and no county name. These rows are
-- intentionally excluded because they do not represent a county
-- and therefore cannot reference a County record.

INSERT INTO CountyHealthRecord (
    county_id,
    measure_id,
    data_value_type_id,
    year,
    data_source,
    data_value,
    low_confidence_limit,
    high_confidence_limit
)
SELECT
    c.county_id,
    TRIM(s.MeasureId) AS measure_id,
    TRIM(s.DataValueTypeID) AS data_value_type_id,
    CAST(s.Year AS UNSIGNED) AS year,
    NULLIF(TRIM(s.DataSource), '') AS data_source,

    CAST(
        NULLIF(TRIM(s.Data_Value), '')
        AS DECIMAL(6,2)
    ) AS data_value,

    CAST(
        NULLIF(TRIM(s.Low_Confidence_Limit), '')
        AS DECIMAL(6,2)
    ) AS low_confidence_limit,

    CAST(
        NULLIF(TRIM(s.High_Confidence_Limit), '')
        AS DECIMAL(6,2)
    ) AS high_confidence_limit

FROM places_county_staging AS s

JOIN County AS c
    ON c.location_id = TRIM(s.LocationID)

JOIN Measure AS m
    ON m.measure_id = TRIM(s.MeasureId)

JOIN DataValueType AS dvt
    ON dvt.data_value_type_id =
       TRIM(s.DataValueTypeID)

WHERE NULLIF(TRIM(s.Year), '') IS NOT NULL;


-- 9. CREATE REPORTING VIEW
-- Author: Shahab Shakib
-- Creates a readable denormalized view for reports, analysis,
-- and dashboard queries.

CREATE OR REPLACE VIEW vw_county_health_details AS
SELECT
    chr.record_id,
    chr.year,

    s.state_abbr,
    s.state_name,

    c.location_id,
    c.county_name,
    c.total_population,
    c.total_pop_18plus,
    c.latitude,
    c.longitude,

    cat.category_name,

    m.measure_id,
    m.measure_name,
    m.short_question_text,

    dvt.data_value_type_name,
    dvt.data_value_unit,

    chr.data_source,
    chr.data_value,
    chr.low_confidence_limit,
    chr.high_confidence_limit

FROM CountyHealthRecord AS chr

JOIN County AS c
    ON chr.county_id = c.county_id

JOIN State AS s
    ON c.state_id = s.state_id

JOIN Measure AS m
    ON chr.measure_id = m.measure_id

JOIN Category AS cat
    ON m.category_id = cat.category_id

JOIN DataValueType AS dvt
    ON chr.data_value_type_id =
       dvt.data_value_type_id;


-- 10. POPULATION VERIFICATION
-- Author: Shahab Shakib
-- Expected values:
-- State:                              52
-- Category:                        6
-- DataValueType:              2
-- Measure:                        40
-- County:                           3,144
-- CountyHealthRecord:     229,218
-- Excluded national rows: 80

SELECT 'State' AS table_name, COUNT(*) AS row_count
FROM State

UNION ALL

SELECT 'Category', COUNT(*)
FROM Category

UNION ALL

SELECT 'DataValueType', COUNT(*)
FROM DataValueType

UNION ALL

SELECT 'Measure', COUNT(*)
FROM Measure

UNION ALL

SELECT 'County', COUNT(*)
FROM County

UNION ALL

SELECT 'CountyHealthRecord', COUNT(*)
FROM CountyHealthRecord

UNION ALL

SELECT 'Reporting View', COUNT(*)
FROM vw_county_health_details;


-- Reconciles the source staging rows with the county-level rows
-- and the intentionally excluded national records.

SELECT
    (
        SELECT COUNT(*)
        FROM places_county_staging
    ) AS staging_rows,

    (
        SELECT COUNT(*)
        FROM CountyHealthRecord
    ) AS county_health_rows,

    (
        SELECT COUNT(*)
        FROM places_county_staging AS s
        LEFT JOIN County AS c
            ON c.location_id = TRIM(s.LocationID)
        WHERE c.county_id IS NULL
    ) AS excluded_national_rows;


-- 11. REFERENTIAL-INTEGRITY VERIFICATION
-- Author: Shahab Shakib
-- Each query should return zero.

SELECT COUNT(*) AS orphan_counties
FROM County AS c
LEFT JOIN State AS s
    ON c.state_id = s.state_id
WHERE s.state_id IS NULL;


SELECT COUNT(*) AS orphan_measures
FROM Measure AS m
LEFT JOIN Category AS c
    ON m.category_id = c.category_id
WHERE c.category_id IS NULL;


SELECT COUNT(*) AS orphan_health_records
FROM CountyHealthRecord AS chr

LEFT JOIN County AS c
    ON chr.county_id = c.county_id

LEFT JOIN Measure AS m
    ON chr.measure_id = m.measure_id

LEFT JOIN DataValueType AS dvt
    ON chr.data_value_type_id =
       dvt.data_value_type_id

WHERE c.county_id IS NULL
   OR m.measure_id IS NULL
   OR dvt.data_value_type_id IS NULL;


-- 12. DUPLICATE VERIFICATION
-- Author: Shahab Shakib
-- This query should return zero rows.

SELECT
    county_id,
    measure_id,
    data_value_type_id,
    year,
    COUNT(*) AS duplicate_count
FROM CountyHealthRecord
GROUP BY
    county_id,
    measure_id,
    data_value_type_id,
    year
HAVING COUNT(*) > 1;


-- 13. YEAR DISTRIBUTION
-- Author: Shahab Shakib
-- Expected:
-- 2022:  31,440
-- 2023: 197,778

SELECT
    year,
    COUNT(*) AS record_count
FROM CountyHealthRecord
GROUP BY year
ORDER BY year;
