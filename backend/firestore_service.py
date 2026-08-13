import os
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

class FirestoreService:
    """
    Firestore Data Access Service for Student 360 Agent.
    Supports both Google Cloud Firestore and local Firebase Firestore Emulator.
    """

    def __init__(self, project_id: str = "intern-bnmit-july-2026"):
        self.project_id = project_id
        
        # If running locally and GCP cloud Firestore isn't provisioned,
        # default to local emulator port 8080 if FIRESTORE_EMULATOR_HOST is set or requested.
        if "FIRESTORE_EMULATOR_HOST" not in os.environ:
            os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"

        try:
            self.db = firestore.Client(project=self.project_id)
        except Exception as e:
            print(f"[FirestoreService] Client initialization note: {e}")
            self.db = firestore.Client(project=self.project_id)

    # --- Student Operations ---
    def save_student(self, student_data: Dict[str, Any]) -> str:
        doc_id = student_data["studentId"]
        self.db.collection("students").document(doc_id).set(student_data)
        return doc_id

    def get_students(self) -> List[Dict[str, Any]]:
        docs = self.db.collection("students").stream()
        return [doc.to_dict() for doc in docs]

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection("students").document(student_id).get()
        return doc.to_dict() if doc.exists else None

    # --- Risk Assessment Operations ---
    def save_risk_assessment(self, assessment_data: Dict[str, Any]) -> str:
        doc_id = assessment_data["studentId"]
        self.db.collection("risk_assessments").document(doc_id).set(assessment_data)
        return doc_id

    def get_risk_assessments(self) -> List[Dict[str, Any]]:
        docs = self.db.collection("risk_assessments").stream()
        results = [doc.to_dict() for doc in docs]
        # Sort by compositeRiskScore descending (high risk priority first)
        results.sort(key=lambda x: x.get("compositeRiskScore", 0), reverse=True)
        return results

    def get_risk_assessment(self, student_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection("risk_assessments").document(student_id).get()
        return doc.to_dict() if doc.exists else None

    # --- Parent Conversation Audit Trail Operations ---
    def save_parent_conversation(self, conversation_data: Dict[str, Any]) -> str:
        doc_ref = self.db.collection("parent_conversations").document()
        conversation_data["id"] = doc_ref.id
        doc_ref.set(conversation_data)
        return doc_ref.id

    def get_parent_conversations(self, student_id: str) -> List[Dict[str, Any]]:
        docs = self.db.collection("parent_conversations")\
            .where(filter=FieldFilter("studentId", "==", student_id))\
            .stream()
        conversations = [doc.to_dict() for doc in docs]
        # Sort by timestamp descending
        conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return conversations
