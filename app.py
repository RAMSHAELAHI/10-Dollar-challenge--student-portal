import streamlit as st # type: ignore
import sqlite3
from contextlib import contextmanager
from database import get_db_connection, setup_database
from PIL import Image # type: ignore
import io

st.sidebar.header("GIAIC Student Portal")

slot_teacher_map = {
    "Monday 2-5 PM": "Sir Zia",
    "Tuesday 2-5 PM": "Sir Asharib",
    "Wednesday 2-5 PM": "Sir Ali Aftab",
    "Thursday 2-5 PM": "Sir Aneeq",
    "Friday 2-5 PM": "Sir Hamzah Syed",
    "Saturday 2-5 PM": "Sir Ali Aftab",
    "Sunday 2-5 PM": "Sir Muhammad Bilal Khan"
}

faq_data = {
    "Typescript": [
        "What are the benefits of using TypeScript?",
        "How does TypeScript relate to JavaScript?",
        "What are interfaces and types in TypeScript?"
    ],
    "Next.js": [
        "What is Next.js and what is it used for?",
        "What are the key features of Next.js?",
        "How does routing work in Next.js?"
    ],
    "Python": [
        "What are the basic data types in Python?",
        "How do you define functions in Python?",
        "What are some popular libraries in Python?"
    ],
    "General": [
        "How do I register for a course?",
        "What if I forget my password?",
        "Who should I contact for technical support?"
    ]
}

def register():
    st.header("📋 Student Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not all([username, password]):
            st.warning("Please fill all fields.")
            return
        try:
            with get_db_connection() as cursor:
                cursor.execute("INSERT INTO students (username, password, name, roll_number, class, slot, photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               ('new_user', password, '', '', '', '', None)) # Basic insert, more details in profile
            st.success("Registration successful! Now login.")
        except sqlite3.IntegrityError:
            st.error("Username already exists.")

def login():
    st.header("🔐 Student Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not all([username, password]):
            st.warning("Please fill all fields.")
            return
        with get_db_connection() as cursor:
            cursor.execute("SELECT * FROM students WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully.")
            else:
                st.error("Invalid credentials.")

def dashboard():
    st.header(f"📊 Dashboard")
    if st.session_state.logged_in:
        st.subheader(f"Welcome, {st.session_state.username}!")
        st.info("All card generation features are now under 'GIAIC Card Generator' in the navigation.")
    else:
        st.info("Please log in to view the dashboard.")
        login()

def faqs():
    st.header("❓ Frequently Asked Questions")
    course = st.selectbox("Select a Course", list(faq_data.keys()))
    if course:
        st.subheader(f"FAQs for {course}:")
        for question in faq_data[course]:
            st.markdown(f"- {question}")

def card_generator():
    st.subheader("💳 GIAIC Card Generator")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
        roll_number = st.text_input("Roll Number", placeholder="e.g., GIAIC-SP24-001")
        # Slot Selection for the card
        card_slot = st.selectbox("Slot", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        # Timings Selection for the card
        timings = st.selectbox("Timings", ["9:00 to 12:00", "2:00 - 5:00", "7:00-10:00"])

        if st.button("Generate Card"):
            if name and roll_number and card_slot and timings and uploaded_file:
                st.success("Card Generated!") # Placeholder for actual card generation
            elif any([not name, not roll_number, not card_slot, not timings, uploaded_file is None]):
                st.warning("Please fill all the information and upload a profile picture.")

        st.subheader("Course Information:")
        # Display Slot Selection (related to teacher)
        st.subheader("Select Class Slot:")
        available_slots = list(slot_teacher_map.keys())
        teacher_slot = st.selectbox("Available Slots", available_slots)
        st.write(f"Selected Class Slot: {teacher_slot}")

        # Teachers Information based on selected slot
        st.subheader("Teacher for the selected class slot:")
        teacher = slot_teacher_map.get(teacher_slot)
        if teacher:
            st.write(f"The teacher for {teacher_slot} is: {teacher}")
        else:
            st.write("No teacher assigned for this slot.")

        # Quarter Courses
        st.subheader("Quarter Courses:")
        st.markdown("- **Q1: Typescript**: <span style='float: right;'>Passed</span>", unsafe_allow_html=True)
        st.markdown("- **Q2: Next.js**: <span style='float: right;'>Passed</span>", unsafe_allow_html=True)
        st.markdown("- **Q3: Python**: <span style='float: right;'>Result will be announced after final viva</span>", unsafe_allow_html=True)
        st.markdown("- **Q4: Agentic AI - Next & last quarter**")

    with col2:
        uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Profile Picture", width=150)

def feedback():
    st.header("📝 Student Course Feedback")
    if st.session_state.logged_in:
        courses = ["Typescript", "Next.js", "Python", "Agentic AI"]
        selected_course = st.selectbox("Select a Course", courses)
        feedback_text = st.text_area(f"Feedback for {selected_course}", "Enter your feedback here...")
        if st.button("Submit Feedback"):
            if feedback_text:
                st.success(f"Thank you for your feedback on {selected_course}!")
                # In a real application, you would save this feedback to a database
            else:
                st.warning("Please enter your feedback.")
    else:
        st.info("Please log in to provide feedback.")
        login()

def main():
    setup_database()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ''

    navigation_options = ["Home", "Registration", "Login", "Dashboard", "FAQs", "GIAIC Card Generator"]
    if st.session_state.logged_in:
        navigation_options.append("Logout")
        navigation_options.append("Course Feedback") # Added Course Feedback

    home_option = st.sidebar.selectbox(
        "Navigate",
        navigation_options
    )

    if home_option == "Registration":
        register()
    elif home_option == "Login":
        login()
    elif home_option == "Dashboard":
        dashboard()
    elif home_option == "FAQs":
        faqs()
    elif home_option == "GIAIC Card Generator":
        card_generator()
    elif home_option == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.success("Logged out successfully.")
    elif home_option == "Course Feedback":
        feedback()
    elif home_option == "Home":
        st.markdown(
            """
            <style>
            .background-giaic {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 150px;
                font-weight: bold;
                color: #f0f2f6; /* Light grey */
                opacity: 0.5;
                z-index: -1;
            }
            </style>
            <div class="background-giaic">GIAIC</div>
            <h1>Welcome to the Student Portal!</h1>
            <p>Please use the navigation in the sidebar to access different sections.</p>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()