
import streamlit as st
import sys
from pathlib import Path

# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables


# Create all database tables
create_tables()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Student Career & Placement System",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------

if not st.session_state.get("logged_in", False):

    st.title("🎓 AI Student Career & Placement System")

    st.info("Please login to access your dashboard.")

    if st.button("🔐 Go to Login", type="primary"):
        st.switch_page("pages/login.py")

    st.stop()


# --------------------------------------------------
# SESSION DATA
# --------------------------------------------------

user_id = st.session_state.get("user_id")
user_name = st.session_state.get("user_name", "Student")


if user_id is None:

    st.error("❌ User ID not found.")

    if st.button("Go to Login"):
        st.switch_page("pages/login.py")

    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🎓 Career System")

st.sidebar.success(
    f"Welcome, {user_name}"
)

st.sidebar.divider()

if st.sidebar.button(
    "👨‍🎓 Student Profile",
    use_container_width=True
):
    st.switch_page("pages/student_profile.py")


if st.sidebar.button(
    "📄 Resume Analysis",
    use_container_width=True
):
    st.switch_page("pages/resume_analysis.py")


if st.sidebar.button(
    "📊 Skill Gap Analysis",
    use_container_width=True
):
    st.switch_page("pages/skill_gap.py")


if st.sidebar.button(
    "🎯 Career Recommendation",
    use_container_width=True
):
    st.switch_page("pages/career_recommendation.py")


if st.sidebar.button(
    "💼 Job Recommendation",
    use_container_width=True
):
    st.switch_page("pages/job_recommendation.py")


if st.sidebar.button(
    "📋 Application Tracker",
    use_container_width=True
):
    st.switch_page("pages/application_tracker.py")


st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    for key in [
        "logged_in",
        "user_id",
        "user_name",
        "role"
    ]:
        st.session_state.pop(key, None)

    st.switch_page("pages/login.py")


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("🎓 AI Student Career & Placement System")

st.subheader(
    f"Welcome back, {user_name}! 👋"
)

st.write(
    "Manage your profile, resume, skills, career recommendations, "
    "job opportunities and applications from one place."
)


# --------------------------------------------------
# GET STUDENT PROFILE
# --------------------------------------------------

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        college,
        degree,
        branch,
        cgpa,
        graduation_year,
        skills,
        interest,
        preferred_career
    FROM student_profiles
    WHERE user_id = ?
    """,
    (user_id,)
)

profile = cursor.fetchone()


# --------------------------------------------------
# GET STATISTICS
# --------------------------------------------------

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM resumes
    WHERE user_id = ?
    """,
    (user_id,)
)

resume_count = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM job_applications
    WHERE user_id = ?
    """,
    (user_id,)
)

application_count = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM job_applications
    WHERE user_id = ?
    AND status = 'Interview'
    """,
    (user_id,)
)

interview_count = cursor.fetchone()["total"]


cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM job_applications
    WHERE user_id = ?
    AND status = 'Selected'
    """,
    (user_id,)
)

selected_count = cursor.fetchone()["total"]


connection.close()


# --------------------------------------------------
# PROFILE COMPLETION
# --------------------------------------------------

profile_completion = 0

if profile:

    fields = [
        profile["college"],
        profile["degree"],
        profile["branch"],
        profile["cgpa"],
        profile["graduation_year"],
        profile["skills"],
        profile["interest"],
        profile["preferred_career"]
    ]

    completed_fields = sum(
        1
        for field in fields
        if field is not None and str(field).strip() != ""
    )

    profile_completion = round(
        (completed_fields / len(fields)) * 100
    )


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

st.divider()

st.subheader("📊 Your Progress")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📄 Resumes",
        resume_count
    )

with col2:
    st.metric(
        "📋 Applications",
        application_count
    )

with col3:
    st.metric(
        "🎤 Interviews",
        interview_count
    )

with col4:
    st.metric(
        "🏆 Selected",
        selected_count
    )


# --------------------------------------------------
# PROFILE SECTION
# --------------------------------------------------

st.divider()

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("👨‍🎓 Student Profile")

    if profile:

        st.write(
            f"**College:** "
            f"{profile['college'] or 'Not added'}"
        )

        st.write(
            f"**Degree:** "
            f"{profile['degree'] or 'Not added'}"
        )

        st.write(
            f"**Branch:** "
            f"{profile['branch'] or 'Not added'}"
        )

        st.write(
            f"**CGPA:** "
            f"{profile['cgpa'] if profile['cgpa'] is not None else 'Not added'}"
        )

        st.write(
            f"**Graduation Year:** "
            f"{profile['graduation_year'] or 'Not added'}"
        )

        st.write(
            f"**Preferred Career:** "
            f"{profile['preferred_career'] or 'Not selected'}"
        )

    else:

        st.warning(
            "⚠️ Your student profile has not been completed yet."
        )

        if st.button(
            "👨‍🎓 Complete Profile",
            type="primary"
        ):
            st.switch_page(
                "pages/student_profile.py"
            )


with col2:

    st.subheader("📈 Profile Completion")

    st.progress(
        profile_completion / 100
    )

    st.write(
        f"**{profile_completion}% Complete**"
    )

    if profile_completion < 100:

        st.info(
            "Complete your profile to get better "
            "career and job recommendations."
        )


# --------------------------------------------------
# QUICK ACTIONS
# --------------------------------------------------

st.divider()

st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "📄 Analyze Resume",
        use_container_width=True
    ):
        st.switch_page(
            "pages/resume_analysis.py"
        )

    if st.button(
        "📊 Check Skill Gap",
        use_container_width=True
    ):
        st.switch_page(
            "pages/skill_gap.py"
        )


with col2:

    if st.button(
        "🎯 Career Recommendation",
        use_container_width=True
    ):
        st.switch_page(
            "pages/career_recommendation.py"
        )

    if st.button(
        "💼 Find Jobs",
        use_container_width=True
    ):
        st.switch_page(
            "pages/job_recommendation.py"
        )


with col3:

    if st.button(
        "📋 Track Applications",
        use_container_width=True
    ):
        st.switch_page(
            "pages/application_tracker.py"
        )

    if st.button(
        "👨‍🎓 Edit Profile",
        use_container_width=True
    ):
        st.switch_page(
            "pages/student_profile.py"
        )


# --------------------------------------------------
# PROJECT WORKFLOW
# --------------------------------------------------

st.divider()

st.subheader("🚀 Career Preparation Workflow")

steps = [
    ("1️⃣", "Complete Profile"),
    ("2️⃣", "Upload Resume"),
    ("3️⃣", "Analyze Skills"),
    ("4️⃣", "Find Career"),
    ("5️⃣", "Find Jobs"),
    ("6️⃣", "Track Applications")
]

cols = st.columns(6)

for column, (number, text) in zip(cols, steps):

    with column:

        st.markdown(
            f"### {number}"
        )

        st.caption(text)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "🎓 AI Student Career & Placement System | "
    "College Project"
)
