"""
County Health Explorer Streamlit Web Application
Author: Shahab Shakib
Purpose: Provides an interactive interface for exploring county-level public-health data, comparing health measures, and managing county notes.
"""


# Import Libraries
import pandas as pd
import streamlit as st
from sqlalchemy import text


# PAGE CONFIGURATION
st.set_page_config(
    page_title="County Health Explorer",
    page_icon="🏥",
    layout="wide",
)


# DATABASE CONNECTION
try:
    conn = st.connection("mysql", type="sql")

except Exception as error:
    st.error("The application could not connect to the database.")
    st.exception(error)
    st.stop()


# SESSION STATE
if "flash_message" not in st.session_state:
    st.session_state.flash_message = None

if "flash_action" not in st.session_state:
    st.session_state.flash_action = None

if "note_form_epoch" not in st.session_state:
    st.session_state.note_form_epoch = 0

if "last_note_action" not in st.session_state:
    st.session_state.last_note_action = None


# DATABASE WRITE HELPER
def execute_write(query, params=None):
    """
    Execute an INSERT, UPDATE, or DELETE statement and commit
    the database transaction.
    """

    with conn.session as session:
        session.execute(
            text(query),
            params or {},
        )
        session.commit()


# FLASH MESSAGE HELPER
def show_flash_message(action):
    """
    Display a saved success message below the relevant action.
    """

    if (
        st.session_state.flash_action == action
        and st.session_state.flash_message
    ):
        st.success(
            st.session_state.flash_message,
            icon="✅",
        )

        st.session_state.flash_message = None
        st.session_state.flash_action = None


# SIDEBAR
st.sidebar.title("County Health Explorer")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "County Explorer",
        "Measure Comparison",
        "County Notes",
    ],
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "CDC PLACES County Data, 2025 Release"
)


# HOME PAGE
if page == "Home":
    st.title("County Health Explorer")

    st.subheader(
        "A Public Health Database and Dashboard"
    )

    st.write(
        """
        County Health Explorer is an interactive application for exploring
        county-level public health estimates from the CDC PLACES 2025 dataset.

        The application makes a large public-health dataset easier to search,
        filter, compare, and understand. It is intended for students,
        public-health researchers, local health departments, community
        organizations, and policy analysts.
        """
    )

    st.subheader("Problem and Purpose")

    st.write(
        """
        The original CDC dataset contains more than 229,000 rows in a flat-file
        format. Although the file is useful for data distribution, it is not
        convenient for users who want to quickly explore counties, compare
        health indicators, or review public-health estimates without manually
        processing a large CSV file.

        This application connects to a normalized MySQL database and provides
        a browser-based interface for exploring the information.
        """
    )

    st.subheader("Main Features")

    st.markdown(
        """
        - Search counties by state and county name
        - View county population information
        - Filter public-health records by year, category, and prevalence type
        - Review estimates and confidence limits
        - Compare counties for a selected health measure
        - Display ranked county results in tables and charts
        - Create, review, update, and delete county notes
        - Filter notes by state, county, priority, and status
        """
    )

    try:
        state_count = conn.query(
            """
            SELECT COUNT(*) AS state_count
            FROM state;
            """,
            ttl=300,
        )

        county_count = conn.query(
            """
            SELECT COUNT(*) AS county_count
            FROM county;
            """,
            ttl=300,
        )

        measure_count = conn.query(
            """
            SELECT COUNT(*) AS measure_count
            FROM measure;
            """,
            ttl=300,
        )

        record_count = conn.query(
            """
            SELECT COUNT(*) AS record_count
            FROM countyhealthrecord;
            """,
            ttl=300,
        )

        note_count = conn.query(
            """
            SELECT COUNT(*) AS note_count
            FROM usernote;
            """,
            ttl=0,
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "States and Areas",
            f"{int(state_count.iloc[0]['state_count']):,}",
        )

        col2.metric(
            "Counties",
            f"{int(county_count.iloc[0]['county_count']):,}",
        )

        col3.metric(
            "Health Measures",
            f"{int(measure_count.iloc[0]['measure_count']):,}",
        )

        col4.metric(
            "Health Records",
            f"{int(record_count.iloc[0]['record_count']):,}",
        )

        col5.metric(
            "User Notes",
            f"{int(note_count.iloc[0]['note_count']):,}",
        )

    except Exception as error:
        st.warning(
            "The database summary could not be loaded."
        )
        st.exception(error)

    st.subheader("Data Source")

    st.write(
        """
        The application uses the CDC PLACES: Local Data for Better Health,
        County Data, 2025 Release. The database includes chronic-disease
        outcomes, preventive services, health-risk behaviors, disability,
        health status, and health-related social-needs measures.
        """
    )


