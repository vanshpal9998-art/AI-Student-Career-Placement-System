
import streamlit as st
import sys
from pathlib import Path
import random

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables

create_tables()

st.set_page_config(
    page_title="Interview Preparation",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Interview Preparation")
st.write("Practice interview questions based on your preferred career.")


# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please login first.")
    st.stop()

user_id = st.session_state.get("user_id")

if user_id is None:
    st.error("❌ User ID not found.")
    st.stop()


# --------------------------------------------------
# GET PROFILE
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

skills_text = profile["skills"] or ""
preferred_career = profile["preferred_career"] or "General"


# --------------------------------------------------
# INTERVIEW QUESTION BANK
# --------------------------------------------------

questions = {

    "Python Developer": [
        "What is the difference between a list and a tuple in Python?",
        "What are Python decorators?",
        "What is exception handling in Python?",
        "What is the difference between == and is?",
        "What are Python modules and packages?",
        "Explain object-oriented programming in Python.",
        "What is a virtual environment?"
    ],

    "Data Scientist": [
        "What is the difference between supervised and unsupervised learning?",
        "What is data preprocessing?",
        "What is overfitting?",
        "What is cross-validation?",
        "What is the difference between classification and regression?",
        "What is feature engineering?",
        "Explain precision and recall."
    ],

    "Machine Learning Engineer": [
        "What is machine learning?",
        "What is overfitting and how can you prevent it?",
        "What is gradient descent?",
        "What is the difference between training and testing data?",
        "What is a confusion matrix?",
        "What is feature scaling?",
        "Explain the bias-variance tradeoff."
    ],

    "Web Developer": [
        "What is the difference between HTML and CSS?",
        "What is JavaScript?",
        "What is responsive web design?",
        "What is the DOM?",
        "What is an API?",
        "What is the difference between frontend and backend?",
        "What is HTTP?"
    ],

    "Full Stack Developer": [
        "What is the difference between frontend and backend?",
        "What is REST API?",
        "What is a database?",
        "What is authentication?",
        "What is the difference between SQL and NoSQL?",
        "What is MVC architecture?",
        "How does a web application communicate with a server?"
    ],

    "AI Engineer": [
        "What is artificial intelligence?",
        "What is the difference between AI and machine learning?",
        "What is deep learning?",
        "What are neural networks?",
        "What is natural language processing?",
        "What is computer vision?",
        "What is a large language model?"
    ],

    "Cloud Engineer": [
        "What is cloud computing?",
        "What is the difference between IaaS, PaaS and SaaS?",
        "What is AWS?",
        "What is virtualization?",
        "What is cloud storage?",
        "What is a container?",
        "What is Docker?"
    ],

    "DevOps Engineer": [
        "What is DevOps?",
        "What is CI/CD?",
        "What is Docker?",
        "What is Kubernetes?",
        "What is version control?",
        "What is Git?",
        "What is infrastructure as code?"
    ],

    "General": [
        "Tell me about yourself.",
        "What are your strengths?",
        "What are your weaknesses?",
        "Why should we hire you?",
        "Where do you see yourself in five years?",
        "Tell me about your college project.",
        "Why are you interested in this career?"
    ]
}


career_questions = questions.get(
    preferred_career,
    questions["General"]
)


# --------------------------------------------------
# INTERVIEW SETTINGS
# --------------------------------------------------

st.subheader("🎯 Interview Settings")

col1, col2 = st.columns(2)

with col1:

    question_count = st.selectbox(
        "Number of Questions",
        [5, 10, 15]
    )

with col2:

    interview_type = st.selectbox(
        "Interview Type",
        [
            "Technical",
            "HR",
            "Mixed"
        ]
    )


# --------------------------------------------------
# START INTERVIEW
# --------------------------------------------------

if "interview_questions" not in st.session_state:
    st.session_state["interview_questions"] = []

if "interview_answers" not in st.session_state:
    st.session_state["interview_answers"] = {}

if "interview_started" not in st.session_state:
    st.session_state["interview_started"] = False


if st.button(
    "🚀 Start Interview",
    type="primary"
):

    count = min(
        question_count,
        len(career_questions)
    )

    selected_questions = random.sample(
        career_questions,
        count
    )

    st.session_state["interview_questions"] = selected_questions
    st.session_state["interview_answers"] = {}
    st.session_state["interview_started"] = True

    st.rerun()


# --------------------------------------------------
# INTERVIEW QUESTIONS
# --------------------------------------------------

if st.session_state["interview_started"]:

    st.divider()

    st.subheader(
        f"📝 {preferred_career} Interview"
    )

    st.info(
        f"Interview Type: {interview_type}"
    )

    questions_list = st.session_state["interview_questions"]

    for index, question in enumerate(questions_list):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(question)

        answer = st.text_area(
            "Your Answer",
            key=f"answer_{index}",
            placeholder="Write your answer here..."
        )

        st.session_state["interview_answers"][index] = answer

        st.divider()

    if st.button(
        "📊 Finish Interview",
        type="primary"
    ):

        answered = sum(
            1
            for answer in st.session_state["interview_answers"].values()
            if answer.strip()
        )

        total_questions = len(questions_list)

        completion = round(
            (answered / total_questions) * 100
        )

        st.success(
            f"Interview completed! "
            f"You answered {answered}/{total_questions} questions."
        )

        st.metric(
            "Interview Completion",
            f"{completion}%"
        )

        if completion == 100:

            st.success(
                "🎉 Excellent! You answered every question."
            )

        elif completion >= 60:

            st.info(
                "👍 Good attempt. Keep practicing."
            )

        else:

            st.warning(
                "📚 Try answering more questions for better preparation."
            )


# --------------------------------------------------
# TIPS
# --------------------------------------------------

st.divider()

st.subheader("💡 Interview Tips")

tips = [
    "Research the company before the interview.",
    "Understand your resume and projects.",
    "Practice explaining technical concepts clearly.",
    "Use real examples when answering questions.",
    "Keep your answers concise and structured.",
    "Prepare questions to ask the interviewer.",
    "Stay confident and communicate clearly."
]

for tip in tips:
    st.write(f"✅ {tip}")
