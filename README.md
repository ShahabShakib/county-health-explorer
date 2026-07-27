County Health Explorer

Author: Shahab Shakib  
Course Project: Applied Database Technologies  
Dataset: CDC PLACES County Data, 2025 Release  
Source File (as downloaded from CDC): PLACES_Local_Data_for_Better_Health_County_Data_2025_release.csv  
Source File (renamed for local use): places_county_2025_working.csv


Database: MySQL

Project Overview

County Health Explorer is a relational MySQL database for storing and analyzing county level public health estimates from the CDC PLACES dataset.
The database separates states, counties, health categories, measures, data value types, county health records, and user notes into related tables.


Project Files

`sql/county_health_explorer_schema.sql`  
Creates the database tables, keys, constraints, indexes, staging table, and reporting view.

`sql/county_health_explorer_load.sql`  
Loads normalized data from the staging table and performs validation checks.

`sql/county_health_explorer_queries.sql`  
Contains demonstration queries for filtering, aggregation, joins, subqueries, comparisons, missing data analysis, and reporting.

`diagrams/county_health_er_diagram.png`  
Entity relationship diagram for the database.

Execution Order

1.Run `sql/county_health_explorer_schema.sql`.

2.Import `places_county_2025_working.csv` (downloaded from CDC as `PLACES_Local_Data_for_Better_Health_County_Data_2025_release.csv`) into `places_county_staging`.

3.Run `sql/county_health_explorer_load.sql`.

4.Run `sql/county_health_explorer_queries.sql`.


Expected Row Counts

Object - Expected rows

State - 52
Category - 6
DataValueType - 2
Measure - 40
County - 3144 
CountyHealthRecord - 229218
Staging table -229298
Excluded national summary rows - 80
Reporting view - 229218


Data Exclusion

The source file contains 80 United States national summary rows with `LocationID = 59` and no county name. These rows are intentionally excluded from `CountyHealthRecord` because they do not represent a county and cannot satisfy the county foreign-key relationship.


Data Quality Notes

Blank numeric values are initially stored as text in the staging table.
Blank numeric values are converted to `NULL` during normalized loading.
Suppressed or unavailable estimates are stored with NULL data values.
Source footnote fields remain only in the raw staging table and are not included in the normalized reporting tables or application.
Longitude and latitude are extracted from WKT `POINT` values.
A source encoding artifact in the colorectal screening measure name is corrected during loading.


Validation Results

I confirmed there were no orphan records.
I found no duplicate health records.
I verified that updated_at changed automatically.
I confirmed that note priority and status rules worked correctly.

