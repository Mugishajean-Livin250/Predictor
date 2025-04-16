def evaluate_performance(marks):
    total = sum(marks)
    avg = total / len(marks)
    failed_subjects = sum(1 for mark in marks if mark < 40)

    if avg >= 90:
        category = "Outstanding"
        recommendation = "This student consistently performs at a high level. \nEncourage participation in academic competitions or leadership roles."
    elif avg >= 75:
        category = "Strong"
        recommendation = "Performance is solid. Keep challenging the student with more advanced material to maximize growth."
    elif avg >= 60:
        category = "Average"
        recommendation = "Student is doing okay, but more attention is needed to avoid slipping. Recommend setting study goals and reviewing weak areas weekly."
    elif avg >= 40:
        category = "Below Average"
        recommendation = "Performance is slipping. Recommend after-school tutoring and increased parental involvement."
    else:
        category = "At Risk"
        recommendation = "Severe performance issues. Immediate academic intervention and counseling are required, \ncheck teacher's methodolody or if there is apersonal isuue the student is dealing with."

    if failed_subjects >= 2 and avg < 50:
        recommendation += " ⚠️ Student failed multiple subjects and is at a high risk of repeating the class."

    return round(avg, 2), category, recommendation
