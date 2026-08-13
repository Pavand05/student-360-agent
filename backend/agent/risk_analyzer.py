from typing import List
from backend.agent.models import Student, RiskEvidence, SubjectDecline


def calculate_student_risk(student: Student) -> RiskEvidence:
    """
    Deterministic prototype risk calculation engine.
    Calculates exact mathematical facts:
    1. Per-subject exam trends (first vs latest score, decline percentage).
    2. Attendance threshold violations (<80% High, <85% Medium).
    3. Assignment submission threshold violations (<80% High, <88% Medium).
    4. Overall risk categorization (HIGH, MEDIUM, LOW) and numerical priority score.
    """
    subject_declines: List[SubjectDecline] = []
    max_decline_percent = 0.0
    worst_subject = None

    for subject, scores in student.subjects.items():
        if len(scores) >= 2:
            first_score = scores[0]
            latest_score = scores[-1]
            if first_score > 0:
                diff = first_score - latest_score
                decline_pct = round((diff / first_score) * 100.0, 1)
                
                # Check for academic decline (decline >= 10% or latest score < 60)
                if decline_pct > 0 or latest_score < 60:
                    sub_decline = SubjectDecline(
                        subject=subject,
                        scores=scores,
                        firstScore=first_score,
                        latestScore=latest_score,
                        declinePercent=decline_pct
                    )
                    subject_declines.append(sub_decline)

                    if decline_pct > max_decline_percent:
                        max_decline_percent = decline_pct
                        worst_subject = subject

    academic_decline_detected = max_decline_percent >= 12.0 or any(sd.latestScore < 55 for sd in subject_declines)

    # Threshold rules
    attendance_risk_detected = student.attendance < 85.0
    attendance_high_risk = student.attendance < 80.0

    assignment_risk_detected = student.assignmentSubmission < 88.0
    assignment_high_risk = student.assignmentSubmission < 80.0

    # Composite risk score calculation (0 to 100)
    # Higher score = higher urgency for principal
    academic_penalty = max(0.0, max_decline_percent) * 0.8
    if any(s[-1] < 55 for s in student.subjects.values()):
        academic_penalty += 20.0  # extra penalty for failing scores

    attendance_penalty = max(0.0, (90.0 - student.attendance)) * 1.5
    assignment_penalty = max(0.0, (90.0 - student.assignmentSubmission)) * 1.0

    composite_score = round(academic_penalty + attendance_penalty + assignment_penalty, 1)

    # Determine Overall Risk Level
    if (academic_decline_detected and (attendance_high_risk or assignment_high_risk)) or \
       max_decline_percent >= 25.0 or student.attendance < 75.0 or composite_score >= 40.0:
        overall_risk = "HIGH"
    elif academic_decline_detected or attendance_risk_detected or assignment_risk_detected or composite_score >= 15.0:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return RiskEvidence(
        studentId=student.studentId,
        name=student.name,
        class_name=student.class_name,
        attendance=student.attendance,
        assignmentSubmission=student.assignmentSubmission,
        academicDeclineDetected=academic_decline_detected,
        subjectDeclines=subject_declines,
        worstSubject=worst_subject,
        attendanceRiskDetected=attendance_risk_detected,
        assignmentRiskDetected=assignment_risk_detected,
        overallRiskLevel=overall_risk,
        compositeRiskScore=composite_score
    )
