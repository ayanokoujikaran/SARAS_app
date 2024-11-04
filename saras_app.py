import streamlit as st
import mysql.connector

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='sql12.freesqldatabase.com',
            user='sql12738793',
            password='nYPr75TmMH',
            database='sql12738793',
            port=3306
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Database connection error: {e}")
        return None

# User login function
def login_user(username, credential, role):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        if role == 'Student':
            cursor.execute("SELECT * FROM Students WHERE username=%s AND student_id=%s", (username, credential))
        elif role == 'Admin':
            cursor.execute("SELECT * FROM Admins WHERE username=%s AND password=%s", (username, credential))
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
        for roll_no in presentees:
            cursor.execute("INSERT INTO Attendance (student_id, attendance_date, status) VALUES ((SELECT student_id FROM Students WHERE roll_no=%s), %s, 'Present')", (roll_no, date))
        for roll_no in absentees:
            cursor.execute("INSERT INTO Attendance (student_id, attendance_date, status) VALUES ((SELECT student_id FROM Students WHERE roll_no=%s), %s, 'Absent')", (roll_no, date))
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
            color: white.
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
        credential = st.text_input("Student ID" if role == "Student" else "Password", type="password")
        if st.button("Login"):
            user = login_user(username, credential, role)
            if user:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = user
            else:
                st.error("Invalid credentials")
    else:
        user = st.session_state.user
        role = st.session_state.role
        st.success(f"Welcome {user['username']}!")
        
        if role == "Student":
            records = get_attendance_records(user['student_id'])
            st.write("Your Attendance Records:")
            st.table(records)
        elif role == "Admin":
            st.write("Admin Dashboard")
            date = st.date_input("Select Date")
            mode = st.radio("Update Mode", ["Presentees", "Absentees"])
            if mode == "Presentees":
                presentees = st.text_area("Enter roll numbers of presentees (comma-separated)").split(',')
                absentees = get_absentees(presentees)
            else:
                absentees = st.text_area("Enter roll numbers of absentees (comma-separated)").split(',')
                presentees = get_presentees(absentees)
            if st.button("Update Attendance"):
                update_attendance(date, presentees, absentees)
                st.success("Attendance updated successfully!")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.user = None

def get_absentees(presentees):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT roll_no FROM Students WHERE roll_no NOT IN (%s)", (",".join(map(str, presentees)),))
        absentees = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return absentees
    return []

def get_presentees(absentees):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT roll_no FROM Students WHERE roll_no NOT IN (%s)", (",".join(map(str, absentees)),))
        presentees = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()
        return presentees
    return []

if __name__ == "__main__":
    main()
