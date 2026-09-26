
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
# PAGE CONFIG
# ---------------------------------------------------------

st.title("📄 Resume Analysis")
st.write("Upload your resume and analyze your skills.")


# ---------------------------------------------------------
# CREATE TABLES
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
# UPLOAD FOLDER
# ---------------------------------------------------------

upload_folder = PROJECT_ROOT / "Uploads" / "resumes"

if upload_folder.exists() and not upload_folder.is_dir():
    st.error(
        f"❌ {upload_folder} exists but is not a folder."
    )
    st.stop()

upload_folder.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# SKILLS
# ---------------------------------------------------------

SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "machine learning",
    "artificial intelligence",
    "data science",
    "html",
    "css",
    "javascript",
    "react",
    "django",
    "flask",
    "streamlit",
    "git",
    "github",
    "aws",
    "azure",
    "docker",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch"
]


# ---------------------------------------------------------
# EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(file_path):

    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(str(file_path))

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as error:

        st.error(f"PDF extraction error: {error}")
        return ""


# ---------------------------------------------------------
# EXTRACT TEXT FROM DOCX
# ---------------------------------------------------------

def extract_docx_text(file_path):

    try:
        from docx import Document

        document = Document(str(file_path))

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    except Exception as error:

        st.error(f"DOCX extraction error: {error}")
        return ""


# ---------------------------------------------------------
# DETECT SKILLS
# ---------------------------------------------------------

def detect_skills(text):

    text_lower = text.lower()

    detected = []

    for skill in SKILLS:

        if skill.lower() in text_lower:
            detected.append(skill)

    return detected


# ---------------------------------------------------------
# FILE UPLOADER
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)


# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------

if uploaded_file:

    st.success(
        f"Selected file: {uploaded_file.name}"
    )

    if st.button(
        "🔍 Analyze Resume",
        type="primary"
    ):

        try:

            # Safe filename
            safe_filename = Path(
                uploaded_file.name
            ).name

            # Add user ID to avoid filename conflicts
            file_path = upload_folder / (
                f"{user_id}_{safe_filename}"
            )

            # Save uploaded file
            with open(file_path, "wb") as file:

                file.write(
                    uploaded_file.getbuffer()
                )

            # -------------------------------------------------
            # EXTRACT TEXT
            # -------------------------------------------------

            if safe_filename.lower().endswith(".pdf"):

                resume_text = extract_pdf_text(
                    file_path
                )

            elif safe_filename.lower().endswith(".docx"):

                resume_text = extract_docx_text(
                    file_path
                )

            else:

                resume_text = ""

            # -------------------------------------------------
            # DETECT SKILLS
            # -------------------------------------------------

            detected_skills = detect_skills(
                resume_text
            )

            skills_text = ", ".join(
                detected_skills
            )

            # -------------------------------------------------
            # SAVE DATABASE
            # -------------------------------------------------

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO resumes (
                    user_id,
                    filename,
                    file_path,
                    resume_text,
                    detected_skills
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                safe_filename,
                str(file_path),
                resume_text,
                skills_text
            ))

            connection.commit()
            connection.close()

            # -------------------------------------------------
            # DISPLAY RESULT
            # -------------------------------------------------

            st.success(
                "✅ Resume uploaded and analyzed successfully!"
            )

            st.subheader("🧠 Detected Skills")

            if detected_skills:

                for skill in detected_skills:
                    st.write(f"✅ {skill.title()}")

            else:

                st.info(
                    "No predefined skills were detected."
                )

            st.subheader("📄 Resume Text")

            if resume_text.strip():

                st.text_area(
                    "Extracted resume content",
                    resume_text,
                    height=300
                )

            else:

                st.warning(
                    "Could not extract text from this resume."
                )

        except Exception as error:

            st.error(
                f"❌ Could not save analysis: {error}"
            )


# ---------------------------------------------------------
# PREVIOUS RESUMES
# ---------------------------------------------------------

st.divider()

st.subheader("📚 Previous Resume Analyses")

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT
        filename,
        detected_skills,
        id
    FROM resumes
    WHERE user_id = ?
    ORDER BY id DESC
""", (user_id,))

resumes = cursor.fetchall()

connection.close()


if resumes:

    for resume in resumes:

        with st.expander(
            f"📄 {resume['filename']}"
        ):

            st.write(
                "**Detected Skills:**"
            )

            if resume["detected_skills"]:

                st.write(
                    resume["detected_skills"]
                )

            else:

                st.write(
                    "No skills detected."
                )

else:

    st.info(
        "No resume has been uploaded yet."
    )

