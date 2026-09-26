import streamlit as st
from google import genai
import os
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# LOGIN CHECK
# --------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()


# --------------------------------------------------
# API KEY
# --------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "Gemini API key not found."
    )

    st.info(
        "Set GEMINI_API_KEY in PowerShell and restart Streamlit."
    )

    st.stop()


client = genai.Client(
    api_key=api_key
)


# --------------------------------------------------
# LOAD CAREER KNOWLEDGE
# --------------------------------------------------

knowledge_file = (
    Path(__file__).resolve().parents[1]
    / "ai"
    / "knowledge_base"
    / "career_guide.txt"
)


if knowledge_file.exists():

    with open(
        knowledge_file,
        "r",
        encoding="utf-8"
    ) as file:

        career_knowledge = file.read()

else:

    career_knowledge = ""


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("🤖 AI Career & Placement Assistant")

st.write(
    "Ask me about careers, skills, resumes, "
    "interviews, placements and learning plans."
)


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your AI Career Assistant. "
                "Ask me anything about your career, "
                "resume, skills, interviews or placements."
            )
        }
    ]


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

prompt = st.chat_input(
    "Ask your career question..."
)


# --------------------------------------------------
# SEND MESSAGE
# --------------------------------------------------

if prompt:

    # Display user message
    with st.chat_message("user"):

        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    # --------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------

    system_instruction = """
You are an AI Student Career and Placement Assistant.

Your job is to help college students with:

- Career selection
- Resume improvement
- Skill development
- Skill gap analysis
- Job preparation
- Technical interviews
- HR interviews
- Learning plans
- Placement preparation
- Projects
- Programming and technology learning

Give clear, practical and beginner-friendly answers.

Use the provided career knowledge when relevant.

Do not invent information from the knowledge base.
If the knowledge base does not contain the answer,
you may provide general educational guidance.

Career knowledge:

""" + career_knowledge


    try:

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=(
                        system_instruction
                        + "\n\nStudent question:\n"
                        + prompt
                    )
                )

                answer = response.text

            st.markdown(answer)


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


    except Exception as e:

        st.caption(
            f"Error: {e}"
        )


# --------------------------------------------------
# CLEAR CHAT
# --------------------------------------------------

if st.button("🗑️ Clear Chat"):

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Chat cleared. 👋 "
                "What would you like to learn?"
            )
        }
    ]

    st.rerun()