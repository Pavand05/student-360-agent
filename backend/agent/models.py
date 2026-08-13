from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Student(BaseModel):
    studentId: str = Field(..., description="Unique Student Identifier")
    name: str = Field(..., description="Student Full Name")
    class_name: str = Field(..., alias="class", description="Class / Grade e.g. 8-B")
    attendance: float = Field(..., description="Overall attendance percentage (0-100)")
    assignmentSubmission: float = Field(..., description="Daily assignment submission rate (0-100)")
    subjects: Dict[str, List[float]] = Field(
        ..., 
        description="Exam score history per subject, e.g. {'Maths': [82, 68, 51]}"
    )

    class Config:
        populate_by_name = True


class SubjectDecline(BaseModel):
    subject: str
    scores: List[float]
    firstScore: float
    latestScore: float
    declinePercent: float


class RiskEvidence(BaseModel):
    studentId: str
    name: str
    class_name: str = Field(..., alias="class")
    attendance: float
    assignmentSubmission: float
    academicDeclineDetected: bool
    subjectDeclines: List[SubjectDecline]
    worstSubject: Optional[str] = None
    attendanceRiskDetected: bool
    assignmentRiskDetected: bool
    overallRiskLevel: str  # HIGH, MEDIUM, LOW
    compositeRiskScore: float  # Numeric score for ranking (higher = higher priority)

    class Config:
        populate_by_name = True


class RiskAssessmentResult(BaseModel):
    studentId: str
    name: str
    class_name: str = Field(..., alias="class")
    overallRiskLevel: str
    compositeRiskScore: float
    evidence: RiskEvidence
    aiSummaryReason: str
    recommendedAction: str
    updatedAt: str

    class Config:
        populate_by_name = True


class ParentConversation(BaseModel):
    id: Optional[str] = None
    studentId: str
    studentName: Optional[str] = None
    discussion: str = Field(..., description="What was discussed with the parent")
    agreement: str = Field(..., description="What was agreed upon")
    followUpDate: str = Field(..., description="Follow-up target date (YYYY-MM-DD)")
    timestamp: str = Field(..., description="ISO timestamp of conversation record")
    loggedBy: str = Field("Principal", description="Role logging the conversation")
