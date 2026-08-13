from typing import List
from backend.agent.models import Student
from backend.agent.agent import Student360Agent
from backend.firestore_service import FirestoreService


SAMPLE_STUDENTS = [
    Student(
        studentId="S001",
        name="Rahul Sharma",
        class_name="8-B",
        attendance=78.0,
        assignmentSubmission=85.0,
        subjects={
            "Maths": [82.0, 68.0, 51.0],
            "Science": [75.0, 73.0, 71.0],
            "English": [80.0, 78.0, 76.0]
        }
    ),
    Student(
        studentId="S002",
        name="Ananya Verma",
        class_name="8-B",
        attendance=96.0,
        assignmentSubmission=95.0,
        subjects={
            "Maths": [88.0, 91.0, 94.0],
            "Science": [90.0, 92.0, 95.0],
            "English": [85.0, 87.0, 89.0]
        }
    ),
    Student(
        studentId="S003",
        name="Vikram Patel",
        class_name="8-A",
        attendance=68.0,
        assignmentSubmission=90.0,
        subjects={
            "Maths": [85.0, 84.0, 86.0],
            "Science": [88.0, 87.0, 89.0],
            "English": [82.0, 80.0, 83.0]
        }
    ),
    Student(
        studentId="S004",
        name="Priya Nair",
        class_name="8-A",
        attendance=91.0,
        assignmentSubmission=72.0,
        subjects={
            "Maths": [78.0, 76.0, 75.0],
            "Science": [82.0, 74.0, 65.0],
            "English": [88.0, 85.0, 84.0]
        }
    ),
    Student(
        studentId="S005",
        name="Karan Gupta",
        class_name="8-B",
        attendance=64.0,
        assignmentSubmission=65.0,
        subjects={
            "Maths": [70.0, 58.0, 45.0],
            "Science": [68.0, 55.0, 48.0],
            "English": [72.0, 68.0, 60.0]
        }
    )
]


def seed_database_and_run_agent():
    """
    Seeds raw student metrics into Firestore and runs the Google ADK Agent
    to analyze performance and persist risk assessments.
    """
    print("=== Student 360 Agent: Seeding & Analysis ===")
    firestore_service = FirestoreService()
    agent = Student360Agent()

    for student in SAMPLE_STUDENTS:
        # Save raw student data
        student_dict = student.model_dump(by_alias=True)
        firestore_service.save_student(student_dict)
        print(f"[Seed] Saved student record: {student.studentId} - {student.name}")

        # Run ADK agent analysis
        print(f"[Agent] Analyzing Student 360 for {student.name}...")
        assessment = agent.analyze_student(student)
        
        # Save risk assessment to Firestore
        assessment_dict = assessment.model_dump(by_alias=True)
        firestore_service.save_risk_assessment(assessment_dict)
        print(f"[Agent] Risk Level: {assessment.overallRiskLevel} | AI Reason: {assessment.aiSummaryReason[:60]}...")

    print("=== Seeding & Agent Pipeline Execution Completed Successfully ===")


if __name__ == "__main__":
    seed_database_and_run_agent()