# COUNTY EXPLORER PAGE
elif page == "County Explorer":
    st.title("County Explorer")

    st.write(
        """
        Select a state and county to view available public-health measures.
        Use the filters to change the year, prevalence type, and category.
        """
    )

    # LOAD STATES THAT HAVE COUNTIES
    try:
        states = conn.query(
            """
            SELECT DISTINCT
                s.state_id,
                s.state_abbr,
                s.state_name
            FROM state AS s
            JOIN county AS c
                ON s.state_id = c.state_id
            ORDER BY s.state_name;
            """,
            ttl=300,
        )

    except Exception as error:
        st.error(
            "The state list could not be loaded."
        )
        st.exception(error)
        st.stop()

    if states.empty:
        st.warning(
            "No states were found in the database."
        )
        st.stop()

    states["state_label"] = (
        states["state_name"]
        + " ("
        + states["state_abbr"]
        + ")"
    )

    selected_state_label = st.selectbox(
        "Select a state or reporting area",
        states["state_label"].tolist(),
        key="explorer_state",
    )

    selected_state_row = states[
        states["state_label"] == selected_state_label
    ].iloc[0]

    selected_state_id = int(
        selected_state_row["state_id"]
    )

    # LOAD COUNTIES
    try:
        counties = conn.query(
            """
            SELECT
                county_id,
                location_id,
                county_name,
                total_population,
                total_pop_18plus
            FROM county
            WHERE state_id = :state_id
            ORDER BY county_name;
            """,
            params={
                "state_id": selected_state_id,
            },
            ttl=0,
        )

    except Exception as error:
        st.error(
            "The county list could not be loaded."
        )
        st.exception(error)
        st.stop()

    if counties.empty:
        st.warning(
            "No counties were found for the selected state."
        )
        st.stop()

    counties["county_label"] = (
        counties["county_name"]
        + " - FIPS "
        + counties["location_id"]
    )

    selected_county_label = st.selectbox(
        "Select a county",
        counties["county_label"].tolist(),
        key="explorer_county",
    )

    selected_county_row = counties[
        counties["county_label"] == selected_county_label
    ].iloc[0]

    selected_county_id = int(
        selected_county_row["county_id"]
    )

    selected_county_name = selected_county_row[
        "county_name"
    ]

    location_id = selected_county_row[
        "location_id"
    ]

    # COUNTY PROFILE
    st.subheader(
        f"{selected_county_name} Profile"
    )

    population = selected_county_row[
        "total_population"
    ]

    adult_population = selected_county_row[
        "total_pop_18plus"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "County FIPS Code",
        location_id,
    )

    if pd.notna(population):
        col2.metric(
            "Total Population",
            f"{int(population):,}",
        )

    else:
        col2.metric(
            "Total Population",
            "Not available",
        )

    if pd.notna(adult_population):
        col3.metric(
            "Population Age 18+",
            f"{int(adult_population):,}",
        )

    else:
        col3.metric(
            "Population Age 18+",
            "Not available",
        )

    # LOAD FILTER OPTIONS
    try:
        years = conn.query(
            """
            SELECT DISTINCT year
            FROM countyhealthrecord
            WHERE county_id = :county_id
            ORDER BY year DESC;
            """,
            params={
                "county_id": selected_county_id,
            },
            ttl=0,
        )

        value_types = conn.query(
            """
            SELECT
                data_value_type_id,
                data_value_type_name
            FROM datavaluetype
            ORDER BY data_value_type_name;
            """,
            ttl=300,
        )

        categories = conn.query(
            """
            SELECT
                category_id,
                category_name
            FROM category
            ORDER BY category_name;
            """,
            ttl=300,
        )

    except Exception as error:
        st.error(
            "The filter options could not be loaded."
        )
        st.exception(error)
        st.stop()

    if years.empty:
        st.warning(
            "No health-record years were found for this county."
        )
        st.stop()

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    selected_year = filter_col1.selectbox(
        "Year",
        years["year"].astype(int).tolist(),
    )

    selected_value_type = filter_col2.selectbox(
        "Prevalence type",
        value_types[
            "data_value_type_name"
        ].tolist(),
    )

    category_options = (
        ["All categories"]
        + categories["category_name"].tolist()
    )

    selected_category = filter_col3.selectbox(
        "Category",
        category_options,
    )

    # BUILD HEALTH RECORD QUERY
    health_query = """
        SELECT
            category_name,
            measure_name,
            short_question_text,
            data_value_type_name,
            data_value,
            data_value_unit,
            low_confidence_limit,
            high_confidence_limit
        FROM vw_county_health_details
        WHERE location_id = :location_id
          AND year = :year
          AND data_value_type_name = :value_type
    """

    health_params = {
        "location_id": location_id,
        "year": int(selected_year),
        "value_type": selected_value_type,
    }

    if selected_category != "All categories":
        health_query += """
          AND category_name = :category_name
        """

        health_params["category_name"] = (
            selected_category
        )

    health_query += """
        ORDER BY category_name, measure_name;
    """

    # RETRIEVE HEALTH RECORDS
    try:
        health_records = conn.query(
            health_query,
            params=health_params,
            ttl=0,
        )

    except Exception as error:
        st.error(
            "The health records could not be loaded."
        )
        st.exception(error)
        st.stop()

    # DISPLAY HEALTH RECORDS
    st.subheader("Public Health Measures")

    if health_records.empty:
        st.info(
            "No records were found for the selected filters."
        )

    else:
        available_count = int(
            health_records["data_value"]
            .notna()
            .sum()
        )

        suppressed_count = int(
            health_records["data_value"]
            .isna()
            .sum()
        )

        metric_col1, metric_col2, metric_col3 = (
            st.columns(3)
        )

        metric_col1.metric(
            "Total Records",
            len(health_records),
        )

        metric_col2.metric(
            "Available Estimates",
            available_count,
        )

        metric_col3.metric(
            "Suppressed or Unavailable",
            suppressed_count,
        )

        display_records = health_records.rename(
            columns={
                "category_name": "Category",
                "measure_name": "Measure",
                "short_question_text": "Short Name",
                "data_value_type_name": "Value Type",
                "data_value": "Estimate",
                "data_value_unit": "Unit",
                "low_confidence_limit": (
                    "Low Confidence Limit"
                ),
                "high_confidence_limit": (
                    "High Confidence Limit"
                ),
            }
        )

        st.dataframe(
            display_records,
            use_container_width=True,
            hide_index=True,
        )


