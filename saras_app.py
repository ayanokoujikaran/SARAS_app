import streamlit as st
import mysql.connector

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='@KSsani2007',
            database='saras'
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Database connection error: {e}")
        return None

# User login function
def login_user(username, password, role):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        if role == 'Student':
            cursor.execute("SELECT * FROM Students WHERE username=%s AND password=%s", (username, password))
        elif role == 'Admin':
            cursor.execute("SELECT * FROM Admins WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    return None

# Get attendance records for a student
def get_attendance_records(student_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Attendance WHERE student_id=%s", (student_id,))
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        return records
    return []

# Update attendance in the database
def update_attendance(date, presentees, absentees):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        for student_id in presentees:
            cursor.execute("INSERT INTO Attendance (student_id, attendance_date, status) VALUES (%s, %s, 'Present')", (student_id, date))
        for student_id in absentees:
            cursor.execute("INSERT INTO Attendance (student_id, attendance_date, status) VALUES (%s, %s, 'Absent')", (student_id, date))
        connection.commit()
        cursor.close()
        connection.close()

# Main application function
def main():
    st.set_page_config(page_title="SARAS - Student Attendance Record System", page_icon=":books:", layout="wide")
    st.markdown(
        """
        <style>
        .main {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user = None

    if not st.session_state.logged_in:
        st.title("SARAS - Student Attendance Record System")
        role = st.selectbox("Select Role", ["Student", "Admin"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password, role)
            if user:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = user
            else:
                st.error("Invalid credentials")
    else:
        user = st.session_state.user
        role = st.session_state.role
        st.success(f"Welcome {user['name']}!")
        
        if role == "Student":
            records = get_attendance_records(user['student_id'])
            st.write("Your Attendance Records:")
            st.table(records)
        elif role == "Admin":
            st.write("Admin Dashboard")
            date = st.date_input("Select Date")
            presentees = st.text_area("Enter student IDs of presentees (comma-separated)").split(',')
            absentees = st.text_area("Enter student IDs of absentees (comma-separated)").split(',')
            if st.button("Update Attendance"):
                update_attendance(date, presentees, absentees)
                st.success("Attendance updated successfully!")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.user = None

if __name__ == "__main__":
    main()
