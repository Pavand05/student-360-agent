import os
import pandas as pd
from backend.agent.models import Student
from backend.agent.agent import Student360Agent
from backend.firestore_service import FirestoreService


def import_excel_and_run_agent(excel_file_path: str = "students_dataset.xlsx"):
    """
    Reads an Excel file (.xlsx) containing student metrics across multiple classes (8th, 9th, 10th grade),
    runs the Google ADK Agent pipeline, and persists student records and AI risk assessments into Firestore.
    """
    print(f"=== Excel Import Pipeline: Ingesting '{excel_file_path}' ===")
    
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found at: {excel_file_path}")

    # Read Excel sheet into pandas DataFrame
    df = pd.read_excel(excel_file_path)
    print(f"[Excel Parser] Loaded {len(df)} student rows across classes: {list(df['class'].unique())}")

    firestore_service = FirestoreService()
    agent = Student360Agent()

    processed_count = 0

    for idx, row in df.iterrows():
        # Parse subject exam mark series
        subjects = {
            "Maths": [float(row["Maths_Exam1"]), float(row["Maths_Exam2"]), float(row["Maths_Exam3"])],
            "Science": [float(row["Science_Exam1"]), float(row["Science_Exam2"]), float(row["Science_Exam3"])],
            "English": [float(row["English_Exam1"]), float(row["English_Exam2"]), float(row["English_Exam3"])]
        }

        student = Student(
            studentId=str(row["studentId"]),
            name=str(row["name"]),
            class_name=str(row["class"]),
            attendance=float(row["attendance"]),
            assignmentSubmission=float(row["assignmentSubmission"]),
            subjects=subjects
        )

        # 1. Save student to Firestore
        student_dict = student.model_dump(by_alias=True)
        firestore_service.save_student(student_dict)

        # 2. Run Google ADK Agent Analysis
        print(f"[Agent] Assessing Student 360: {student.studentId} - {student.name} ({student.class_name})...")
        assessment = agent.analyze_student(student)

        # 3. Save AI Risk Assessment to Firestore
        assessment_dict = assessment.model_dump(by_alias=True)
        firestore_service.save_risk_assessment(assessment_dict)
        print(f"   -> Result: {assessment.overallRiskLevel} Risk | Priority Score: {assessment.compositeRiskScore}")

        processed_count += 1

    print(f"=== Excel Ingestion & ADK Agent Pipeline Completed: {processed_count} Students Assessed ===")


if __name__ == "__main__":
    import_excel_and_run_agent()