# MEASURE COMPARISON PAGE
elif page == "Measure Comparison":
    st.title("Measure Comparison")

    st.write(
        """
        Compare counties for a selected public-health measure.
        The table and chart rank counties with the highest
        published estimates for the selected year and prevalence type.
        """
    )

    # LOAD FILTER OPTIONS
    try:
        measures = conn.query(
            """
            SELECT
                m.measure_id,
                m.measure_name,
                m.short_question_text,
                c.category_name
            FROM measure AS m
            JOIN category AS c
                ON m.category_id = c.category_id
            ORDER BY
                c.category_name,
                m.measure_name;
            """,
            ttl=300,
        )

        comparison_years = conn.query(
            """
            SELECT DISTINCT year
            FROM countyhealthrecord
            ORDER BY year DESC;
            """,
            ttl=300,
        )

        comparison_types = conn.query(
            """
            SELECT
                data_value_type_id,
                data_value_type_name
            FROM datavaluetype
            ORDER BY data_value_type_name;
            """,
            ttl=300,
        )

    except Exception as error:
        st.error(
            "The comparison options could not be loaded."
        )
        st.exception(error)
        st.stop()

    if measures.empty:
        st.warning(
            "No measures were found in the database."
        )
        st.stop()

    measures["measure_label"] = (
        measures["category_name"]
        + " - "
        + measures["measure_name"]
    )

    filter_col1, filter_col2 = st.columns(2)

    selected_measure_label = filter_col1.selectbox(
        "Select a health measure",
        measures["measure_label"].tolist(),
    )

    selected_measure_row = measures[
        measures["measure_label"]
        == selected_measure_label
    ].iloc[0]

    selected_measure_id = selected_measure_row[
        "measure_id"
    ]

    selected_measure_name = selected_measure_row[
        "measure_name"
    ]

    selected_measure_category = selected_measure_row[
        "category_name"
    ]

    selected_comparison_year = filter_col2.selectbox(
        "Select a year",
        comparison_years[
            "year"
        ].astype(int).tolist(),
    )

    filter_col3, filter_col4 = st.columns(2)

    selected_comparison_type = filter_col3.selectbox(
        "Select a prevalence type",
        comparison_types[
            "data_value_type_name"
        ].tolist(),
    )

    result_limit = filter_col4.slider(
        "Number of counties to display",
        min_value=5,
        max_value=25,
        value=10,
        step=5,
    )

    safe_result_limit = int(result_limit)

    # RETRIEVE COMPARISON RESULTS
    comparison_query = f"""
        SELECT
            state_abbr,
            state_name,
            location_id,
            county_name,
            data_value,
            data_value_unit,
            low_confidence_limit,
            high_confidence_limit
        FROM vw_county_health_details
        WHERE year = :year
          AND measure_id = :measure_id
          AND data_value_type_name = :value_type
          AND data_value IS NOT NULL
        ORDER BY data_value DESC
        LIMIT {safe_result_limit};
    """

    try:
        comparison_results = conn.query(
            comparison_query,
            params={
                "year": int(
                    selected_comparison_year
                ),
                "measure_id": selected_measure_id,
                "value_type": selected_comparison_type,
            },
            ttl=0,
        )

    except Exception as error:
        st.error(
            "The county comparison could not be loaded."
        )
        st.exception(error)
        st.stop()

    # DISPLAY COMPARISON RESULTS
    st.subheader(selected_measure_name)

    st.write(
        f"**Category:** {selected_measure_category}"
    )

    st.caption(
        f"{selected_comparison_year} - "
        f"{selected_comparison_type}"
    )

    if comparison_results.empty:
        st.info(
            "No county estimates were found for the "
            "selected filters."
        )
        st.stop()

    highest_row = comparison_results.iloc[0]

    highest_value = float(
        highest_row["data_value"]
    )

    unit = highest_row["data_value_unit"]

    metric_col1, metric_col2, metric_col3 = (
        st.columns(3)
    )

    metric_col1.metric(
        "Highest County",
        highest_row["county_name"],
    )

    metric_col2.metric(
        "State",
        highest_row["state_abbr"],
    )

    metric_col3.metric(
        "Highest Estimate",
        f"{highest_value:.2f} {unit}",
    )

    comparison_results["county_state"] = (
        comparison_results["county_name"]
        + ", "
        + comparison_results["state_abbr"]
    )

    chart_data = comparison_results[
        [
            "county_state",
            "data_value",
        ]
    ].copy()

    chart_data = chart_data.rename(
        columns={
            "data_value": "Estimate",
        }
    )

    chart_data = chart_data.set_index(
        "county_state"
    )

    chart_data = chart_data.sort_values(
        by="Estimate",
        ascending=True,
    )

    st.subheader("Ranked County Chart")

    st.bar_chart(
        chart_data,
        horizontal=True,
        use_container_width=True,
    )

    st.subheader("Detailed Results")

    display_results = comparison_results[
        [
            "state_abbr",
            "state_name",
            "location_id",
            "county_name",
            "data_value",
            "data_value_unit",
            "low_confidence_limit",
            "high_confidence_limit",
        ]
    ].copy()

    display_results.insert(
        0,
        "Rank",
        range(1, len(display_results) + 1),
    )

    display_results = display_results.rename(
        columns={
            "state_abbr": "State",
            "state_name": "State Name",
            "location_id": "County FIPS",
            "county_name": "County",
            "data_value": "Estimate",
            "data_value_unit": "Unit",
            "low_confidence_limit": (
                "Low Confidence Limit"
            ),
            "high_confidence_limit": (
                "High Confidence Limit"
            ),
        }
    )

    st.dataframe(
        display_results,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        """
        Rankings include only records with a published estimate.
        Suppressed or unavailable CDC values are excluded from
        this comparison.
        """
    )


