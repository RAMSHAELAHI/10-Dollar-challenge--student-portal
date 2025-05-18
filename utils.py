import streamlit as st  # type: ignore

def display_error(message: str) -> None:
    """Displays an error message in Streamlit."""
    st.error(message)

def display_success(message: str) -> None:
    """Displays a success message in Streamlit."""
    st.success(message)

def validate_input(name: str, roll_no: str, email: str, slot: str, contact: str, course: str, favorite_teacher: str, photo: bytes) -> str | None:
    """Validates input fields, returns error message or None if all inputs are valid."""
    if not name.strip():
        return "Please enter your name."
    if not roll_no.strip():
        return "Please enter your roll number."
    if not email.strip():
        return "Please enter your email."
    if not slot.strip():
        return "Please enter your slot."
    if not contact.strip():
        return "Please enter your contact number."
    if not course.strip():
        return "Please select a course."
    if not favorite_teacher.strip():
        return "Please select your favorite teacher."
    if not photo:
        return "Please upload a photo."
    return None  # All valid

class Course:
    """A dummy Course class to encapsulate grade logic."""
    def __init__(self, name: str):
        self.name = name

    def get_grade(self, marks: int) -> str:
        if marks >= 90:
            return "A"
        elif marks >= 80:
            return "B"
        elif marks >= 70:
            return "C"
        elif marks >= 60:
            return "D"
        else:
            return "F"
