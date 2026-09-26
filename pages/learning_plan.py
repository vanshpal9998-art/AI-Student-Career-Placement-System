import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables

create_tables()

st.set_page_config(
    page_title="Learning Plan",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Personalized Learning Plan")
st.write(
    "Build a learning roadmap based on your preferred career and skills."
)


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
preferred_career = profile["preferred_career"] or ""


# --------------------------------------------------
# LEARNING ROADMAP
# --------------------------------------------------

learning_data = {

    "Python Developer": {
        "Beginner": [
            "Python Basics",
            "Variables and Data Types",
            "Conditions and Loops",
            "Functions",
            "Lists, Tuples and Dictionaries",
            "Object-Oriented Programming"
        ],
        "Intermediate": [
            "File Handling",
            "Exception Handling",
            "Modules and Packages",
            "Virtual Environments",
            "Git and GitHub",
            "SQL"
        ],
        "Advanced": [
            "Django",
            "Flask",
            "REST APIs",
            "Database Integration",
            "Testing",
            "Deployment"
        ]
    },

    "Data Scientist": {
        "Beginner": [
            "Python",
            "Statistics Basics",
            "SQL",
            "Data Cleaning",
            "Pandas",
            "NumPy"
        ],
        "Intermediate": [
            "Data Visualization",
            "Matplotlib",
            "Exploratory Data Analysis",
            "Probability",
            "Machine Learning",
            "Feature Engineering"
        ],
        "Advanced": [
            "Advanced Machine Learning",
            "Model Evaluation",
            "Deep Learning",
            "Time Series",
            "NLP",
            "Machine Learning Projects"
        ]
    },

    "Machine Learning Engineer": {
        "Beginner": [
            "Python",
            "NumPy",
            "Pandas",
            "Statistics",
            "Linear Algebra"
        ],
        "Intermediate": [
            "Machine Learning",
            "Scikit-learn",
            "Data Preprocessing",
            "Feature Engineering",
            "Model Evaluation"
        ],
        "Advanced": [
            "TensorFlow",
            "PyTorch",
            "Deep Learning",
            "Model Deployment",
            "MLOps",
            "Production ML Systems"
        ]
    },

    "Web Developer": {
        "Beginner": [
            "HTML",
            "CSS",
            "JavaScript",
            "Git",
            "Responsive Web Design"
        ],
        "Intermediate": [
            "JavaScript ES6",
            "DOM",
            "APIs",
            "React",
            "Frontend Projects"
        ],
        "Advanced": [
            "Advanced React",
            "Authentication",
            "Performance Optimization",
            "Deployment",
            "Web Security",
            "Portfolio Projects"
        ]
    },

    "Full Stack Developer": {
        "Beginner": [
            "HTML",
            "CSS",
            "JavaScript",
            "Git"
        ],
        "Intermediate": [
            "React",
            "Python",
            "SQL",
            "REST APIs",
            "Backend Development"
        ],
        "Advanced": [
            "Authentication",
            "System Design",
            "Docker",
            "Cloud Deployment",
            "Testing",
            "Full Stack Projects"
        ]
    },

    "AI Engineer": {
        "Beginner": [
            "Python",
            "NumPy",
            "Pandas",
            "Mathematics",
            "Statistics"
        ],
        "Intermediate": [
            "Machine Learning",
            "Deep Learning",
            "Neural Networks",
            "TensorFlow",
            "PyTorch"
        ],
        "Advanced": [
            "Natural Language Processing",
            "Computer Vision",
            "Generative AI",
            "Large Language Models",
            "Model Deployment",
            "AI Projects"
        ]
    },

    "Cloud Engineer": {
        "Beginner": [
            "Linux",
            "Networking Basics",
            "Python",
            "Git"
        ],
        "Intermediate": [
            "AWS",
            "Azure",
            "Cloud Storage",
            "Virtual Machines",
            "Docker"
        ],
        "Advanced": [
            "Cloud Architecture",
            "Kubernetes",
            "Infrastructure as Code",
            "Monitoring",
            "Security",
            "Cloud Deployment"
        ]
    },

    "DevOps Engineer": {
        "Beginner": [
            "Linux",
            "Git",
            "Networking",
            "Python"
        ],
        "Intermediate": [
            "Docker",
            "CI/CD",
            "GitHub Actions",
            "AWS",
            "Azure"
        ],
        "Advanced": [
            "Kubernetes",
            "Infrastructure as Code",
            "Terraform",
            "Monitoring",
            "Cloud Security",
            "DevOps Projects"
        ]
    }
}


# --------------------------------------------------
# SELECT CAREER
# --------------------------------------------------

career_options = list(learning_data.keys())

if preferred_career in career_options:

    selected_career = st.selectbox(
        "🎯 Select Career",
        career_options,
        index=career_options.index(preferred_career)
    )

else:

    selected_career = st.selectbox(
        "🎯 Select Career",
        career_options
    )


roadmap = learning_data[selected_career]


# --------------------------------------------------
# DISPLAY ROADMAP
# --------------------------------------------------

st.divider()

st.subheader(
    f"🚀 Learning Roadmap: {selected_career}"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown("### 🟢 Beginner")

    for topic in roadmap["Beginner"]:

        st.checkbox(
            topic,
            key=f"beginner_{selected_career}_{topic}"
        )


with col2:

    st.markdown("### 🟡 Intermediate")

    for topic in roadmap["Intermediate"]:

        st.checkbox(
            topic,
            key=f"intermediate_{selected_career}_{topic}"
        )


with col3:

    st.markdown("### 🔴 Advanced")

    for topic in roadmap["Advanced"]:

        st.checkbox(
            topic,
            key=f"advanced_{selected_career}_{topic}"
        )


# --------------------------------------------------
# SKILLS SECTION
# --------------------------------------------------

st.divider()

st.subheader("💻 Your Current Skills")

if skills_text:

    skills = [
        skill.strip()
        for skill in skills_text.split(",")
        if skill.strip()
    ]

    for skill in skills:
        st.write(f"✅ {skill}")

else:

    st.info(
        "No skills found. Add your skills in Student Profile."
    )


# --------------------------------------------------
# STUDY PLAN
# --------------------------------------------------

st.divider()

st.subheader("📅 Weekly Study Plan")

days = [
    ("Monday", "Learn a new concept"),
    ("Tuesday", "Practice coding"),
    ("Wednesday", "Solve problems"),
    ("Thursday", "Build a small project"),
    ("Friday", "Review previous topics"),
    ("Saturday", "Work on portfolio project"),
    ("Sunday", "Revision and interview practice")
]

for day, activity in days:

    st.write(
        f"**{day}:** {activity}"
    )


# --------------------------------------------------
# PROJECT IDEAS
# --------------------------------------------------

st.divider()

st.subheader("🛠️ Project Ideas")

project_ideas = {

    "Python Developer": [
        "Student Management System",
        "Expense Tracker",
        "Python REST API"
    ],

    "Data Scientist": [
        "Student Performance Prediction",
        "Sales Data Analysis",
        "Customer Churn Analysis"
    ],

    "Machine Learning Engineer": [
        "House Price Prediction",
        "Student Placement Prediction",
        "Recommendation System"
    ],

    "Web Developer": [
        "Portfolio Website",
        "College Website",
        "Online Quiz Application"
    ],

    "Full Stack Developer": [
        "Job Portal",
        "Student Placement Portal",
        "E-Commerce Application"
    ],

    "AI Engineer": [
        "AI Chatbot",
        "Resume Analyzer",
        "Career Recommendation System"
    ],

    "Cloud Engineer": [
        "Cloud File Storage",
        "Cloud Monitoring Dashboard",
        "Containerized Web Application"
    ],

    "DevOps Engineer": [
        "CI/CD Pipeline Project",
        "Dockerized Web Application",
        "Cloud Deployment Project"
    ]
}


for project in project_ideas[selected_career]:

    st.write(f"💡 **{project}**")


st.success(
    "🎯 Follow the roadmap consistently and build projects to strengthen your portfolio."
)


if st.sidebar.button(
    "📋 Application Tracker",
    use_container_width=True
):
    st.switch_page("pages/application_tracker.py")



if st.sidebar.button(
    "🎤 Interview Preparation",
    use_container_width=True
):
    st.switch_page("pages/interview.py")


if st.sidebar.button(
    "📚 Learning Plan",
    use_container_width=True
):
    st.switch_page("pages/learning_plan.py")



if st.button(
    "🎤 Interview Practice",
    use_container_width=True
):
    st.switch_page("pages/interview.py")

if st.button(
    "📚 Learning Plan",
    use_container_width=True
):
    st.switch_page("pages/learning_plan.py")
