
import streamlit as st
import sys
from pathlib import Path
from datetime import date

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables


# Create required tables
create_tables()

st.title("📋 Application Tracker")
st.write("Track your job and internship applications.")


# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login first.")
    st.stop()

user_id = st.session_state.get("user_id")

if user_id is None:
    st.error("❌ User ID not found.")
    st.info("Please logout and login again.")
    st.stop()


# --------------------------------------------------
# ADD NEW APPLICATION
# --------------------------------------------------

st.subheader("➕ Add New Application")

with st.form("application_form"):

    job_title = st.text_input(
        "Job Title",
        placeholder="Example: Python Developer"
    )

    company = st.text_input(
        "Company",
        placeholder="Example: Infosys"
    )

    location = st.text_input(
        "Location",
        placeholder="Example: Noida"
    )

    job_type = st.selectbox(
        "Job Type",
        [
            "Full Time",
            "Part Time",
            "Internship",
            "Remote"
        ]
    )

    application_date = st.date_input(
        "Application Date",
        value=date.today()
    )

    status = st.selectbox(
        "Application Status",
        [
            "Applied",
            "Under Review",
            "Interview",
            "Selected",
            "Rejected"
        ]
    )

    notes = st.text_area(
        "Notes",
        placeholder="Example: Applied through company website."
    )

    submitted = st.form_submit_button(
        "💾 Add Application",
        type="primary"
    )


# --------------------------------------------------
# SAVE APPLICATION
# --------------------------------------------------

if submitted:

    if not job_title.strip():
        st.error("❌ Please enter the job title.")

    elif not company.strip():
        st.error("❌ Please enter the company name.")

    else:

        try:
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO job_applications (
                    user_id,
                    job_title,
                    company,
                    location,
                    job_type,
                    application_date,
                    status,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    job_title.strip(),
                    company.strip(),
                    location.strip(),
                    job_type,
                    application_date.isoformat(),
                    status,
                    notes.strip()
                )
            )

            connection.commit()
            connection.close()

            st.success("✅ Application added successfully!")
            st.rerun()

        except Exception as error:
            st.error(f"❌ Could not save application: {error}")


# --------------------------------------------------
# GET APPLICATIONS
# --------------------------------------------------

try:

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            job_title,
            company,
            location,
            job_type,
            application_date,
            status,
            notes
        FROM job_applications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    applications = cursor.fetchall()

    connection.close()

except Exception as error:
    st.error(f"❌ Could not load applications: {error}")
    applications = []


# --------------------------------------------------
# APPLICATION SUMMARY
# --------------------------------------------------

st.subheader("📊 Application Summary")

total = len(applications)

applied_count = sum(
    1 for app in applications
    if app["status"] == "Applied"
)

review_count = sum(
    1 for app in applications
    if app["status"] == "Under Review"
)

interview_count = sum(
    1 for app in applications
    if app["status"] == "Interview"
)

selected_count = sum(
    1 for app in applications
    if app["status"] == "Selected"
)

rejected_count = sum(
    1 for app in applications
    if app["status"] == "Rejected"
)


col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total", total)
col2.metric("Applied", applied_count)
col3.metric("Review", review_count)
col4.metric("Interview", interview_count)
col5.metric("Selected", selected_count)
col6.metric("Rejected", rejected_count)


# --------------------------------------------------
# SHOW APPLICATIONS
# --------------------------------------------------

st.subheader("📄 My Applications")

if not applications:

    st.info(
        "No applications found. Add your first job or internship application above."
    )

else:

    for application in applications:

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(
                    f"### 💼 {application['job_title']}"
                )

                st.write(
                    f"🏢 **Company:** {application['company']}"
                )

                st.write(
                    f"📍 **Location:** {application['location'] or 'Not specified'}"
                )

                st.write(
                    f"🕐 **Job Type:** {application['job_type']}"
                )

                st.write(
                    f"📅 **Applied:** {application['application_date']}"
                )

                if application["notes"]:
                    st.write(
                        f"📝 **Notes:** {application['notes']}"
                    )

            with col2:

                st.write("**Status**")

                new_status = st.selectbox(
                    "Application Status",
                    [
                        "Applied",
                        "Under Review",
                        "Interview",
                        "Selected",
                        "Rejected"
                    ],
                    index=[
                        "Applied",
                        "Under Review",
                        "Interview",
                        "Selected",
                        "Rejected"
                    ].index(application["status"]),
                    key=f"status_{application['id']}",
                    label_visibility="collapsed"
                )

                if st.button(
                    "🔄 Update",
                    key=f"update_{application['id']}"
                ):

                    try:

                        connection = get_connection()
                        cursor = connection.cursor()

                        cursor.execute(
                            """
                            UPDATE job_applications
                            SET status = ?
                            WHERE id = ?
                            AND user_id = ?
                            """,
                            (
                                new_status,
                                application["id"],
                                user_id
                            )
                        )

                        connection.commit()
                        connection.close()

                        st.success("Status updated!")
                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"❌ Could not update status: {error}"
                        )

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{application['id']}"
                ):

                    try:

                        connection = get_connection()
                        cursor = connection.cursor()

                        cursor.execute(
                            """
                            DELETE FROM job_applications
                            WHERE id = ?
                            AND user_id = ?
                            """,
                            (
                                application["id"],
                                user_id
                            )
                        )

                        connection.commit()
                        connection.close()

                        st.success("Application deleted!")
                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"❌ Could not delete application: {error}"
                        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "💡 Keep your application status updated so you can track your placement progress."
)
