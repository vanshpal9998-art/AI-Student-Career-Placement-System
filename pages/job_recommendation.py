
import streamlit as st
import sys
from pathlib import Path
from datetime import date

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables


# Create tables
create_tables()

st.title("💼 Job Recommendations")
st.write("Find jobs that match your skills and preferred career.")


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
# GET STUDENT PROFILE
# --------------------------------------------------

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT skills, preferred_career
    FROM student_profiles
    WHERE user_id = ?
    """,
    (user_id,)
)

profile = cursor.fetchone()
connection.close()


if profile is None:
    st.warning("⚠️ Please complete your Student Profile first.")
    st.stop()


student_skills_text = profile["skills"] or ""
preferred_career = profile["preferred_career"] or ""

student_skills = {
    skill.strip().lower()
    for skill in student_skills_text.split(",")
    if skill.strip()
}


# --------------------------------------------------
# SAMPLE JOB DATA
# --------------------------------------------------

jobs = [
    {
        "title": "Python Developer",
        "company": "TechSoft Solutions",
        "location": "Noida",
        "type": "Full Time",
        "career": "Python Developer",
        "skills": ["python", "sql", "django", "git"]
    },
    {
        "title": "Junior Python Developer",
        "company": "CodeWorks India",
        "location": "Delhi",
        "type": "Full Time",
        "career": "Python Developer",
        "skills": ["python", "sql", "flask", "git"]
    },
    {
        "title": "Data Science Intern",
        "company": "DataLabs",
        "location": "Bangalore",
        "type": "Internship",
        "career": "Data Scientist",
        "skills": ["python", "pandas", "numpy", "sql"]
    },
    {
        "title": "Data Scientist",
        "company": "AnalyticsHub",
        "location": "Hyderabad",
        "type": "Full Time",
        "career": "Data Scientist",
        "skills": ["python", "pandas", "numpy", "machine learning", "sql"]
    },
    {
        "title": "Machine Learning Intern",
        "company": "AI Labs",
        "location": "Bangalore",
        "type": "Internship",
        "career": "Machine Learning Engineer",
        "skills": ["python", "machine learning", "numpy", "pandas"]
    },
    {
        "title": "Machine Learning Engineer",
        "company": "IntelliTech",
        "location": "Pune",
        "type": "Full Time",
        "career": "Machine Learning Engineer",
        "skills": ["python", "machine learning", "tensorflow", "pytorch"]
    },
    {
        "title": "Frontend Developer",
        "company": "WebWorks",
        "location": "Noida",
        "type": "Full Time",
        "career": "Web Developer",
        "skills": ["html", "css", "javascript", "git"]
    },
    {
        "title": "React Developer",
        "company": "Digital India Tech",
        "location": "Delhi",
        "type": "Full Time",
        "career": "Web Developer",
        "skills": ["html", "css", "javascript", "react"]
    },
    {
        "title": "Full Stack Developer",
        "company": "SoftwareWorks",
        "location": "Gurgaon",
        "type": "Full Time",
        "career": "Full Stack Developer",
        "skills": ["html", "css", "javascript", "react", "python", "sql"]
    },
    {
        "title": "AI Engineer",
        "company": "FutureAI",
        "location": "Bangalore",
        "type": "Full Time",
        "career": "AI Engineer",
        "skills": ["python", "machine learning", "artificial intelligence", "tensorflow", "pytorch"]
    },
    {
        "title": "Cloud Engineer",
        "company": "CloudTech",
        "location": "Hyderabad",
        "type": "Full Time",
        "career": "Cloud Engineer",
        "skills": ["aws", "docker", "linux", "python"]
    },
    {
        "title": "DevOps Intern",
        "company": "DevOpsWorks",
        "location": "Pune",
        "type": "Internship",
        "career": "DevOps Engineer",
        "skills": ["git", "docker", "linux", "aws"]
    }
]


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.subheader("🔎 Filter Jobs")

locations = sorted(
    list(set(job["location"] for job in jobs))
)

job_types = sorted(
    list(set(job["type"] for job in jobs))
)

careers = sorted(
    list(set(job["career"] for job in jobs))
)

col1, col2, col3 = st.columns(3)

with col1:
    selected_location = st.selectbox(
        "Location",
        ["All"] + locations
    )

with col2:
    selected_type = st.selectbox(
        "Job Type",
        ["All"] + job_types
    )

with col3:
    selected_career = st.selectbox(
        "Career",
        ["All"] + careers
    )


# --------------------------------------------------
# CALCULATE JOB MATCH
# --------------------------------------------------

recommended_jobs = []

for job in jobs:

    if (
        selected_location != "All"
        and job["location"] != selected_location
    ):
        continue

    if (
        selected_type != "All"
        and job["type"] != selected_type
    ):
        continue

    if (
        selected_career != "All"
        and job["career"] != selected_career
    ):
        continue

    required_skills = set(job["skills"])

    matched_skills = (
        student_skills.intersection(required_skills)
    )

    missing_skills = (
        required_skills - student_skills
    )

    if required_skills:
        skill_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 100
    else:
        skill_score = 0

    career_bonus = 0

    if preferred_career:
        if job["career"].lower() == preferred_career.lower():
            career_bonus = 10

    final_score = min(
        round(skill_score + career_bonus, 2),
        100
    )

    recommended_jobs.append({
        "job": job,
        "score": final_score,
        "matched": sorted(matched_skills),
        "missing": sorted(missing_skills)
    })


# Highest matching jobs first
recommended_jobs.sort(
    key=lambda x: x["score"],
    reverse=True
)


# --------------------------------------------------
# SHOW RESULTS
# --------------------------------------------------

st.divider()

st.subheader(
    f"🎯 Recommended Jobs ({len(recommended_jobs)})"
)

if not recommended_jobs:

    st.info("No jobs match your selected filters.")

else:

    for index, recommendation in enumerate(recommended_jobs):

        job = recommendation["job"]
        score = recommendation["score"]
        matched = recommendation["matched"]
        missing = recommendation["missing"]

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:

                st.markdown(
                    f"### 💼 {job['title']}"
                )

                st.write(
                    f"🏢 **Company:** {job['company']}"
                )

                st.write(
                    f"📍 **Location:** {job['location']}"
                )

                st.write(
                    f"🕐 **Type:** {job['type']}"
                )

                st.write(
                    f"🎯 **Career:** {job['career']}"
                )

                if matched:
                    st.write(
                        "✅ **Matched Skills:** "
                        + ", ".join(matched)
                    )
                else:
                    st.write(
                        "✅ **Matched Skills:** None"
                    )

                if missing:
                    st.write(
                        "📚 **Missing Skills:** "
                        + ", ".join(missing)
                    )

            with col2:

                st.metric(
                    "Match Score",
                    f"{score}%"
                )

                if st.button(
                    "📝 Track Application",
                    key=f"track_{index}"
                ):

                    try:

                        connection = get_connection()
                        cursor = connection.cursor()

                        # Check if already added
                        cursor.execute(
                            """
                            SELECT id
                            FROM job_applications
                            WHERE user_id = ?
                            AND job_title = ?
                            AND company = ?
                            """,
                            (
                                user_id,
                                job["title"],
                                job["company"]
                            )
                        )

                        existing = cursor.fetchone()

                        if existing:

                            connection.close()

                            st.warning(
                                "⚠️ This job is already in your Application Tracker."
                            )

                        else:

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
                                    job["title"],
                                    job["company"],
                                    job["location"],
                                    job["type"],
                                    date.today().isoformat(),
                                    "Applied",
                                    "Added from Job Recommendations"
                                )
                            )

                            connection.commit()
                            connection.close()

                            st.success(
                                "✅ Added to Application Tracker!"
                            )

                    except Exception as error:

                        st.error(
                            f"❌ Could not track application: {error}"
                        )


# --------------------------------------------------
# INFORMATION
# --------------------------------------------------

st.divider()

st.info(
    "💡 These are sample job listings for the college project. "
    "They are not live job vacancies."
)
