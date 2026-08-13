import pandas as pd

# Sample Multi-Grade Student Dataset across 8th, 9th, and 10th Classes
STUDENT_RECORDS = [
    # Class 8th
    {
        "studentId": "S001", "name": "Rahul Sharma", "class": "8-B", "attendance": 78.0, "assignmentSubmission": 85.0,
        "Maths_Exam1": 82, "Maths_Exam2": 68, "Maths_Exam3": 51,
        "Science_Exam1": 75, "Science_Exam2": 73, "Science_Exam3": 71,
        "English_Exam1": 80, "English_Exam2": 78, "English_Exam3": 76
    },
    {
        "studentId": "S002", "name": "Ananya Verma", "class": "8-B", "attendance": 96.0, "assignmentSubmission": 95.0,
        "Maths_Exam1": 88, "Maths_Exam2": 91, "Maths_Exam3": 94,
        "Science_Exam1": 90, "Science_Exam2": 92, "Science_Exam3": 95,
        "English_Exam1": 85, "English_Exam2": 87, "English_Exam3": 89
    },
    {
        "studentId": "S003", "name": "Vikram Patel", "class": "8-A", "attendance": 82.0, "assignmentSubmission": 90.0,
        "Maths_Exam1": 85, "Maths_Exam2": 84, "Maths_Exam3": 86,
        "Science_Exam1": 88, "Science_Exam2": 87, "Science_Exam3": 89,
        "English_Exam1": 82, "English_Exam2": 80, "English_Exam3": 83
    },
    # Class 9th
    {
        "studentId": "S007", "name": "Aditya Roy", "class": "9-A", "attendance": 72.0, "assignmentSubmission": 75.0,
        "Maths_Exam1": 79, "Maths_Exam2": 62, "Maths_Exam3": 46,  # 41.7% drop -> HIGH RISK
        "Science_Exam1": 80, "Science_Exam2": 78, "Science_Exam3": 75,
        "English_Exam1": 76, "English_Exam2": 74, "English_Exam3": 72
    },
    {
        "studentId": "S008", "name": "Meera Joshi", "class": "9-A", "attendance": 94.0, "assignmentSubmission": 96.0,
        "Maths_Exam1": 92, "Maths_Exam2": 95, "Maths_Exam3": 97,  # Top performer -> LOW RISK
        "Science_Exam1": 89, "Science_Exam2": 93, "Science_Exam3": 96,
        "English_Exam1": 91, "English_Exam2": 94, "English_Exam3": 95
    },
    {
        "studentId": "S009", "name": "Tanvi Deshmukh", "class": "9-B", "attendance": 83.0, "assignmentSubmission": 89.0,
        "Maths_Exam1": 81, "Maths_Exam2": 76, "Maths_Exam3": 70,  # Mild drop -> MEDIUM RISK
        "Science_Exam1": 82, "Science_Exam2": 80, "Science_Exam3": 78,
        "English_Exam1": 85, "English_Exam2": 84, "English_Exam3": 83
    },
    {
        "studentId": "S010", "name": "Yash Vardhan", "class": "9-B", "attendance": 66.0, "assignmentSubmission": 68.0,
        "Maths_Exam1": 70, "Maths_Exam2": 58, "Maths_Exam3": 42,  # Severe drop & low attendance -> HIGH RISK
        "Science_Exam1": 68, "Science_Exam2": 56, "Science_Exam3": 49,
        "English_Exam1": 72, "English_Exam2": 65, "English_Exam3": 58
    },
    # Class 10th
    {
        "studentId": "S011", "name": "Kavya Menon", "class": "10-A", "attendance": 98.0, "assignmentSubmission": 97.0,
        "Maths_Exam1": 95, "Maths_Exam2": 97, "Maths_Exam3": 99,  # Star student -> LOW RISK
        "Science_Exam1": 96, "Science_Exam2": 98, "Science_Exam3": 100,
        "English_Exam1": 94, "English_Exam2": 95, "English_Exam3": 96
    },
    {
        "studentId": "S012", "name": "Rohan Kulkarni", "class": "10-A", "attendance": 76.0, "assignmentSubmission": 82.0,
        "Maths_Exam1": 84, "Maths_Exam2": 69, "Maths_Exam3": 52,  # 38% drop in 10th board prep -> HIGH RISK
        "Science_Exam1": 82, "Science_Exam2": 80, "Science_Exam3": 78,
        "English_Exam1": 80, "English_Exam2": 78, "English_Exam3": 76
    },
    {
        "studentId": "S013", "name": "Sneha Reddy", "class": "10-B", "attendance": 84.0, "assignmentSubmission": 90.0,
        "Maths_Exam1": 82, "Maths_Exam2": 78, "Maths_Exam3": 72,  # Attendance watch -> MEDIUM RISK
        "Science_Exam1": 85, "Science_Exam2": 83, "Science_Exam3": 81,
        "English_Exam1": 86, "English_Exam2": 85, "English_Exam3": 84
    },
    {
        "studentId": "S014", "name": "Arjun Kapoor", "class": "10-B", "attendance": 62.0, "assignmentSubmission": 60.0,
        "Maths_Exam1": 75, "Maths_Exam2": 58, "Maths_Exam3": 40,  # Critical attendance & marks -> HIGH RISK
        "Science_Exam1": 72, "Science_Exam2": 55, "Science_Exam3": 44,
        "English_Exam1": 70, "English_Exam2": 62, "English_Exam3": 52
    }
]

def generate_excel_and_csv():
    df = pd.DataFrame(STUDENT_RECORDS)
    excel_path = "students_dataset.xlsx"
    csv_path = "students_dataset.csv"

    df.to_excel(excel_path, index=False)
    df.to_csv(csv_path, index=False)

    print(f"[Success] Generated Excel file: {excel_path}")
    print(f"[Success] Generated CSV file: {csv_path}")
    print(f"Total Rows: {len(df)} across Classes: {list(df['class'].unique())}")

if __name__ == "__main__":
    generate_excel_and_csv()
