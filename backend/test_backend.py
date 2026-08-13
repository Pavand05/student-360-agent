import os
import unittest
from backend.agent.models import Student
from backend.agent.risk_analyzer import calculate_student_risk
from backend.agent.agent import Student360Agent
from backend.firestore_service import FirestoreService

class TestStudent360Backend(unittest.TestCase):

    def setUp(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
        self.high_risk_student = Student(
            studentId="TEST_S001",
            name="Test High Risk Rahul",
            class_name="8-B",
            attendance=75.0,
            assignmentSubmission=78.0,
            subjects={
                "Maths": [85.0, 65.0, 48.0],
                "Science": [70.0, 68.0, 64.0]
            }
        )

    def test_01_deterministic_risk_logic(self):
        evidence = calculate_student_risk(self.high_risk_student)
        self.assertEqual(evidence.overallRiskLevel, "HIGH")
        self.assertTrue(evidence.academicDeclineDetected)
        self.assertTrue(evidence.attendanceRiskDetected)
        self.assertEqual(evidence.worstSubject, "Maths")
        print("\n[OK] Test 1 Passed: Deterministic risk logic accurately flagged HIGH risk student")

    def test_02_adk_agent_pipeline(self):
        agent = Student360Agent()
        result = agent.analyze_student(self.high_risk_student)
        self.assertEqual(result.overallRiskLevel, "HIGH")
        self.assertIsNotNone(result.aiSummaryReason)
        self.assertIsNotNone(result.recommendedAction)
        print("\n[OK] Test 2 Passed: ADK Agent pipeline produced valid result with summary and action")

    def test_03_firestore_persistence(self):
        service = FirestoreService()

        # Save student
        student_id = service.save_student(self.high_risk_student.model_dump(by_alias=True))
        self.assertEqual(student_id, "TEST_S001")

        # Fetch student
        retrieved_student = service.get_student("TEST_S001")
        self.assertIsNotNone(retrieved_student)
        self.assertEqual(retrieved_student["name"], "Test High Risk Rahul")

        # Save & Fetch parent conversation
        conv_id = service.save_parent_conversation({
            "studentId": "TEST_S001",
            "discussion": "Discussed math performance drop",
            "agreement": "Agreed on math tutor",
            "followUpDate": "2026-08-25",
            "timestamp": "2026-08-13T12:00:00Z"
        })
        self.assertIsNotNone(conv_id)

        convs = service.get_parent_conversations("TEST_S001")
        self.assertTrue(len(convs) > 0)
        self.assertEqual(convs[0]["agreement"], "Agreed on math tutor")
        print("\n[OK] Test 3 Passed: Firestore read/write operations verified successfully")


if __name__ == "__main__":
    unittest.main()
