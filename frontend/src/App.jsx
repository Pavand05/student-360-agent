import React, { useState, useEffect } from "react";
import { collection, onSnapshot, query, where, addDoc } from "firebase/firestore";
import { db } from "./firebase";
import { 
  AlertTriangle, MessageSquare, Calendar, Plus, X, UserPlus
} from "lucide-react";

export default function App() {
  const [students, setStudents] = useState([]);
  const [assessments, setAssessments] = useState({});
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  
  const [searchTerm, setSearchTerm] = useState("");
  const [classFilter, setClassFilter] = useState("ALL");

  // Form State for Parent Conversation Log
  const [discussion, setDiscussion] = useState("");
  const [agreement, setAgreement] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State for Adding New Student
  const [newId, setNewId] = useState("");
  const [newName, setNewName] = useState("");
  const [newClass, setNewClass] = useState("8-B");
  const [newAttendance, setNewAttendance] = useState("75");
  const [newSubmission, setNewSubmission] = useState("80");
  const [mathsMarks, setMathsMarks] = useState("82, 65, 48");
  const [scienceMarks, setScienceMarks] = useState("75, 72, 70");
  const [isCreatingStudent, setIsCreatingStudent] = useState(false);

  // 1. Real-time Firestore Listener for Students
  useEffect(() => {
    const unsubscribe = onSnapshot(collection(db, "students"), (snapshot) => {
      const studentData = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      setStudents(studentData);
    });
    return () => unsubscribe();
  }, []);

  // 2. Real-time Firestore Listener for Risk Assessments
  useEffect(() => {
    const unsubscribe = onSnapshot(collection(db, "risk_assessments"), (snapshot) => {
      const assessMap = {};
      snapshot.docs.forEach((doc) => {
        assessMap[doc.id] = doc.data();
      });
      setAssessments(assessMap);
    });
    return () => unsubscribe();
  }, []);

  // 3. Real-time Firestore Listener for Parent Conversations of Selected Student
  useEffect(() => {
    if (!selectedStudentId) {
      setConversations([]);
      return;
    }

    const q = query(
      collection(db, "parent_conversations"),
      where("studentId", "==", selectedStudentId)
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const convList = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      convList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setConversations(convList);
    });

    return () => unsubscribe();
  }, [selectedStudentId]);

  // Combine Student & Assessment for Prioritized Dashboard Table
  const combinedList = students.map((std) => {
    const assess = assessments[std.studentId] || {};
    return {
      ...std,
      riskLevel: assess.overallRiskLevel || "LOW",
      compositeScore: assess.compositeRiskScore || 0,
      aiReason: assess.aiSummaryReason || "No risk assessment computed yet.",
      action: assess.recommendedAction || "Monitor regular progress.",
      evidence: assess.evidence || {},
    };
  });

  // Sort by composite risk priority (HIGH first)
  combinedList.sort((a, b) => b.compositeScore - a.compositeScore);

  // Filtered List
  const filteredStudents = combinedList.filter((s) => {
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          s.studentId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesClass = classFilter === "ALL" || s.class === classFilter;
    return matchesSearch && matchesClass;
  });

  // Calculate High-level Dashboard Statistics
  const totalStudentsCount = students.length;
  const highRiskCount = combinedList.filter((s) => s.riskLevel === "HIGH").length;
  const mediumRiskCount = combinedList.filter((s) => s.riskLevel === "MEDIUM").length;

  const selectedStudent = combinedList.find((s) => s.studentId === selectedStudentId);

  // Handle Form Submission for Parent Conversation
  const handleSaveConversation = async (e) => {
    e.preventDefault();
    if (!discussion || !agreement || !followUpDate || !selectedStudentId) return;

    setIsSubmitting(true);
    try {
      await addDoc(collection(db, "parent_conversations"), {
        studentId: selectedStudentId,
        studentName: selectedStudent?.name,
        discussion,
        agreement,
        followUpDate,
        timestamp: new Date().toISOString(),
        loggedBy: "Principal"
      });

      setDiscussion("");
      setAgreement("");
      setFollowUpDate("");
    } catch (err) {
      console.error("Error saving parent conversation:", err);
      alert("Failed to save conversation. Check emulator connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Adding New Student via Backend Agent API
  const handleCreateStudent = async (e) => {
    e.preventDefault();
    if (!newId || !newName) return;

    setIsCreatingStudent(true);

    const parseScores = (str) => str.split(",").map((s) => parseFloat(s.trim()) || 0);

    const studentPayload = {
      studentId: newId.trim(),
      name: newName.trim(),
      class: newClass,
      attendance: parseFloat(newAttendance) || 0,
      assignmentSubmission: parseFloat(newSubmission) || 0,
      subjects: {
        Maths: parseScores(mathsMarks),
        Science: parseScores(scienceMarks),
      }
    };

    try {
      const res = await fetch("http://localhost:8000/api/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(studentPayload),
      });

      if (!res.ok) throw new Error("Failed to post student to backend");
      
      const data = await res.json();
      console.log("[Create Student Success]", data);

      // Reset Form & Close Modal
      setNewId("");
      setNewName("");
      setShowAddModal(false);
    } catch (err) {
      console.error("Error adding student:", err);
      alert("Make sure backend FastAPI server (python -m backend.main) is running on port 8000!");
    } finally {
      setIsCreatingStudent(false);
    }
  };

  return (
    <div className="container">
      {/* App Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">360</div>
          <div>
            <h1 className="app-title">Student 360 Performance Tracker</h1>
            <p className="app-subtitle">Principal Executive Dashboard & AI Risk Analysis</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <button 
            className="btn-primary" 
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            onClick={() => setShowAddModal(true)}
          >
            <UserPlus size={16} /> Add New Student
          </button>
          <div className="live-badge">
            <div className="pulse-dot"></div>
            Firestore Sync Active
          </div>
        </div>
      </header>

      {/* Overview Stat Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Enrolled Students</div>
          <div className="stat-value">{totalStudentsCount}</div>
        </div>
        <div className="stat-card" style={{ borderLeft: "4px solid #ef4444" }}>
          <div className="stat-label" style={{ color: "#fca5a5" }}>High Risk (Action Needed)</div>
          <div className="stat-value" style={{ color: "#ef4444" }}>{highRiskCount}</div>
        </div>
        <div className="stat-card" style={{ borderLeft: "4px solid #f59e0b" }}>
          <div className="stat-label" style={{ color: "#fcd34d" }}>Medium Risk (Watchlist)</div>
          <div className="stat-value" style={{ color: "#f59e0b" }}>{mediumRiskCount}</div>
        </div>
      </div>

      {/* Main Table Section */}
      <section className="section-card">
        <div className="table-controls">
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <input
              type="text"
              placeholder="Search by student name or ID..."
              className="search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
              className="select-filter"
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
            >
              <option value="ALL">All Classes</option>
              <option value="8-A">Class 8-A</option>
              <option value="8-B">Class 8-B</option>
            </select>
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-muted)" }}>
            Showing {filteredStudents.length} of {students.length} students
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="student-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Class</th>
                <th>Attendance</th>
                <th>Submissions</th>
                <th>Risk Priority</th>
                <th>AI Explanation (Plain-English Reason)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student) => (
                <tr key={student.studentId} onClick={() => setSelectedStudentId(student.studentId)}>
                  <td style={{ fontWeight: "600" }}>
                    <div>{student.name}</div>
                    <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>ID: {student.studentId}</div>
                  </td>
                  <td>{student.class}</td>
                  <td>
                    <span style={{ color: student.attendance < 80 ? "#fca5a5" : "#6ee7b7", fontWeight: "600" }}>
                      {student.attendance}%
                    </span>
                  </td>
                  <td>
                    <span style={{ color: student.assignmentSubmission < 80 ? "#fca5a5" : "#6ee7b7", fontWeight: "600" }}>
                      {student.assignmentSubmission}%
                    </span>
                  </td>
                  <td>
                    <span className={`risk-badge ${student.riskLevel}`}>
                      {student.riskLevel}
                    </span>
                  </td>
                  <td style={{ maxWidth: "340px", fontSize: "13px", color: "#cbd5e1", lineHeight: "1.4" }}>
                    {student.aiReason}
                  </td>
                  <td>
                    <button
                      className="btn-primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedStudentId(student.studentId);
                      }}
                    >
                      View 360°
                    </button>
                  </td>
                </tr>
              ))}
              {filteredStudents.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)" }}>
                    No students match your filter criteria. Select "All Classes" or clear search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Add Student Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" style={{ maxWidth: "550px" }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 style={{ fontSize: "20px", fontWeight: "700" }}>Add New Student & Run Risk Agent</h2>
              <button className="close-btn" onClick={() => setShowAddModal(false)}>&times;</button>
            </div>

            <form onSubmit={handleCreateStudent}>
              <div className="grid-two-col" style={{ gap: "12px" }}>
                <div className="form-group">
                  <label className="form-label">Student ID</label>
                  <input className="form-input" placeholder="e.g. S006" value={newId} onChange={(e) => setNewId(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Student Name</label>
                  <input className="form-input" placeholder="e.g. Rohan Mehta" value={newName} onChange={(e) => setNewName(e.target.value)} required />
                </div>
              </div>

              <div className="grid-two-col" style={{ gap: "12px" }}>
                <div className="form-group">
                  <label className="form-label">Class</label>
                  <select className="form-input" value={newClass} onChange={(e) => setNewClass(e.target.value)}>
                    <option value="8-A">Class 8-A</option>
                    <option value="8-B">Class 8-B</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Attendance %</label>
                  <input className="form-input" type="number" value={newAttendance} onChange={(e) => setNewAttendance(e.target.value)} required />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Assignment Submission Rate %</label>
                <input className="form-input" type="number" value={newSubmission} onChange={(e) => setNewSubmission(e.target.value)} required />
              </div>

              <div className="form-group">
                <label className="form-label">Maths Exam Marks (3 Exams, comma-separated)</label>
                <input className="form-input" placeholder="85, 68, 50" value={mathsMarks} onChange={(e) => setMathsMarks(e.target.value)} required />
              </div>

              <div className="form-group">
                <label className="form-label">Science Exam Marks (3 Exams, comma-separated)</label>
                <input className="form-input" placeholder="78, 74, 72" value={scienceMarks} onChange={(e) => setScienceMarks(e.target.value)} required />
              </div>

              <button type="submit" className="btn-primary" style={{ width: "100%", marginTop: "12px" }} disabled={isCreatingStudent}>
                {isCreatingStudent ? "Running Google ADK Agent..." : "Save & Analyze Student 360"}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Student 360 Drilldown Modal */}
      {selectedStudent && (
        <div className="modal-overlay" onClick={() => setSelectedStudentId(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2 style={{ fontSize: "22px", fontWeight: "700" }}>{selectedStudent.name} (360° View)</h2>
                <p style={{ fontSize: "14px", color: "var(--text-muted)" }}>
                  ID: {selectedStudent.studentId} | Class: {selectedStudent.class}
                </p>
              </div>
              <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                <span className={`risk-badge ${selectedStudent.riskLevel}`}>
                  {selectedStudent.riskLevel} RISK
                </span>
                <button className="close-btn" onClick={() => setSelectedStudentId(null)}>&times;</button>
              </div>
            </div>

            {/* AI Summary Banner */}
            <div className="card-box" style={{ background: "rgba(30, 41, 59, 0.9)", borderLeft: "4px solid #38bdf8" }}>
              <div className="card-title">
                <AlertTriangle size={18} color="#38bdf8" /> AI Student Risk Assessment (Gemini 2.5)
              </div>
              <p style={{ fontSize: "14px", lineHeight: "1.6", color: "#f8fafc", marginBottom: "12px" }}>
                {selectedStudent.aiReason}
              </p>
              <div style={{ background: "rgba(56, 189, 248, 0.1)", padding: "12px 16px", borderRadius: "8px", border: "1px solid rgba(56, 189, 248, 0.3)" }}>
                <strong style={{ color: "#38bdf8", fontSize: "13px" }}>RECOMMENDED PRINCIPAL ACTION:</strong>
                <p style={{ fontSize: "13px", color: "#e2e8f0", marginTop: "4px" }}>
                  {selectedStudent.action}
                </p>
              </div>
            </div>

            {/* Metrics & Subject Trends Grid */}
            <div className="grid-two-col">
              <div className="card-box">
                <div className="card-title">Disciplines & Attendance</div>
                <div style={{ marginBottom: "16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#cbd5e1" }}>
                    <span>Attendance Rate</span>
                    <span style={{ fontWeight: "700" }}>{selectedStudent.attendance}%</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${selectedStudent.attendance}%`,
                        backgroundColor: selectedStudent.attendance < 80 ? "#ef4444" : "#10b981"
                      }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#cbd5e1" }}>
                    <span>Daily Assignment Submissions</span>
                    <span style={{ fontWeight: "700" }}>{selectedStudent.assignmentSubmission}%</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${selectedStudent.assignmentSubmission}%`,
                        backgroundColor: selectedStudent.assignmentSubmission < 80 ? "#ef4444" : "#10b981"
                      }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="card-box">
                <div className="card-title">Subject Exam Trends (Last 3 Exams)</div>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {selectedStudent.subjects && Object.entries(selectedStudent.subjects).map(([subject, scores]) => {
                    const first = scores[0];
                    const latest = scores[scores.length - 1];
                    const isDecline = latest < first;
                    const diffPct = Math.round(((first - latest) / first) * 100);

                    return (
                      <div key={subject} style={{ background: "#0f172a", padding: "10px 14px", borderRadius: "8px", border: "1px solid #334155" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                          <span style={{ fontWeight: "600" }}>{subject}</span>
                          <span style={{ color: isDecline ? "#fca5a5" : "#6ee7b7", fontSize: "12px", fontWeight: "600" }}>
                            {isDecline ? `↓ Dropped ${diffPct}%` : `↑ Stable/Improved`}
                          </span>
                        </div>
                        <div style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                          Exams History: {scores.join(" → ")} (Latest: {latest}/100)
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Parent Conversation Log & Audit Trail */}
            <div className="grid-two-col">
              <div className="card-box">
                <div className="card-title"><MessageSquare size={16} /> Log Parent Conversation</div>
                <form onSubmit={handleSaveConversation}>
                  <div className="form-group">
                    <label className="form-label">What was discussed?</label>
                    <textarea
                      className="form-textarea"
                      placeholder="e.g. Discussed 37% drop in Maths exam scores..."
                      value={discussion}
                      onChange={(e) => setDiscussion(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">What was agreed?</label>
                    <textarea
                      className="form-textarea"
                      placeholder="e.g. Parent agreed to enrol in weekend tutoring..."
                      value={agreement}
                      onChange={(e) => setAgreement(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Follow-up Date</label>
                    <input
                      type="date"
                      className="form-input"
                      value={followUpDate}
                      onChange={(e) => setFollowUpDate(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn-primary" style={{ width: "100%", marginTop: "8px" }} disabled={isSubmitting}>
                    {isSubmitting ? "Saving to Firestore..." : "Save Conversation Audit Log"}
                  </button>
                </form>
              </div>

              <div className="card-box">
                <div className="card-title"><Calendar size={16} /> Audit Trail (Conversation History)</div>
                <div style={{ maxHeight: "300px", overflowY: "auto" }}>
                  {conversations.length === 0 ? (
                    <p style={{ fontSize: "13px", color: "var(--text-muted)", padding: "16px 0" }}>
                      No parent conversations logged yet for this student.
                    </p>
                  ) : (
                    conversations.map((conv) => (
                      <div key={conv.id} className="conversation-item">
                        <div className="conversation-date">
                          {new Date(conv.timestamp).toLocaleString()} | Logged by {conv.loggedBy || "Principal"}
                        </div>
                        <div style={{ fontSize: "13px", marginTop: "4px", color: "#f8fafc" }}>
                          <strong>Discussed:</strong> {conv.discussion}
                        </div>
                        <div style={{ fontSize: "13px", color: "#38bdf8", marginTop: "2px" }}>
                          <strong>Agreed:</strong> {conv.agreement}
                        </div>
                        <div style={{ fontSize: "12px", color: "#fcd34d", marginTop: "2px" }}>
                          Follow-up Target: {conv.followUpDate}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
