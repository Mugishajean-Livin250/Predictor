import streamlit as st
from database import (
    create_tables,
    add_student,
    add_mark,
    get_student_marks,
    get_weekly_marks,
    save_monthly_report,
    save_weekly_report,
    get_all_monthly_reports,
    get_all_weekly_reports
)
from prediction_logic import evaluate_performance


# Initialize DB
create_tables()

# Home Page for login

def home_page():
    st.title("🎓 Student Performance Prediction System")
    st.subheader("Welcome to the Student Performance Prediction System!")
    st.write("""
        This system helps teachers and parents monitor and improve student performance.
        Teachers can input weekly marks, generate progress reports, and view trends.
        Parents can log in to view their child’s performance.
    """)

    user_type = st.radio("Login as:", ["Teacher", "Parent"])
    email = st.text_input("Email", "")
    password = st.text_input("Password", "", type="password")

    if st.button("Log In"):
        if user_type == "Teacher" and email == "teacher@gmail.com" and password == "teacher":
            st.session_state.logged_in = True
            st.session_state.role = "teacher"
            st.success("Teacher logged in successfully! Redirecting to dashboard...")
        elif user_type == "Parent" and email == "parent@gmail.com" and password == "parent":
            st.session_state.logged_in = True
            st.session_state.role = "parent"
            st.success("Parent logged in successfully! Redirecting to dashboard...")
        else:
            st.error("Incorrect credentials. Please try again.")

# Teacher Dashboard

def teacher_dashboard():
    st.title("📊 Teacher Dashboard")

    st.sidebar.subheader("Navigation")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Features")
    st.sidebar.markdown("- Weekly and Monthly Reports")
    st.sidebar.markdown("- Real-time Evaluation Logic")
    st.sidebar.markdown("- Performance Trend Analysis")
    st.sidebar.markdown("- Export Options (PDF/Excel)")
    st.sidebar.markdown("- Parent Portal Access")

    classes = ["S4", "S5", "S6"]
    combinations = {
        "MPG": ["Math", "Physics", "Geography"],
        "PCM": ["Physics", "Chemistry", "Math"],
        "PCB": ["Physics", "Chemistry", "Biology"]
    }

    # Generate sample students
    if st.sidebar.button("🔁 Generate Sample Students"):
        for i in range(1, 6):
            student_id = f"Student00{i}"
            class_name = classes[i % len(classes)]
            combination = list(combinations.keys())[i % len(combinations)]
            add_student(student_id, class_name, combination)
        st.success("Sample students generated.")

    # Weekly Marks Entry
    st.header("📅 Enter Weekly Marks")
    student_ids = [f"Student00{i}" for i in range(1, 6)]
    student_id = st.selectbox("Select Student", student_ids)
    selected_week = st.selectbox("Week", [1, 2, 3, 4])
    selected_comb = st.selectbox("Combination", list(combinations.keys()))
    subjects = combinations[selected_comb]

    marks = {}
    for subject in subjects:
        marks[subject] = st.number_input(f"{subject} score", min_value=0, max_value=100, step=1)

    if st.button("✅ Submit Weekly Marks"):
        if student_id and selected_week and marks:
            for subject, score in marks.items():
                add_mark(student_id, selected_week, subject, score)
            st.success("Weekly marks submitted successfully.")
        else:
            st.error("Please fill all fields before submitting.")

    # Weekly Report
    st.header("🗓️ Generate Weekly Report")
    selected_week_for_report = st.selectbox("Select Week for Report", [1, 2, 3, 4], key="weekly_report")
    if st.button("📅 Process Weekly Reports"):
        for student_id in student_ids:
            records = get_weekly_marks(student_id, selected_week_for_report)
            marks = [score for (_, _, _, score) in records]
            if marks:
                avg, cat, rec = evaluate_performance(marks)
                save_weekly_report(student_id, selected_week_for_report, avg, cat, rec)
        st.success(f"Weekly reports for Week {selected_week_for_report} generated.")

    if st.button("📄 Show Weekly Reports"):
        data = get_all_weekly_reports()
        if data:
            import pandas as pd
            df = pd.DataFrame(data, columns=["Student ID", "Week", "Average Score", "Category", "Recommendation"])
            st.dataframe(df)
        else:
            st.info("No weekly reports available yet.")

    # Monthly Report
    st.header("📈 Generate Monthly Report")
    if st.button("🧠 Process Monthly Reports"):
        for student_id in student_ids:
            records = get_student_marks(student_id)
            marks = [score for (_, _, score) in records]
            if marks:
                avg, cat, rec = evaluate_performance(marks)
                save_monthly_report(student_id, avg, cat, rec)
        st.success("Monthly reports generated.")

    st.header("📋 View Monthly Report Table")
    if st.button("📤 Show Monthly Reports"):
        data = get_all_monthly_reports()
        if data:
            import pandas as pd
            df = pd.DataFrame(data, columns=["Student ID", "Average Score", "Category", "Recommendation"])
            st.dataframe(df)
        else:
            st.info("No monthly reports available yet.")

    # Performance Trends
    st.header("📊 Student Performance Trends")
    selected_trend_student = st.selectbox("Select Student for Trend Analysis", student_ids, key="trend")
    if st.button("📈 Show Trend Graphs"):
        trend_data = get_student_marks(selected_trend_student)
        if trend_data:
            import pandas as pd
            import altair as alt

            trend_df = pd.DataFrame(trend_data, columns=["Week", "Subject", "Score"])

            line_chart = alt.Chart(trend_df).mark_line(point=True).encode(
                x="Week:O",
                y="Score:Q",
                color="Subject:N",
                tooltip=["Week", "Subject", "Score"]
            ).properties(title=f"Weekly Performance Trend - {selected_trend_student}")

            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.warning("No performance data available for this student.")

    # Footer with About & FAQs
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>📬 Contact: info@schoolreportsystem.com | ☎️ +250 788 123 456</p>
        <p><strong>About Us:</strong> This platform is designed to help teachers and parents monitor and improve student academic outcomes with real-time reports and predictions.</p>
        <p><strong>FAQs:</strong><br>
        Q1: How is the prediction calculated?<br>
        A1: We use a weighted average with performance thresholds to assess academic progress.<br>
        Q2: Can parents input data?<br>
        A2: No, only teachers input data while parents have view-only access.</p>
        <p>© 2025 Student Performance System. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Parent Dashboard (read-only view)
def parent_dashboard():
    st.title("👨‍👩‍👧 Parent Dashboard")
    st.subheader("Welcome, dear parent! Here is your student's performance.")
    student_id = st.selectbox("Select Your Child (Student ID)", [f"Student00{i}" for i in range(1, 6)])

    st.write("### 📋 Monthly Report")
    data = get_all_monthly_reports()
    filtered = [row for row in data if row[0] == student_id]
    if filtered:
        import pandas as pd
        df = pd.DataFrame(filtered, columns=["Student ID", "Average Score", "Category", "Recommendation"])
        st.dataframe(df)
    else:
        st.info("No monthly report available for this student.")

    st.write("### 📅 Weekly Performance")
    weekly_data = get_all_weekly_reports()
    filtered_weekly = [row for row in weekly_data if row[0] == student_id]
    if filtered_weekly:
        df2 = pd.DataFrame(filtered_weekly, columns=["Student ID", "Week", "Average Score", "Category", "Recommendation"])
        st.dataframe(df2)
    else:
        st.info("No weekly performance data found.")

# App logic
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    home_page()
else:
    if st.session_state.role == "teacher":
        teacher_dashboard()
    elif st.session_state.role == "parent":
        parent_dashboard()
