from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent.models import Student, ParentConversation
from backend.agent.agent import Student360Agent
from backend.firestore_service import FirestoreService

app = FastAPI(
    title="Student 360 Performance Tracker API",
    description="Backend API powering the Student 360 Agent and Principal Dashboard",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

firestore_service = FirestoreService()
agent = Student360Agent()


class ConversationCreateRequest(BaseModel):
    discussion: str
    agreement: str
    followUpDate: str


@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Student 360 Performance Tracker Agent",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/students")
def get_all_students():
    return firestore_service.get_students()


@app.get("/api/risk-assessments")
def get_all_risk_assessments():
    return firestore_service.get_risk_assessments()


@app.get("/api/students/{student_id}/360")
def get_student_360(student_id: str):
    student = firestore_service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    assessment = firestore_service.get_risk_assessment(student_id)
    conversations = firestore_service.get_parent_conversations(student_id)

    return {
        "student": student,
        "assessment": assessment,
        "conversations": conversations
    }


@app.post("/api/students/{student_id}/conversations")
def create_parent_conversation(student_id: str, req: ConversationCreateRequest):
    student = firestore_service.get_student(student_id)
    student_name = student.get("name") if student else None

    conv = ParentConversation(
        studentId=student_id,
        studentName=student_name,
        discussion=req.discussion,
        agreement=req.agreement,
        followUpDate=req.followUpDate,
        timestamp=datetime.now().isoformat(),
        loggedBy="Principal"
    )

    conv_dict = conv.model_dump(by_alias=True)
    conv_id = firestore_service.save_parent_conversation(conv_dict)
    conv_dict["id"] = conv_id
    return {"status": "success", "conversation": conv_dict}


@app.post("/api/analyze-all")
def trigger_agent_analysis():
    students_raw = firestore_service.get_students()
    results = []

    for raw in students_raw:
        student = Student.model_validate(raw)
        assessment = agent.analyze_student(student)
        firestore_service.save_risk_assessment(assessment.model_dump(by_alias=True))
        results.append(assessment)

    return {
        "status": "completed",
        "processed_students": len(results),
        "assessments": [r.model_dump(by_alias=True) for r in results]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