# COUNTY NOTES PAGE
elif page == "County Notes":
    st.title("County Notes")

    st.write(
        """
        Create and manage research notes or priority labels for
        counties. Notes can apply to an entire county or to a
        specific public-health measure.
        """
    )

    # NOTE ACTION SELECTOR
    note_action = st.radio(
        "Choose an action",
        [
            "View Notes",
            "Create Note",
            "Update Note",
            "Delete Note",
        ],
        horizontal=True,
        key="note_action",
    )

    # Refresh form widgets when the selected action changes.
    if note_action != st.session_state.last_note_action:
        st.session_state.note_form_epoch += 1
        st.session_state.last_note_action = note_action

        current_action_name = (
            note_action
            .lower()
            .replace(" note", "")
            .replace(" notes", "")
        )

        if (
            st.session_state.flash_action
            and st.session_state.flash_action
            != current_action_name
        ):
            st.session_state.flash_message = None
            st.session_state.flash_action = None

    form_epoch = st.session_state.note_form_epoch

    # LOAD STATES AND MEASURES
    try:
        note_states = conn.query(
            """
            SELECT DISTINCT
                s.state_id,
                s.state_abbr,
                s.state_name
            FROM state AS s
            JOIN county AS c
                ON s.state_id = c.state_id
            ORDER BY s.state_name;
            """,
            ttl=300,
        )

        note_measures = conn.query(
            """
            SELECT
                measure_id,
                measure_name
            FROM measure
            ORDER BY measure_name;
            """,
            ttl=300,
        )

    except Exception as error:
        st.error(
            "The note options could not be loaded."
        )
        st.exception(error)
        st.stop()

    if note_states.empty:
        st.warning(
            "No states were found in the database."
        )
        st.stop()

    note_states["state_label"] = (
        note_states["state_name"]
        + " ("
        + note_states["state_abbr"]
        + ")"
    )

    # VIEW NOTES
    if note_action == "View Notes":
        st.subheader("View County Notes")

        st.write(
            """
            Select a state, county, priority, and status to review
            saved notes. Select All states and areas and All counties
            to display every note.
            """
        )

        # STATE FILTER
        view_state_options = (
            ["All states and areas"]
            + note_states["state_label"].tolist()
        )

        selected_view_state_label = st.selectbox(
            "Select a state or reporting area",
            view_state_options,
            key=f"view_state_{form_epoch}",
        )

        selected_view_state_id = None

        if selected_view_state_label != "All states and areas":
            selected_view_state_row = note_states[
                note_states["state_label"]
                == selected_view_state_label
            ].iloc[0]

            selected_view_state_id = int(
                selected_view_state_row["state_id"]
            )

        # COUNTY FILTER
        try:
            if selected_view_state_id is None:
                view_counties = conn.query(
                    """
                    SELECT
                        c.county_id,
                        c.county_name,
                        c.location_id,
                        s.state_abbr,
                        s.state_name
                    FROM county AS c
                    JOIN state AS s
                        ON c.state_id = s.state_id
                    ORDER BY
                        s.state_name,
                        c.county_name;
                    """,
                    ttl=0,
                )

            else:
                view_counties = conn.query(
                    """
                    SELECT
                        c.county_id,
                        c.county_name,
                        c.location_id,
                        s.state_abbr,
                        s.state_name
                    FROM county AS c
                    JOIN state AS s
                        ON c.state_id = s.state_id
                    WHERE c.state_id = :state_id
                    ORDER BY c.county_name;
                    """,
                    params={
                        "state_id": selected_view_state_id,
                    },
                    ttl=0,
                )

        except Exception as error:
            st.error(
                "The county filter could not be loaded."
            )
            st.exception(error)
            st.stop()

        if view_counties.empty:
            st.warning(
                "No counties were found."
            )
            st.stop()

        view_counties["county_label"] = (
            view_counties["county_name"]
            + ", "
            + view_counties["state_abbr"]
            + " - FIPS "
            + view_counties["location_id"]
        )

        view_county_options = (
            ["All counties"]
            + view_counties["county_label"].tolist()
        )

        selected_view_county_label = st.selectbox(
            "Select a county",
            view_county_options,
            key=f"view_county_{form_epoch}",
        )

        selected_view_county_id = None

        if selected_view_county_label != "All counties":
            selected_view_county_row = view_counties[
                view_counties["county_label"]
                == selected_view_county_label
            ].iloc[0]

            selected_view_county_id = int(
                selected_view_county_row["county_id"]
            )

        # PRIORITY AND STATUS FILTERS
        filter_col1, filter_col2 = st.columns(2)

        selected_priority_filter = filter_col1.selectbox(
            "Priority",
            [
                "All priorities",
                "Low",
                "Medium",
                "High",
            ],
            key=f"view_priority_{form_epoch}",
        )

        selected_status_filter = filter_col2.selectbox(
            "Status",
            [
                "All statuses",
                "Open",
                "In Progress",
                "Closed",
            ],
            key=f"view_status_{form_epoch}",
        )

        # BUILD NOTE QUERY
        view_notes_query = """
            SELECT
                n.note_id,
                s.state_name,
                s.state_abbr,
                c.county_name,
                c.location_id,
                m.measure_name,
                n.note_text,
                n.priority_level,
                n.status,
                n.created_at,
                n.updated_at
            FROM usernote AS n
            JOIN county AS c
                ON n.county_id = c.county_id
            JOIN state AS s
                ON c.state_id = s.state_id
            LEFT JOIN measure AS m
                ON n.measure_id = m.measure_id
            WHERE 1 = 1
        """

        view_notes_params = {}

        if selected_view_state_id is not None:
            view_notes_query += """
                AND s.state_id = :state_id
            """

            view_notes_params["state_id"] = (
                selected_view_state_id
            )

        if selected_view_county_id is not None:
            view_notes_query += """
                AND c.county_id = :county_id
            """

            view_notes_params["county_id"] = (
                selected_view_county_id
            )

        if selected_priority_filter != "All priorities":
            view_notes_query += """
                AND n.priority_level = :priority_level
            """

            view_notes_params["priority_level"] = (
                selected_priority_filter
            )

        if selected_status_filter != "All statuses":
            view_notes_query += """
                AND n.status = :status
            """

            view_notes_params["status"] = (
                selected_status_filter
            )

        view_notes_query += """
            ORDER BY
                n.updated_at DESC,
                n.note_id DESC;
        """

        # LOAD FILTERED NOTES
        try:
            view_notes = conn.query(
                view_notes_query,
                params=view_notes_params,
                ttl=0,
            )

        except Exception as error:
            st.error(
                "The notes could not be loaded."
            )
            st.exception(error)
            st.stop()

        # DISPLAY FILTERED NOTES
        if view_notes.empty:
            st.info(
                "No notes match the selected filters."
            )

        else:
            view_notes["measure_name"] = (
                view_notes["measure_name"]
                .fillna("General county note")
            )

            open_note_count = int(
                (
                    view_notes["status"] == "Open"
                ).sum()
            )

            high_priority_count = int(
                (
                    view_notes["priority_level"] == "High"
                ).sum()
            )

            metric_col1, metric_col2, metric_col3 = (
                st.columns(3)
            )

            metric_col1.metric(
                "Displayed Notes",
                len(view_notes),
            )

            metric_col2.metric(
                "Open Notes",
                open_note_count,
            )

            metric_col3.metric(
                "High-Priority Notes",
                high_priority_count,
            )

            view_notes_display = view_notes[
                [
                    "note_id",
                    "state_name",
                    "state_abbr",
                    "county_name",
                    "location_id",
                    "measure_name",
                    "note_text",
                    "priority_level",
                    "status",
                    "created_at",
                    "updated_at",
                ]
            ].rename(
                columns={
                    "note_id": "Note ID",
                    "state_name": "State or Area",
                    "state_abbr": "Abbreviation",
                    "county_name": "County",
                    "location_id": "County FIPS",
                    "measure_name": "Measure",
                    "note_text": "Note",
                    "priority_level": "Priority",
                    "status": "Status",
                    "created_at": "Created",
                    "updated_at": "Updated",
                }
            )

            st.dataframe(
                view_notes_display,
                use_container_width=True,
                hide_index=True,
            )

    # CREATE, UPDATE, AND DELETE NOTE
    else:
        # STATE SELECTOR
        selected_note_state_label = st.selectbox(
            "Select a state or reporting area",
            note_states["state_label"].tolist(),
            key=f"note_state_{form_epoch}",
        )

        selected_note_state = note_states[
            note_states["state_label"]
            == selected_note_state_label
        ].iloc[0]

        selected_note_state_id = int(
            selected_note_state["state_id"]
        )

        # COUNTY SELECTOR
        try:
            note_counties = conn.query(
                """
                SELECT
                    county_id,
                    county_name,
                    location_id
                FROM county
                WHERE state_id = :state_id
                ORDER BY county_name;
                """,
                params={
                    "state_id": selected_note_state_id,
                },
                ttl=0,
            )

        except Exception as error:
            st.error(
                "The county list could not be loaded."
            )
            st.exception(error)
            st.stop()

        if note_counties.empty:
            st.warning(
                "No counties were found for the selected state."
            )
            st.stop()

        note_counties["county_label"] = (
            note_counties["county_name"]
            + " - FIPS "
            + note_counties["location_id"]
        )

        selected_note_county_label = st.selectbox(
            "Select a county",
            note_counties["county_label"].tolist(),
            key=f"note_county_{form_epoch}",
        )

        selected_note_county = note_counties[
            note_counties["county_label"]
            == selected_note_county_label
        ].iloc[0]

        selected_note_county_id = int(
            selected_note_county["county_id"]
        )

        selected_note_county_name = (
            selected_note_county["county_name"]
        )

        # MEASURE OPTIONS
        measure_options = {
            "General county note": None
        }

        for _, measure_row in note_measures.iterrows():
            measure_options[
                measure_row["measure_name"]
            ] = measure_row["measure_id"]

        # LOAD NOTES FOR SELECTED COUNTY
        try:
            county_notes = conn.query(
                """
                SELECT
                    n.note_id,
                    n.note_text,
                    n.priority_level,
                    n.status,
                    n.created_at,
                    n.updated_at,
                    n.measure_id,
                    m.measure_name
                FROM usernote AS n
                LEFT JOIN measure AS m
                    ON n.measure_id = m.measure_id
                WHERE n.county_id = :county_id
                ORDER BY
                    n.updated_at DESC,
                    n.note_id DESC;
                """,
                params={
                    "county_id": selected_note_county_id,
                },
                ttl=0,
            )

        except Exception as error:
            st.error(
                "The county notes could not be loaded."
            )
            st.exception(error)
            st.stop()

        # CREATE NOTE
        if note_action == "Create Note":
            st.subheader(
                f"Create a Note for "
                f"{selected_note_county_name}"
            )

            with st.form(
                f"create_note_form_{form_epoch}",
                clear_on_submit=True,
            ):
                create_measure_label = st.selectbox(
                    "Associated health measure",
                    list(measure_options.keys()),
                    key=f"create_measure_{form_epoch}",
                )

                create_priority = st.selectbox(
                    "Priority level",
                    [
                        "Low",
                        "Medium",
                        "High",
                    ],
                    key=f"create_priority_{form_epoch}",
                )

                create_status = st.selectbox(
                    "Status",
                    [
                        "Open",
                        "In Progress",
                        "Closed",
                    ],
                    key=f"create_status_{form_epoch}",
                )

                create_note_text = st.text_area(
                    "Note",
                    placeholder=(
                        "Enter a research note, observation, "
                        "or follow-up item."
                    ),
                    height=140,
                    key=f"create_text_{form_epoch}",
                )

                create_submitted = (
                    st.form_submit_button(
                        "Create Note"
                    )
                )

            if create_submitted:
                cleaned_note = create_note_text.strip()

                if not cleaned_note:
                    st.error(
                        "Please enter note text."
                    )

                else:
                    selected_measure_value = (
                        measure_options[
                            create_measure_label
                        ]
                    )

                    try:
                        execute_write(
                            """
                            INSERT INTO usernote (
                                county_id,
                                measure_id,
                                note_text,
                                priority_level,
                                status
                            )
                            VALUES (
                                :county_id,
                                :measure_id,
                                :note_text,
                                :priority_level,
                                :status
                            );
                            """,
                            {
                                "county_id": (
                                    selected_note_county_id
                                ),
                                "measure_id": (
                                    selected_measure_value
                                ),
                                "note_text": cleaned_note,
                                "priority_level": (
                                    create_priority
                                ),
                                "status": create_status,
                            },
                        )

                        st.session_state.flash_message = (
                            "The note was created successfully."
                        )

                        st.session_state.flash_action = (
                            "create"
                        )

                        st.session_state.note_form_epoch += 1

                        st.rerun()

                    except Exception as error:
                        st.error(
                            "The note could not be created."
                        )
                        st.exception(error)

            show_flash_message("create")

        # UPDATE NOTE
        elif note_action == "Update Note":
            st.subheader(
                f"Update a Note for "
                f"{selected_note_county_name}"
            )

            if county_notes.empty:
                st.info(
                    "Create a note before using the update feature."
                )

            else:
                update_labels = {}

                for _, note_row in county_notes.iterrows():
                    preview = str(
                        note_row["note_text"]
                    )

                    if len(preview) > 55:
                        preview = preview[:55] + "..."

                    label = (
                        f"Note {int(note_row['note_id'])}: "
                        f"{preview}"
                    )

                    update_labels[label] = int(
                        note_row["note_id"]
                    )

                selected_update_label = st.selectbox(
                    "Select a note to update",
                    list(update_labels.keys()),
                    key=(
                        f"update_note_selection_"
                        f"{form_epoch}"
                    ),
                )

                selected_update_id = update_labels[
                    selected_update_label
                ]

                current_note = county_notes[
                    county_notes["note_id"]
                    == selected_update_id
                ].iloc[0]

                current_measure_label = (
                    "General county note"
                )

                if pd.notna(
                    current_note["measure_id"]
                ):
                    matching_measure = note_measures[
                        note_measures["measure_id"]
                        == current_note["measure_id"]
                    ]

                    if not matching_measure.empty:
                        current_measure_label = (
                            matching_measure[
                                "measure_name"
                            ].iloc[0]
                        )

                measure_label_list = list(
                    measure_options.keys()
                )

                if (
                    current_measure_label
                    in measure_label_list
                ):
                    current_measure_index = (
                        measure_label_list.index(
                            current_measure_label
                        )
                    )

                else:
                    current_measure_index = 0

                priority_options = [
                    "Low",
                    "Medium",
                    "High",
                ]

                status_options = [
                    "Open",
                    "In Progress",
                    "Closed",
                ]

                current_priority = current_note[
                    "priority_level"
                ]

                current_status = current_note[
                    "status"
                ]

                priority_index = (
                    priority_options.index(
                        current_priority
                    )
                    if current_priority
                    in priority_options
                    else 0
                )

                status_index = (
                    status_options.index(
                        current_status
                    )
                    if current_status
                    in status_options
                    else 0
                )

                update_widget_key = (
                    f"{form_epoch}_"
                    f"{selected_update_id}"
                )

                with st.form(
                    f"update_note_form_"
                    f"{update_widget_key}"
                ):
                    update_measure_label = st.selectbox(
                        "Associated health measure",
                        measure_label_list,
                        index=current_measure_index,
                        key=(
                            f"update_measure_"
                            f"{update_widget_key}"
                        ),
                    )

                    update_priority = st.selectbox(
                        "Priority level",
                        priority_options,
                        index=priority_index,
                        key=(
                            f"update_priority_"
                            f"{update_widget_key}"
                        ),
                    )

                    update_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_index,
                        key=(
                            f"update_status_"
                            f"{update_widget_key}"
                        ),
                    )

                    update_note_text = st.text_area(
                        "Note",
                        value=str(
                            current_note["note_text"]
                        ),
                        height=140,
                        key=(
                            f"update_text_"
                            f"{update_widget_key}"
                        ),
                    )

                    update_submitted = (
                        st.form_submit_button(
                            "Save Changes"
                        )
                    )

                if update_submitted:
                    cleaned_update_text = (
                        update_note_text.strip()
                    )

                    if not cleaned_update_text:
                        st.error(
                            "The note text cannot be empty."
                        )

                    else:
                        update_measure_id = (
                            measure_options[
                                update_measure_label
                            ]
                        )

                        try:
                            execute_write(
                                """
                                UPDATE usernote
                                SET
                                    measure_id = :measure_id,
                                    note_text = :note_text,
                                    priority_level = :priority_level,
                                    status = :status
                                WHERE note_id = :note_id
                                  AND county_id = :county_id;
                                """,
                                {
                                    "measure_id": (
                                        update_measure_id
                                    ),
                                    "note_text": (
                                        cleaned_update_text
                                    ),
                                    "priority_level": (
                                        update_priority
                                    ),
                                    "status": update_status,
                                    "note_id": (
                                        selected_update_id
                                    ),
                                    "county_id": (
                                        selected_note_county_id
                                    ),
                                },
                            )

                            st.session_state.flash_message = (
                                "The note was updated successfully."
                            )

                            st.session_state.flash_action = (
                                "update"
                            )

                            st.session_state.note_form_epoch += 1

                            st.rerun()

                        except Exception as error:
                            st.error(
                                "The note could not be updated."
                            )
                            st.exception(error)

            show_flash_message("update")

        # DELETE NOTE
        elif note_action == "Delete Note":
            st.subheader(
                f"Delete a Note for "
                f"{selected_note_county_name}"
            )

            if county_notes.empty:
                st.info(
                    "There are no notes available to delete."
                )

            else:
                delete_labels = {}

                for _, note_row in county_notes.iterrows():
                    preview = str(
                        note_row["note_text"]
                    )

                    if len(preview) > 55:
                        preview = preview[:55] + "..."

                    label = (
                        f"Note {int(note_row['note_id'])}: "
                        f"{preview}"
                    )

                    delete_labels[label] = int(
                        note_row["note_id"]
                    )

                selected_delete_label = st.selectbox(
                    "Select a note to delete",
                    list(delete_labels.keys()),
                    key=(
                        f"delete_note_selection_"
                        f"{form_epoch}"
                    ),
                )

                selected_delete_id = delete_labels[
                    selected_delete_label
                ]

                delete_note_row = county_notes[
                    county_notes["note_id"]
                    == selected_delete_id
                ].iloc[0]

                st.warning(
                    "Deleting a note cannot be undone."
                )

                st.write(
                    f"**Selected note:** "
                    f"{delete_note_row['note_text']}"
                )

                confirm_delete = st.checkbox(
                    "I confirm that I want to delete "
                    "this note.",
                    key=(
                        f"confirm_delete_"
                        f"{form_epoch}"
                    ),
                )

                if st.button(
                    "Delete Note",
                    type="primary",
                    disabled=not confirm_delete,
                    key=(
                        f"delete_button_"
                        f"{form_epoch}"
                    ),
                ):
                    try:
                        execute_write(
                            """
                            DELETE FROM usernote
                            WHERE note_id = :note_id
                              AND county_id = :county_id;
                            """,
                            {
                                "note_id": (
                                    selected_delete_id
                                ),
                                "county_id": (
                                    selected_note_county_id
                                ),
                            },
                        )

                        st.session_state.flash_message = (
                            "The note was deleted successfully."
                        )

                        st.session_state.flash_action = (
                            "delete"
                        )

                        st.session_state.note_form_epoch += 1

                        st.rerun()

                    except Exception as error:
                        st.error(
                            "The note could not be deleted."
                        )
                        st.exception(error)

            show_flash_message("delete")