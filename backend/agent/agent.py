import json
import os
from datetime import datetime
from google import genai
from google.adk.agents import LlmAgent

from backend.agent.models import Student, RiskAssessmentResult
from backend.agent.risk_analyzer import calculate_student_risk
from backend.agent.prompts import STUDENT_RISK_EXPLANATION_PROMPT


class Student360Agent:
    """
    Student 360 Performance Tracker Agent built using Google ADK 2.6.3 architecture principles.
    
    Architecture Justification:
    - Combines deterministic mathematical processing (risk_analyzer.py) with Gemini 2.5 LLM reasoning.
    - Mathematical facts (exact percentages, declines, thresholds) are calculated in Python first.
    - ADK LlmAgent / Gemini client converts structured facts into empathetic, parent-friendly explanations.
    """

    def __init__(self, project_id: str = "intern-bnmit-july-2026", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize Google GenAI client (Vertex AI mode)
        try:
            self.genai_client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
        except Exception as e:
            print(f"[Student360Agent] Warning initializing Vertex AI Client: {e}")
            self.genai_client = None

        # Google ADK LlmAgent representation
        self.adk_agent = LlmAgent(
            name="student_360_risk_explainer",
            model="gemini-2.5-flash",
            instruction="You translate deterministic student risk metrics into clear, parent-ready principal summaries."
        )

    def analyze_student(self, student: Student) -> RiskAssessmentResult:
        """
        Executes the full Agent Pipeline:
        1. Deterministic calculation of risk evidence (scores, declines, attendance thresholds).
        2. Prompt formatting with structured factual data.
        3. Gemini 2.5 Flash execution via Vertex AI / ADK.
        4. Structured RiskAssessmentResult generation.
        """
        # Step 1: Deterministic Risk Engine
        evidence = calculate_student_risk(student)

        # Step 2: Format facts for Gemini Prompt
        subject_trends_json = json.dumps(student.subjects)
        
        risk_factors = []
        if evidence.academicDeclineDetected:
            for sd in evidence.subjectDeclines:
                risk_factors.append(f"{sd.subject} dropped by {sd.declinePercent}% (from {sd.firstScore} to {sd.latestScore})")
        if evidence.attendanceRiskDetected:
            risk_factors.append(f"Attendance is low at {evidence.attendance}%")
        if evidence.assignmentRiskDetected:
            risk_factors.append(f"Assignment submission rate is low at {evidence.assignmentSubmission}%")
        if not risk_factors:
            risk_factors.append("No critical risk factors detected; student is performing well.")

        risk_factors_text = "; ".join(risk_factors)

        prompt_input = STUDENT_RISK_EXPLANATION_PROMPT.format(
            name=student.name,
            class_name=student.class_name,
            overall_risk_level=evidence.overallRiskLevel,
            attendance=evidence.attendance,
            assignment_submission=evidence.assignmentSubmission,
            subject_trends_json=subject_trends_json,
            risk_factors_text=risk_factors_text
        )

        # Step 3: LLM Generation
        ai_summary = ""
        recommended_action = ""

        if self.genai_client:
            try:
                response = self.genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_input
                )
                
                # Parse JSON output from Gemini
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()

                parsed = json.loads(raw_text)
                ai_summary = parsed.get("aiSummaryReason", "")
                recommended_action = parsed.get("recommendedAction", "")
            except Exception as e:
                print(f"[Student360Agent] Gemini generation fallback for {student.name}: {e}")
                # Deterministic fallback if Gemini call encounters quota/network error
                ai_summary = self._generate_fallback_summary(student, evidence, risk_factors_text)
                recommended_action = self._generate_fallback_action(evidence)
        else:
            ai_summary = self._generate_fallback_summary(student, evidence, risk_factors_text)
            recommended_action = self._generate_fallback_action(evidence)

        # Step 4: Construct Result
        return RiskAssessmentResult(
            studentId=student.studentId,
            name=student.name,
            class_name=student.class_name,
            overallRiskLevel=evidence.overallRiskLevel,
            compositeRiskScore=evidence.compositeRiskScore,
            evidence=evidence,
            aiSummaryReason=ai_summary,
            recommendedAction=recommended_action,
            updatedAt=datetime.now().isoformat()
        )

    def _generate_fallback_summary(self, student: Student, evidence, risk_factors_text: str) -> str:
        if evidence.overallRiskLevel == "HIGH":
            return f"{student.name} is flagged for HIGH attention due to: {risk_factors_text}. Urgent principal-parent intervention recommended."
        elif evidence.overallRiskLevel == "MEDIUM":
            return f"{student.name} shows moderate risk indicators: {risk_factors_text}. Regular monitoring advised."
        return f"{student.name} is performing consistently well with high attendance ({student.attendance}%) and stable assignment submissions."

    def _generate_fallback_action(self, evidence) -> str:
        if evidence.academicDeclineDetected and evidence.worstSubject:
            return f"Schedule subject-specific remedial sessions for {evidence.worstSubject} and review weekly exam progress with parents."
        elif evidence.attendanceRiskDetected:
            return "Discuss attendance hurdles with parents to create a daily school arrival check-in system."
        elif evidence.assignmentRiskDetected:
            return "Implement a daily assignment tracker signed by parents every evening."
        return "Maintain current positive study habits and acknowledge academic performance."
