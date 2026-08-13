# Student 360 Performance Tracker Agent

An AI-powered Student 360 Performance Tracker Agent built for school principals using **Google ADK 2.6.3**, **Gemini 2.5 Flash**, **Firestore**, and **React**.

---

## 1. Problem Statement

School principals struggle to track student performance and take timely action due to scattered data:
- Exam marks sit in one spreadsheet, daily assignment submissions in another, and attendance in a third.
- Principals cannot easily answer critical questions like:
  - *"Which students have declined across the last three exams?"*
  - *"Which subject is weakest in Class 8-B?"*
  - *"Which children are at risk because of attendance versus academic ability?"*
- By the time problems are noticed, the term is over.
- Furthermore, when principals call parents, conversations are unrecorded, making audit, follow-up, and progress tracking impossible.

---

## 2. Solution Overview

The **Student 360 Performance Tracker Agent**:
1. **Ingests & Unifies Scattered Data**: Combines exam score series, attendance rates, and daily assignment submission discipline into a unified 360-degree profile.
2. **Deterministic Risk Calculations**: Computes exact percentage drops, subject-wise declines, and attendance/submission threshold violations without LLM math hallucination.
3. **AI Plain-English Risk Explanations**: Uses **Google ADK 2.6.3** and **Gemini 2.5 Flash** to translate facts into empathetic, parent-ready summaries and recommended actions.
4. **Prioritized Executive Dashboard**: Renders a React dashboard sorting high-risk students at the top for immediate principal action.
5. **Parent Conversation Audit Trail**: Provides a form to record discussions, commitments, and follow-up dates, persisting a timestamped audit trail in Firestore with real-time UI updates via `onSnapshot`.

---

## 3. Architecture & Workflow

```text
Principal
   ↓
React Dashboard (Vite + Firebase Web SDK)
   ↓ (onSnapshot Real-Time Listener)
Firestore Database (students, risk_assessments, parent_conversations)
   ↑ (Persist Assessment Results)
Python / Google ADK Agent Pipeline
   ├── 1. Deterministic Risk Analyzer (risk_analyzer.py)
   ├── 2. Prompt Formatter (prompts.py)
   └── 3. Vertex AI Gemini 2.5 Flash (Generates plain-English summary & recommended action)
```

---

## 4. Technology Stack & Framework Justification

- **Language**: Python 3.11 (Backend), JavaScript / React (Frontend).
- **Agent Framework**: **Google ADK 2.6.3** (`google.adk.agents.LlmAgent`, `Runner`).
  - *Justification*: ADK 2.6.3 provides clean agent composition primitives (`LlmAgent`, `SequentialAgent`) and enterprise integration with Google Cloud Vertex AI.
- **LLM Engine**: **Gemini 2.5 Flash** (`google-genai` via Vertex AI mode).
- **Persistence Layer**: **Firestore** (Google Cloud Firestore & Firebase Firestore Emulator supported).
- **Frontend Dashboard**: React + Vite + Firebase Web SDK (`onSnapshot` real-time listeners) + Lucide Icons.

---

## 5. Data Model & Firestore Schemas

### Collection: `students`
```json
{
  "studentId": "S001",
  "name": "Rahul Sharma",
  "class": "8-B",
  "attendance": 78.0,
  "assignmentSubmission": 85.0,
  "subjects": {
    "Maths": [82.0, 68.0, 51.0],
    "Science": [75.0, 73.0, 71.0],
    "English": [80.0, 78.0, 76.0]
  }
}
```

### Collection: `risk_assessments`
```json
{
  "studentId": "S001",
  "name": "Rahul Sharma",
  "class": "8-B",
  "overallRiskLevel": "HIGH",
  "compositeRiskScore": 45.2,
  "evidence": {
    "academicDeclineDetected": true,
    "worstSubject": "Maths",
    "subjectDeclines": [
      { "subject": "Maths", "firstScore": 82.0, "latestScore": 51.0, "declinePercent": 37.8 }
    ],
    "attendanceRiskDetected": true,
    "assignmentRiskDetected": false
  },
  "aiSummaryReason": "Rahul is at HIGH risk due to a severe 37.8% drop in Maths exam scores (82 to 51) alongside low attendance at 78%.",
  "recommendedAction": "Schedule weekly remedial math sessions and set up a daily attendance check-in with parents.",
  "updatedAt": "2026-08-13T12:00:00Z"
}
```

