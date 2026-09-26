
import streamlit as st
import bcrypt
import sys
from pathlib import Path

# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables


# Make sure database exists
create_tables()


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Student Login",
    page_icon="🔐",
    layout="centered"
)


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("🔐 Student Login")

st.write(
    "Login to access your AI Student Career & Placement System."
)


# --------------------------------------------------
# LOGIN FORM
# --------------------------------------------------

with st.form("login_form"):

    email = st.text_input(
        "Email Address",
        placeholder="example@gmail.com"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login_button = st.form_submit_button(
        "🔐 Login",
        type="primary"
    )


# --------------------------------------------------
# LOGIN PROCESS
# --------------------------------------------------

if login_button:

    email = email.strip().lower()

    if not email:
        st.error("❌ Please enter your email.")

    elif not password:
        st.error("❌ Please enter your password.")

    else:

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role
                FROM users
                WHERE email = ?
                """,
                (email,)
            )

            user = cursor.fetchone()

            connection.close()

            if user is None:

                st.error(
                    "❌ Invalid email or password."
                )

            else:

                stored_password = user["password"]

                password_correct = bcrypt.checkpw(
                    password.encode("utf-8"),
                    stored_password.encode("utf-8")
                )

                if password_correct:

                    # Save login information
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user["id"]
                    st.session_state["user_name"] = user["name"]
                    st.session_state["user_email"] = user["email"]
                    st.session_state["role"] = user["role"]

                    st.success(
                        f"✅ Welcome, {user['name']}!"
                    )

                    st.switch_page("app.py")

                else:

                    st.error(
                        "❌ Invalid email or password."
                    )

        except Exception as error:

            st.error(
                f"❌ Login failed: {error}"
            )


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

st.divider()

st.write("Don't have an account?")

if st.button(
    "📝 Create New Account",
    use_container_width=True
):

    st.switch_page(
        "pages/register.py"
    )


### Step 21.2 — Improve Logout

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    for key in [
        "logged_in",
        "user_id",
        "user_name",
        "user_email",
        "role"
    ]:
        st.session_state.pop(key, None)

    st.switch_page("pages/login.py")

