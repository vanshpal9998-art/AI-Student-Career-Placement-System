
import streamlit as st
import sys
from pathlib import Path

# ---------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("👨‍🎓 Student Profile")
st.write("Complete your profile information.")


# ---------------------------------------------------------
# CREATE DATABASE TABLES
# ---------------------------------------------------------

create_tables()


# ---------------------------------------------------------
# LOGIN CHECK
# ---------------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login first.")
    st.stop()


user_id = st.session_state.get("user_id")
user_name = st.session_state.get("user_name", "Student")


if user_id is None:
    st.error("❌ User ID not found.")
    st.info("Please logout and login again.")
    st.stop()


# ---------------------------------------------------------
# GET EXISTING PROFILE
# ---------------------------------------------------------

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        phone,
        college,
        degree,
        branch,
        cgpa,
        graduation_year,
        skills,
        projects,
        interest,
        preferred_career
    FROM student_profiles
    WHERE user_id = ?
""", (user_id,))

profile = cursor.fetchone()

connection.close()


# ---------------------------------------------------------
# DEFAULT VALUES
# ---------------------------------------------------------

if profile:

    phone_value = profile["phone"] or ""
    college_value = profile["college"] or ""
    degree_value = profile["degree"] or ""
    branch_value = profile["branch"] or ""
    cgpa_value = profile["cgpa"] if profile["cgpa"] is not None else 0.0
    graduation_year_value = (
        profile["graduation_year"]
        if profile["graduation_year"] is not None
        else 2026
    )
    skills_value = profile["skills"] or ""
    projects_value = profile["projects"] or ""
    interest_value = profile["interest"] or ""
    career_value = profile["preferred_career"] or ""

else:

    phone_value = ""
    college_value = ""
    degree_value = ""
    branch_value = ""
    cgpa_value = 0.0
    graduation_year_value = 2026
    skills_value = ""
    projects_value = ""
    interest_value = ""
    career_value = ""


# ---------------------------------------------------------
# PROFILE FORM
# ---------------------------------------------------------

st.subheader(f"Welcome, {user_name} 👋")

with st.form("student_profile_form"):

    st.markdown("### 👤 Personal Information")

    phone = st.text_input(
        "Phone Number",
        value=phone_value
    )

    college = st.text_input(
        "College / University",
        value=college_value
    )

    st.markdown("### 🎓 Education")

    degree = st.text_input(
        "Degree",
        value=degree_value,
        placeholder="Example: B.Tech"
    )

    branch = st.text_input(
        "Branch / Specialization",
        value=branch_value,
        placeholder="Example: Computer Science"
    )

    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=10.0,
        value=float(cgpa_value),
        step=0.1
    )

    graduation_year = st.number_input(
        "Graduation Year",
        min_value=2000,
        max_value=2100,
        value=int(graduation_year_value),
        step=1
    )

    st.markdown("### 💻 Skills")

    skills = st.text_area(
        "Skills",
        value=skills_value,
        placeholder="Example: Python, SQL, Machine Learning, HTML, CSS"
    )

    projects = st.text_area(
        "Projects",
        value=projects_value,
        placeholder="Describe your academic or personal projects"
    )

    st.markdown("### 🎯 Career Preferences")

    interest = st.text_input(
        "Interests",
        value=interest_value,
        placeholder="Example: Artificial Intelligence, Web Development"
    )

    preferred_career = st.selectbox(
        "Preferred Career",
        [
            "",
            "Python Developer",
            "Data Scientist",
            "Machine Learning Engineer",
            "Web Developer",
            "Full Stack Developer",
            "AI Engineer",
            "Cloud Engineer",
            "DevOps Engineer"
        ],
        index=(
            [
                "",
                "Python Developer",
                "Data Scientist",
                "Machine Learning Engineer",
                "Web Developer",
                "Full Stack Developer",
                "AI Engineer",
                "Cloud Engineer",
                "DevOps Engineer"
            ].index(career_value)
            if career_value in [
                "",
                "Python Developer",
                "Data Scientist",
                "Machine Learning Engineer",
                "Web Developer",
                "Full Stack Developer",
                "AI Engineer",
                "Cloud Engineer",
                "DevOps Engineer"
            ]
            else 0
        )
    )

    submitted = st.form_submit_button(
        "💾 Save Profile",
        type="primary"
    )


# ---------------------------------------------------------
# SAVE PROFILE
# ---------------------------------------------------------

if submitted:

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # Check whether profile already exists
        cursor.execute("""
            SELECT id
            FROM student_profiles
            WHERE user_id = ?
        """, (user_id,))

        existing_profile = cursor.fetchone()

        if existing_profile:

            # UPDATE existing profile
            cursor.execute("""
                UPDATE student_profiles
                SET
                    phone = ?,
                    college = ?,
                    degree = ?,
                    branch = ?,
                    cgpa = ?,
                    graduation_year = ?,
                    skills = ?,
                    projects = ?,
                    interest = ?,
                    preferred_career = ?
                WHERE user_id = ?
            """, (
                phone,
                college,
                degree,
                branch,
                cgpa,
                graduation_year,
                skills,
                projects,
                interest,
                preferred_career,
                user_id
            ))

        else:

            # INSERT new profile
            cursor.execute("""
                INSERT INTO student_profiles (
                    user_id,
                    phone,
                    college,
                    degree,
                    branch,
                    cgpa,
                    graduation_year,
                    skills,
                    projects,
                    interest,
                    preferred_career
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                phone,
                college,
                degree,
                branch,
                cgpa,
                graduation_year,
                skills,
                projects,
                interest,
                preferred_career
            ))

        connection.commit()
        connection.close()

        st.success("✅ Student profile saved successfully!")

    except Exception as error:

        st.error(f"❌ Could not save profile: {error}")

