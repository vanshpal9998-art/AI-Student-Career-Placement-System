
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
# PAGE
# ---------------------------------------------------------

st.title("🎯 Skill Gap Analysis")
st.write(
    "Compare your current skills with the skills required "
    "for your preferred career."
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

create_tables()


# ---------------------------------------------------------
# LOGIN CHECK
# ---------------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login first.")
    st.stop()

user_id = st.session_state.get("user_id")

if user_id is None:
    st.error("❌ User ID not found.")
    st.info("Please logout and login again.")
    st.stop()


# ---------------------------------------------------------
# GET STUDENT PROFILE
# ---------------------------------------------------------

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        skills,
        preferred_career
    FROM student_profiles
    WHERE user_id = ?
""", (user_id,))

profile = cursor.fetchone()

connection.close()


# ---------------------------------------------------------
# PROFILE CHECK
# ---------------------------------------------------------

if profile is None:

    st.warning("⚠️ Student profile not found.")

    st.info(
        "Please open Student Profile, complete your "
        "information, and save it first."
    )

    st.stop()


# ---------------------------------------------------------
# CURRENT SKILLS
# ---------------------------------------------------------

current_skills_text = profile["skills"] or ""

preferred_career = profile["preferred_career"] or ""


# ---------------------------------------------------------
# CAREER SKILL REQUIREMENTS
# ---------------------------------------------------------

CAREER_SKILLS = {

    "Python Developer": [
        "python",
        "sql",
        "git",
        "github",
        "django",
        "flask"
    ],

    "Data Scientist": [
        "python",
        "sql",
        "pandas",
        "numpy",
        "data science",
        "machine learning",
        "statistics"
    ],

    "Machine Learning Engineer": [
        "python",
        "numpy",
        "pandas",
        "machine learning",
        "tensorflow",
        "pytorch",
        "sql"
    ],

    "Web Developer": [
        "html",
        "css",
        "javascript",
        "git",
        "github"
    ],

    "Full Stack Developer": [
        "html",
        "css",
        "javascript",
        "react",
        "python",
        "django",
        "sql",
        "git"
    ],

    "AI Engineer": [
        "python",
        "machine learning",
        "artificial intelligence",
        "tensorflow",
        "pytorch",
        "numpy",
        "pandas"
    ],

    "Cloud Engineer": [
        "aws",
        "azure",
        "docker",
        "linux",
        "git",
        "python"
    ],

    "DevOps Engineer": [
        "git",
        "docker",
        "linux",
        "aws",
        "azure",
        "python"
    ]
}


# ---------------------------------------------------------
# DISPLAY PROFILE INFORMATION
# ---------------------------------------------------------

st.subheader("👤 Your Career Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Current Skills:**")

    if current_skills_text:
        st.write(current_skills_text)
    else:
        st.info("No skills added to your profile.")

with col2:
    st.write("**Preferred Career:**")

    if preferred_career:
        st.write(preferred_career)
    else:
        st.info("No preferred career selected.")


# ---------------------------------------------------------
# CAREER SELECTION
# ---------------------------------------------------------

available_careers = list(CAREER_SKILLS.keys())

default_index = 0

if preferred_career in available_careers:
    default_index = available_careers.index(preferred_career)

career = st.selectbox(
    "Select Career for Analysis",
    available_careers,
    index=default_index
)


# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------

if st.button(
    "🔍 Analyze Skill Gap",
    type="primary"
):

    # Convert student's skills into a list
    current_skills = [
        skill.strip().lower()
        for skill in current_skills_text.split(",")
        if skill.strip()
    ]

    required_skills = CAREER_SKILLS[career]

    # -----------------------------------------------------
    # MATCH SKILLS
    # -----------------------------------------------------

    matched_skills = []

    missing_skills = []

    for required_skill in required_skills:

        if required_skill.lower() in current_skills:

            matched_skills.append(
                required_skill
            )

        else:

            missing_skills.append(
                required_skill
            )

    # -----------------------------------------------------
    # MATCH PERCENTAGE
    # -----------------------------------------------------

    total_required = len(required_skills)

    if total_required > 0:

        match_percentage = (
            len(matched_skills)
            / total_required
        ) * 100

    else:

        match_percentage = 0


    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        f"📊 Skill Gap for {career}"
    )

    st.metric(
        "Skill Match",
        f"{match_percentage:.1f}%"
    )

    st.progress(
        int(match_percentage)
    )


    # -----------------------------------------------------
    # TWO COLUMNS
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Matched Skills")

        if matched_skills:

            for skill in matched_skills:
                st.success(skill.title())

        else:

            st.info(
                "No required skills matched yet."
            )


    with col2:

        st.subheader("📚 Skills to Learn")

        if missing_skills:

            for skill in missing_skills:
                st.warning(skill.title())

        else:

            st.success(
                "🎉 You have all required skills!"
            )


    # -----------------------------------------------------
    # SAVE ANALYSIS
    # -----------------------------------------------------

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO skill_gap_analysis (
                user_id,
                career,
                matched_skills,
                missing_skills,
                match_percentage
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            career,
            ", ".join(matched_skills),
            ", ".join(missing_skills),
            match_percentage
        ))

        connection.commit()
        connection.close()

        st.success(
            "✅ Skill gap analysis saved successfully!"
        )

    except Exception as error:

        st.error(
            f"❌ Could not save analysis: {error}"
        )


# ---------------------------------------------------------
# LEARNING RECOMMENDATION
# ---------------------------------------------------------

st.divider()

st.subheader("💡 Learning Recommendation")

if preferred_career:

    if preferred_career == "Python Developer":

        st.write("""
        Focus on Python, SQL, Git, Django and Flask.
        """)

    elif preferred_career == "Data Scientist":

        st.write("""
        Focus on Python, Pandas, NumPy, SQL,
        Statistics and Machine Learning.
        """)

    elif preferred_career == "Machine Learning Engineer":

        st.write("""
        Focus on Python, NumPy, Pandas,
        Machine Learning, TensorFlow and PyTorch.
        """)

    elif preferred_career == "Web Developer":

        st.write("""
        Focus on HTML, CSS, JavaScript, Git
        and modern web development.
        """)

    elif preferred_career == "Full Stack Developer":

        st.write("""
        Focus on HTML, CSS, JavaScript, React,
        Python, Django and SQL.
        """)

    elif preferred_career == "AI Engineer":

        st.write("""
        Focus on Python, Machine Learning,
        Artificial Intelligence, TensorFlow and PyTorch.
        """)

    elif preferred_career == "Cloud Engineer":

        st.write("""
        Focus on AWS, Azure, Docker, Linux,
        Git and Python.
        """)

    elif preferred_career == "DevOps Engineer":

        st.write("""
        Focus on Git, Docker, Linux, AWS,
        Azure and Python.
        """)

else:

    st.info(
        "Complete your Student Profile to get "
        "personalized learning recommendations."
    )
