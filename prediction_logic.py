def evaluate_performance(marks_by_subject):
    feedback = {}
    total = 0
    count = 0

    for subject, mark in marks_by_subject.items():
        try:
            mark = int(mark)
        except ValueError:
            continue

        count += 1
        total += mark

        if mark >= 85:
            fb = " Exceptional performance. Keep it up!"
        elif mark >= 75:
            fb = " Excellent understanding of the subject."
        elif mark >= 65:
            fb = " Good performance. Some improvement possible."
        elif mark >= 55:
            fb = " Fair. Try revising and practicing more."
        elif mark >= 45:
            fb = " Weak performance. Focus and ask for help."
        elif mark >= 35:
            fb = " Poor. Needs serious improvement."
        else:
            fb = " Critical. Immediate attention required."

        feedback[subject] = f"{subject}: {mark} – {fb}"

    avg = total / count if count else 0
    failed_subjects = sum(1 for m in marks_by_subject.values() if int(m) < 40)

    if avg >= 90:
        category = "Outstanding"
        recommendation = "This student consistently performs at a high level. Encourage participation in academic competitions or leadership roles."
    elif avg >= 75:
        category = "Strong"
        recommendation = "Performance is solid. Keep challenging the student with more advanced material to maximize growth."
    elif avg >= 60:
        category = "Average"
        recommendation = "Student is doing okay, but more attention is needed to avoid slipping. Recommend setting study goals and reviewing weak areas weekly."
    elif avg >= 45:
        category = "Below Average"
        recommendation = "Performance is slipping. Recommend after-school tutoring and increased parental involvement."
    elif avg >= 35:
        category = "Poor"
        recommendation = "Performance is poor. Consistent monitoring and focused support are required."
    else:
        category = "At Risk"
        recommendation = "Severe performance issues. Immediate academic intervention and counseling are required."

    if failed_subjects >= 2 and avg < 50:
        recommendation += " ⚠️ Student failed multiple subjects and is at high risk."

    return round(avg, 2), category, recommendation, feedback
