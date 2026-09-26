
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

st.title("🚀 Career Recommendation")
st.write(
    "Get career recommendations based on your "
    "skills, interests and preferred career."
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
# GET PROFILE
# ---------------------------------------------------------

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        skills,
        interest,
        preferred_career,
        cgpa
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
        "information and save it first."
    )

    st.stop()


# ---------------------------------------------------------
# PROFILE DATA
# ---------------------------------------------------------

skills_text = profile["skills"] or ""
interest_text = profile["interest"] or ""
preferred_career = profile["preferred_career"] or ""
cgpa = profile["cgpa"] or 0


current_skills = [
    skill.strip().lower()
    for skill in skills_text.split(",")
    if skill.strip()
]

interests = [
    interest.strip().lower()
    for interest in interest_text.split(",")
    if interest.strip()
]


# ---------------------------------------------------------
# CAREER DATA
# ---------------------------------------------------------

CAREERS = {

    "Python Developer": {

        "skills": [
            "python",
            "sql",
            "git",
            "github",
            "django",
            "flask"
        ],

        "interests": [
            "python",
            "software development",
            "backend",
            "programming"
        ],

        "description":
            "Develop applications and backend systems using Python."
    },


    "Data Scientist": {

        "skills": [
            "python",
            "sql",
            "pandas",
            "numpy",
            "data science",
            "machine learning",
            "statistics"
        ],

        "interests": [
            "data science",
            "data analysis",
            "statistics",
            "machine learning"
        ],

        "description":
            "Analyze data and build data-driven solutions."
    },


    "Machine Learning Engineer": {

        "skills": [
            "python",
            "numpy",
            "pandas",
            "machine learning",
            "tensorflow",
            "pytorch",
            "sql"
        ],

        "interests": [
            "machine learning",
            "artificial intelligence",
            "deep learning",
            "data science"
        ],

        "description":
            "Build, train and deploy machine learning models."
    },


    "Web Developer": {

        "skills": [
            "html",
            "css",
            "javascript",
            "git",
            "github"
        ],

        "interests": [
            "web development",
            "frontend",
            "website",
            "javascript"
        ],

        "description":
            "Build websites and interactive web applications."
    },


    "Full Stack Developer": {

        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "python",
            "django",
            "sql",
            "git"
        ],

        "interests": [
            "web development",
            "full stack",
            "software development",
            "programming"
        ],

        "description":
            "Develop complete frontend and backend web applications."
    },


    "AI Engineer": {

        "skills": [
            "python",
            "machine learning",
            "artificial intelligence",
            "tensorflow",
            "pytorch",
            "numpy",
            "pandas"
        ],

        "interests": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "ai"
        ],

        "description":
            "Develop AI systems and intelligent applications."
    },


    "Cloud Engineer": {

        "skills": [
            "aws",
            "azure",
            "docker",
            "linux",
            "git",
            "python"
        ],

        "interests": [
            "cloud computing",
            "aws",
            "azure",
            "cloud"
        ],

        "description":
            "Design and manage cloud infrastructure and services."
    },


    "DevOps Engineer": {

        "skills": [
            "git",
            "docker",
            "linux",
            "aws",
            "azure",
            "python"
        ],

        "interests": [
            "devops",
            "cloud",
            "automation",
            "deployment"
        ],

        "description":
            "Automate software development, deployment and infrastructure."
    }
}


# ---------------------------------------------------------
# PROFILE SUMMARY
# ---------------------------------------------------------

st.subheader("👤 Your Profile")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Skills",
        len(current_skills)
    )

with col2:

    st.metric(
        "Interests",
        len(interests)
    )

with col3:

    st.metric(
        "CGPA",
        f"{cgpa:.1f}"
    )


if preferred_career:

    st.info(
        f"🎯 Preferred Career: **{preferred_career}**"
    )


# ---------------------------------------------------------
# CALCULATE RECOMMENDATIONS
# ---------------------------------------------------------

recommendations = []


for career, data in CAREERS.items():

    required_skills = data["skills"]
    career_interests = data["interests"]


    # -----------------------------------------------------
    # SKILL MATCH
    # -----------------------------------------------------

    matched_skills = []

    for skill in required_skills:

        if skill.lower() in current_skills:

            matched_skills.append(skill)


    if required_skills:

        skill_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 70

    else:

        skill_score = 0


    # -----------------------------------------------------
    # INTEREST MATCH
    # -----------------------------------------------------

    matched_interests = []

    for interest in career_interests:

        if interest.lower() in interests:

            matched_interests.append(
                interest
            )


    if career_interests:

        interest_score = (
            len(matched_interests)
            / len(career_interests)
        ) * 20

    else:

        interest_score = 0


    # -----------------------------------------------------
    # PREFERRED CAREER MATCH
    # -----------------------------------------------------

    preference_score = 0

    if preferred_career == career:

        preference_score = 10


    # -----------------------------------------------------
    # TOTAL SCORE
    # -----------------------------------------------------

    total_score = (
        skill_score
        + interest_score
        + preference_score
    )


    recommendations.append({

        "career": career,

        "score": total_score,

        "matched_skills": matched_skills,

        "matched_interests": matched_interests,

        "description": data["description"]

    })


# ---------------------------------------------------------
# SORT RECOMMENDATIONS
# ---------------------------------------------------------

recommendations.sort(
    key=lambda item: item["score"],
    reverse=True
)


# ---------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------

st.divider()

st.subheader("🎯 Career Recommendations")

for index, recommendation in enumerate(
    recommendations[:5],
    start=1
):

    career = recommendation["career"]
    score = recommendation["score"]
    matched_skills = recommendation["matched_skills"]
    matched_interests = recommendation["matched_interests"]
    description = recommendation["description"]


    with st.container(border=True):

        st.markdown(
            f"### {index}. {career}"
        )

        st.progress(
            int(min(score, 100))
        )

        st.write(
            f"**Match Score:** {score:.1f}%"
        )

        st.write(
            f"**Description:** {description}"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.write(
                "**Matched Skills:**"
            )

            if matched_skills:

                st.write(
                    ", ".join(
                        skill.title()
                        for skill in matched_skills
                    )
                )

            else:

                st.write(
                    "No matching skills yet."
                )


        with col2:

            st.write(
                "**Matched Interests:**"
            )

            if matched_interests:

                st.write(
                    ", ".join(
                        interest.title()
                        for interest in matched_interests
                    )
                )

            else:

                st.write(
                    "No matching interests yet."
                )


        # -------------------------------------------------
        # SAVE RECOMMENDATION
        # -------------------------------------------------

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO career_recommendations (
                    user_id,
                    career,
                    match_score,
                    matched_skills,
                    matched_interests
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                career,
                score,
                ", ".join(matched_skills),
                ", ".join(matched_interests)
            ))

            connection.commit()
            connection.close()

        except Exception:
            pass


# ---------------------------------------------------------
# NOTE
# ---------------------------------------------------------

st.divider()

st.info(
    "ℹ️ These recommendations use a rule-based scoring "
    "system based on your profile data. They are not "
    "predictions of your future career outcome."
)