### Collection: `parent_conversations`
```json
{
  "id": "conv_101",
  "studentId": "S001",
  "studentName": "Rahul Sharma",
  "discussion": "Discussed 37% drop in Maths exam scores and low attendance.",
  "agreement": "Parent agreed to enrol Rahul in weekend math tutoring and sign daily homework log.",
  "followUpDate": "2026-08-25",
  "timestamp": "2026-08-13T12:30:00Z",
  "loggedBy": "Principal"
}
```

---

## 6. Deterministic Risk Threshold Logic

To ensure absolute accuracy without LLM calculation errors, raw metrics are processed by `backend/agent/risk_analyzer.py`:

- **Academic Decline**: Flagged if exam drop $\ge 12\%$ from first exam, or if latest score $< 55/100$.
- **Attendance Risk**: Flagged if attendance $< 85\%$ (Medium) or $< 80\%$ (High).
- **Assignment Discipline Risk**: Flagged if submission rate $< 88\%$ (Medium) or $< 80\%$ (High).
- **Composite Priority Score**:
  $$\text{Composite Score} = (\text{Max Decline } \times 0.8) + \text{Failing Penalty} + (90 - \text{Attendance}) \times 1.5 + (90 - \text{Submission}) \times 1.0$$
- **Overall Category**: `HIGH` if composite score $\ge 40$ or multi-factor drop; `MEDIUM` if single factor drop; `LOW` otherwise.

---

## 7. Prompts Used

Located in `backend/agent/prompts.py`:

```text
You are an AI Student Performance Assistant working directly with a School Principal.
Translate calculated, deterministic student metrics into clear, professional, parent-friendly summaries and practical action plans.

CRITICAL RULES:
1. STRICT ADHERENCE TO FACTS: Use ONLY provided metrics. Do NOT invent test scores or attendance numbers.
2. PLAIN-ENGLISH REASONING: Clear, non-technical explanation suitable for reading aloud to a parent.
3. TREND IDENTIFICATION: Highlight trends across exam scores, daily assignment submissions, and attendance.
4. PRACTICAL RECOMMENDATION: Exactly ONE concrete recommendation for the principal to discuss with the parent.
```

---

## 8. Setup & Running Instructions

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm
- Google Cloud authenticated credentials (`gcloud auth login`) or Vertex AI access.

### 1. Backend Setup & Seeding
```powershell
# Install Python dependencies
pip install -r backend/requirements.txt

# Run backend tests
npx -y firebase-tools emulators:exec --only firestore "python -m unittest backend/test_backend.py"

# Seed Database & Run ADK Agent Analysis
npx -y firebase-tools emulators:exec --only firestore "python -m backend.seed_data"
```

### 2. Launch FastAPI Backend Server
```powershell
python -m backend.main
```

### 3. Launch React Dashboard
```powershell
cd frontend
npm install
npm run dev
```
Open browser at `http://localhost:5173`.

---

## 9. Demo Walkthrough

1. **Open Dashboard**: Renders prioritized student list with HIGH risk students (`Rahul Sharma`, `Karan Gupta`) at the top.
2. **Review AI Reasons**: View plain-English explanations highlighting exact exam drops and attendance facts.
3. **Drill Down into 360° View**: Click **View 360°** on Rahul Sharma (`S001`) to inspect score trends, attendance progress bars, and Gemini risk analysis.
4. **Log Parent Conversation**:
   - Fill in:
     - Discussion: *"Met with parents to discuss 37.8% drop in Maths (82 to 51) and 78% attendance."*
     - Agreement: *"Parent agreed to weekend math tutoring and daily homework signature."*
     - Follow-up Date: *"2026-08-25"*
   - Click **Save Conversation Audit Log**.
5. **Verify Real-Time Audit Trail**: The entry immediately appears under **Audit Trail (Conversation History)** with a timestamp via Firestore `onSnapshot`.

---

## 10. Assumptions & Limitations

### Assumptions
- Synthetic student data accurately represents real school data structures.
- Principal user role is pre-authenticated for prototype testing.

### Limitations
- GCP project `intern-bnmit-july-2026` lacks Cloud Firestore database creation permissions; prototype runs seamlessly against local Firestore Emulator or Cloud Firestore when provisioned.
- Production deployment would include OAuth2 principal login & role-based access control.

---

## 11. Future Improvements

1. **WhatsApp / SMS Parent Notifications**: Automatic summary dispatch to parents after logged conversations.
2. **Predictive Subject Risk Models**: Machine learning forecasting of end-of-term marks based on mid-term trends.
3. **Multi-School Benchmarking**: Aggregate school-wide subject analytics across grades.
