import streamlit as st
import sys
from pathlib import Path

# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables

create_tables()


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🛠️",
    layout="wide"
)


# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------

if not st.session_state.get("logged_in", False):

    st.warning("⚠️ Please login first.")
    st.stop()


user_id = st.session_state.get("user_id")
role = st.session_state.get("role", "student")


# --------------------------------------------------
# ADMIN CHECK
# --------------------------------------------------

if role != "admin":

    st.error(
        "🚫 Access Denied"
    )

    st.warning(
        "This page is available only to administrators."
    )

    st.stop()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🛠️ Admin Dashboard")

st.write(
    "Monitor students, resumes, applications and placement activity."
)


# --------------------------------------------------
# DATABASE STATISTICS
# --------------------------------------------------

connection = get_connection()
cursor = connection.cursor()


cursor.execute(
    "SELECT COUNT(*) AS total FROM users"
)

total_users = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM users
    WHERE role = 'student'
    """
)

total_students = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM student_profiles
    """
)

total_profiles = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM resumes
    """
)

total_resumes = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM job_applications
    """
)

total_applications = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM job_applications
    WHERE status = 'Interview'
    """
)

total_interviews = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM job_applications
    WHERE status = 'Selected'
    """
)

total_selected = cursor.fetchone()["total"]


connection.close()


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

st.subheader("📊 System Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👥 Total Users",
        total_users
    )

with col2:
    st.metric(
        "🎓 Students",
        total_students
    )

with col3:
    st.metric(
        "👨‍🎓 Profiles",
        total_profiles
    )

with col4:
    st.metric(
        "📄 Resumes",
        total_resumes
    )


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📋 Applications",
        total_applications
    )

with col2:
    st.metric(
        "🎤 Interviews",
        total_interviews
    )

with col3:
    st.metric(
        "🏆 Selected",
        total_selected
    )


# --------------------------------------------------
# STUDENT LIST
# --------------------------------------------------

st.divider()

st.subheader("👥 Registered Students")

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        users.id,
        users.name,
        users.email,
        users.role,
        student_profiles.college,
        student_profiles.degree,
        student_profiles.branch,
        student_profiles.cgpa,
        student_profiles.preferred_career
    FROM users
    LEFT JOIN student_profiles
    ON users.id = student_profiles.user_id
    ORDER BY users.id DESC
    """
)

students = cursor.fetchall()

connection.close()


if not students:

    st.info("No users found.")

else:

    for student in students:

        with st.container(border=True):

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:

                st.markdown(
                    f"### 👤 {student['name']}"
                )

                st.write(
                    f"📧 {student['email']}"
                )

                st.write(
                    f"🔑 Role: {student['role']}"
                )

            with col2:

                st.write(
                    f"🏫 College: "
                    f"{student['college'] or 'Not added'}"
                )

                st.write(
                    f"🎓 Degree: "
                    f"{student['degree'] or 'Not added'}"
                )

                st.write(
                    f"💻 Branch: "
                    f"{student['branch'] or 'Not added'}"
                )

            with col3:

                st.write(
                    f"📈 CGPA: "
                    f"{student['cgpa'] if student['cgpa'] is not None else 'N/A'}"
                )

                st.write(
                    f"🎯 Career: "
                    f"{student['preferred_career'] or 'Not selected'}"
                )


# --------------------------------------------------
# APPLICATION STATUS
# --------------------------------------------------

st.divider()

st.subheader("📋 Application Status")

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        status,
        COUNT(*) AS total
    FROM job_applications
    GROUP BY status
    ORDER BY total DESC
    """
)

application_status = cursor.fetchall()

connection.close()


if application_status:

    for item in application_status:

        st.write(
            f"**{item['status']}:** {item['total']}"
        )

else:

    st.info("No applications available.")


# --------------------------------------------------
# ADMIN FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "🛠️ Admin Dashboard | AI Student Career & Placement System"
)
