import streamlit as st
import pandas as pd
import yagmail
import sqlite3
from datetime import datetime

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

# Initialize database
create_tables()

# Setup deletion log
if "deletion_log" not in st.session_state:
    st.session_state.deletion_log = []

def home_page():
    st.title(" Student Performance Prediction System")
    st.subheader("Welcome to the Student Performance Prediction System!")
    st.write("""
        This system helps teachers monitor and improve student performance.
        Teachers can input weekly marks, generate reports, view trends, and email performance to parents.
    """)

    email = st.text_input("Email", "")
    password = st.text_input("Password", "", type="password")

    if st.button("Log In"):
        if email == "teacher@gmail.com" and password == "teacher":
            st.session_state.logged_in = True
            st.session_state.role = "teacher"
            st.success("Teacher logged in successfully!")
        else:
            st.error("Incorrect credentials. Please try again.")

def teacher_dashboard():
    st.title("Teacher Dashboard")

    # --- SIDEBAR ---
    st.sidebar.subheader("Navigation")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    st.sidebar.markdown("### Features")
    st.sidebar.markdown("- Weekly and Monthly Reports")
    st.sidebar.markdown("- Real-time Evaluation Logic")
    st.sidebar.markdown("- Performance Trend Analysis")
    st.sidebar.markdown("- Export Options")
    st.sidebar.markdown("- Parent Email Reports")
    st.sidebar.markdown("- Delete Student Records")

    # --- EMAIL REPORT ---
    st.sidebar.markdown("###  Email Parent")
    with st.sidebar.expander(" Send Student Marks to Parent"):
        sender_email = st.text_input("Your Gmail", key="sender")
        app_password = st.text_input("App Password", type="password", key="password")
        receiver_email = st.text_input("Parent Email", key="receiver")
        student_id = st.selectbox("Select Student", [f"Student00{i}" for i in range(1, 6)], key="email_student")

        if st.button("Send Report Email"):
            weekly_data = [row for row in get_all_weekly_reports() if row[0] == student_id]
            monthly_data = [row for row in get_all_monthly_reports() if row[0] == student_id]

            if not weekly_data and not monthly_data:
                st.warning("No marks found for this student.")
            else:
                try:
                    yag = yagmail.SMTP(user=sender_email, password=app_password)
                    subject = f" Performance Report for {student_id}"
                    body = f"Hello Parent,\n\nHere are the latest performance reports for {student_id}:\n"

                    for row in weekly_data:
                        _, week, _, _, _ = row
                        records = get_weekly_marks(student_id, week)
                        subject_scores = {sub: score for (_, _, sub, score) in records}
                        _, _, _, feedback = evaluate_performance(subject_scores)
                        body += f"\nWeek {week} Feedback:\n"
                        for line in feedback.values():
                            body += f" - {line}\n"

                    if monthly_data:
                        row = monthly_data[0]
                        _, avg, cat, rec = row
                        body += f"\n\n Monthly Summary:\nAverage: {avg}%\nCategory: {cat}\nRecommendation: {rec}\n"

                    yag.send(to=receiver_email, subject=subject, contents=body)
                    st.success(" Email sent successfully!")
                except Exception as e:
                    st.error(f" Error sending email: {e}")

    # --- DELETE SECTION ---
    st.sidebar.markdown("###  Delete Student Records")
    with st.sidebar.expander("Manage Deletions"):
        del_student_id = st.selectbox("Student ID", [f"Student00{i}" for i in range(1, 6)], key="del_id")
        del_scope = st.radio("Delete Scope", ["Entire Student", "Specific Week"], key="del_scope")

        if del_scope == "Specific Week":
            del_week = st.selectbox("Select Week", [1, 2, 3, 4], key="del_week")

        confirm = st.checkbox(" I confirm I want to delete this data")

        if st.button("Delete Now") and confirm:
            try:
                conn = sqlite3.connect("student_performance.db")
                c = conn.cursor()

                if del_scope == "Entire Student":
                    c.execute("DELETE FROM weekly_subject_marks WHERE student_id = ?", (del_student_id,))
                    c.execute("DELETE FROM weekly_report WHERE student_id = ?", (del_student_id,))
                    c.execute("DELETE FROM monthly_report WHERE student_id = ?", (del_student_id,))
                    c.execute("DELETE FROM students WHERE student_id = ?", (del_student_id,))
                    log_msg = f" Deleted all records for {del_student_id} at {datetime.now().strftime('%H:%M:%S')}"
                else:
                    c.execute("DELETE FROM weekly_subject_marks WHERE student_id = ? AND week = ?", (del_student_id, del_week))
                    c.execute("DELETE FROM weekly_report WHERE student_id = ? AND week = ?", (del_student_id, del_week))
                    log_msg = f" Deleted Week {del_week} for {del_student_id} at {datetime.now().strftime('%H:%M:%S')}"

                conn.commit()
                conn.close()
                st.session_state.deletion_log.insert(0, log_msg)
                st.sidebar.success(" Deletion successful.")
            except Exception as e:
                st.sidebar.error(f"Error during deletion: {e}")

        if st.session_state.deletion_log:
            st.sidebar.markdown("#### Deletion Log:")
            for log_entry in st.session_state.deletion_log[:10]:
                st.sidebar.write(log_entry)

    # --- MAIN PAGE FEATURES ---
    st.header("Enter Weekly Marks")
    classes = ["S4", "S5", "S6"]
    combinations = {
        "MPG": ["Math", "Physics", "Geography"],
        "PCM": ["Physics", "Chemistry", "Math"],
        "PCB": ["Physics", "Chemistry", "Biology"]
    }

    if st.sidebar.button("Generate Sample Students"):
        for i in range(1, 6):
            student_id = f"Student00{i}"
            class_name = classes[i % len(classes)]
            combination = list(combinations.keys())[i % len(combinations)]
            add_student(student_id, class_name, combination)
        st.success("Sample students generated.")

    student_ids = [f"Student00{i}" for i in range(1, 6)]
    student_id = st.selectbox("Select Student", student_ids)
    selected_week = st.selectbox("Week", [1, 2, 3, 4])
    selected_comb = st.selectbox("Combination", list(combinations.keys()))
    subjects = combinations[selected_comb]

    marks = {subject: st.number_input(f"{subject} score", min_value=0, max_value=100, step=1) for subject in subjects}

    if st.button(" Submit Weekly Marks"):
        for subject, score in marks.items():
            add_mark(student_id, selected_week, subject, score)
        st.success("Weekly marks submitted successfully.")

    st.header("Generate Weekly Report")
    selected_week_for_report = st.selectbox("Select Week for Report", [1, 2, 3, 4], key="weekly_report")
    if st.button(" Process Weekly Reports"):
        for student_id in student_ids:
            records = get_weekly_marks(student_id, selected_week_for_report)
            subject_scores = {subject: score for (_, _, subject, score) in records}
            if subject_scores:
                avg, cat, rec, feedback = evaluate_performance(subject_scores)
                save_weekly_report(student_id, selected_week_for_report, avg, cat, rec)
                st.markdown(f"### Feedback for {student_id}:")
                for msg in feedback.values():
                    st.write(f"- {msg}")
        st.success(f"Weekly reports for Week {selected_week_for_report} generated.")

    if st.button(" Show Weekly Reports"):
        data = get_all_weekly_reports()
        if data:
            df = pd.DataFrame(data, columns=["Student ID", "Week", "Average Score", "Category", "Recommendation"])
            st.dataframe(df)
        else:
            st.info("No weekly reports available yet.")

    st.header(" Generate Monthly Report")
    if st.button(" Process Monthly Reports"):
        for student_id in student_ids:
            records = get_student_marks(student_id)
            subject_scores = {subject: score for (_, subject, score) in records}
            if subject_scores:
                avg, cat, rec, feedback = evaluate_performance(subject_scores)
                save_monthly_report(student_id, avg, cat, rec)
        st.success("Monthly reports generated.")

    st.header(" View Monthly Report Table")
    if st.button(" Show Monthly Reports"):
        data = get_all_monthly_reports()
        if data:
            df = pd.DataFrame(data, columns=["Student ID", "Average Score", "Category", "Recommendation"])
            st.dataframe(df)
        else:
            st.info("No monthly reports available yet.")

    st.header(" Student Performance Trends")
    selected_trend_student = st.selectbox("Select Student for Trend Analysis", student_ids, key="trend")
    if st.button(" Show Trend Graphs"):
        trend_data = get_student_marks(selected_trend_student)
        if trend_data:
            trend_df = pd.DataFrame(trend_data, columns=["Week", "Subject", "Score"])
            import altair as alt
            line_chart = alt.Chart(trend_df).mark_line(point=True).encode(
                x="Week:O", y="Score:Q", color="Subject:N", tooltip=["Week", "Subject", "Score"]
            ).properties(title=f"Weekly Performance Trend - {selected_trend_student}")
            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.warning("No performance data available for this student.")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p> Contact: info@schoolreportsystem.com | ☎️ +250 788 123 456</p>
        <p><strong>About Us:</strong> Monitor and improve student outcomes with real-time reports and predictions.</p>
        <p><strong>FAQs:</strong><br>
        Q1: How is the prediction calculated?<br>
        A1: Subject-wise analysis with performance categories and advice.<br>
        Q2: Can parents input data?<br>
        A2: No, only teachers input data.</p>
        <p>© 2025 Student Performance System. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# App Logic
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    home_page()
else:
    teacher_dashboard()
