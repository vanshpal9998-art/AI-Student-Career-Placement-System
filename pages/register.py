
import streamlit as st
import sys
from pathlib import Path
import bcrypt

# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from database.database import get_connection, create_tables


# Make sure database tables exist
create_tables()


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Student Registration",
    page_icon="📝",
    layout="centered"
)


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("📝 Student Registration")

st.write(
    "Create your account to use the AI Student Career & Placement System."
)


# --------------------------------------------------
# REGISTRATION FORM
# --------------------------------------------------

with st.form("registration_form"):

    name = st.text_input(
        "Full Name",
        placeholder="Enter your full name"
    )

    email = st.text_input(
        "Email Address",
        placeholder="example@gmail.com"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter password"
    )

    submitted = st.form_submit_button(
        "📝 Create Account",
        type="primary"
    )


# --------------------------------------------------
# CREATE ACCOUNT
# --------------------------------------------------

if submitted:

    name = name.strip()
    email = email.strip().lower()

    # Basic validation
    if not name:
        st.error("❌ Please enter your name.")

    elif not email:
        st.error("❌ Please enter your email.")

    elif "@" not in email or "." not in email:
        st.error("❌ Please enter a valid email address.")

    elif not password:
        st.error("❌ Please enter a password.")

    elif len(password) < 6:
        st.error(
            "❌ Password must contain at least 6 characters."
        )

    elif password != confirm_password:
        st.error(
            "❌ Passwords do not match."
        )

    else:

        try:

            connection = get_connection()
            cursor = connection.cursor()

            # Check existing email
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                connection.close()

                st.error(
                    "❌ An account with this email already exists."
                )

            else:

                # Hash password
                hashed_password = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                # Create user
                cursor.execute(
                    """
                    INSERT INTO users (
                        name,
                        email,
                        password,
                        role
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        hashed_password,
                        "student"
                    )
                )

                connection.commit()

                new_user_id = cursor.lastrowid

                connection.close()

                # Create empty student profile
                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute(
                    """
                    INSERT INTO student_profiles (
                        user_id
                    )
                    VALUES (?)
                    """,
                    (new_user_id,)
                )

                connection.commit()
                connection.close()

                st.success(
                    "✅ Account created successfully!"
                )

                st.info(
                    "You can now login using your email and password."
                )

                if st.button(
                    "🔐 Go to Login",
                    type="primary"
                ):
                    st.switch_page(
                        "pages/login.py"
                    )

        except Exception as error:

            st.error(
                f"❌ Registration failed: {error}"
            )


# --------------------------------------------------
# LOGIN LINK
# --------------------------------------------------

st.divider()

st.write("Already have an account?")

if st.button("🔐 Login"):

    st.switch_page(
        "pages/login.py"
    )
