import React, { useEffect, useState } from "react";
import axios from "axios";
import "./rev.css";

const CATEGORIES = {
  EMOTIONAL: [2, 7, 12, 15, 23],
  CONDUCT: [4, 6, 11, 17, 21],
  HYPERACTIVITY: [1, 9, 14, 20, 24],
  PEER: [5, 10, 13, 18, 22],
  PROSOCIAL: [0, 3, 8, 16, 19],
};

const Review = ({ testId }) => {
  const [responses, setResponses] = useState({});
  const [summary, setSummary] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [expandedQuestion, setExpandedQuestion] = useState(null);
  const [submitStatus, setSubmitStatus] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await axios.get(`http://localhost:8000/review/${testId}`);
        setResponses(res.data.responses || {});
        setSummary(res.data.summary || "");
      } catch (err) {
        console.error("Failed to fetch review data:", err);
      }
    }
    fetchData();
  }, [testId]);

  const handleConfirm = async () => {
    try {
      await axios.post(`http://localhost:8000/review/${testId}`, {
        summary,
      });
      setSubmitStatus("Summary confirmed and submitted.");
      setIsEditing(false);
    } catch (err) {
      console.error("Failed to submit summary:", err);
      setSubmitStatus("Error submitting summary.");
    }
  };

  const toggleExpand = (index) => {
    setExpandedQuestion((prev) => (prev === index ? null : index));
  };

  const getScoreClass = (value) => {
    if (value === 1) return "score-green";
    if (value === 2) return "score-yellow";
    if (value === 3) return "score-red";
    return "score-empty";
  };


  return (
    <div className="test-review-container">
      <div className="question-list">
        {Object.entries(CATEGORIES).map(([category, indices]) => (
          <div key={category} className="category-block">
            <h3>{category}</h3>
            <div className="category-header-row">
              <span style={{ width: "30px" }}></span>
              <span>Stu</span>
              <span>Par</span>
              <span>Tea</span>
              <span></span>
            </div>
            {indices.map((index) => (
              <div key={index} className="question-row">
                <div className="question-number">Q{index + 1}</div>
                <div className={`response-column ${getScoreClass(responses[index]?.student)}`}>
                  {responses[index]?.student ?? "-"}
                </div>
                <div className={`response-column ${getScoreClass(responses[index]?.parent)}`}>
                  {responses[index]?.parent ?? "-"}
                </div>
                <div className={`response-column ${getScoreClass(responses[index]?.teacher)}`}>
                  {responses[index]?.teacher ?? "-"}
                </div>

                <button className="expand-btn" onClick={() => toggleExpand(index)}>
                  {expandedQuestion === index ? "Hide" : "View"}
                </button>
                {expandedQuestion === index && responses[index] && (
                  <div className="response-detail-panel">
                    <p><strong>Student's Answer:</strong> {responses[index]?.answer ?? "No answer available."}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="summary-box">
        <h3>Summary</h3>
        {isEditing ? (
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
          />
        ) : (
          <p>{summary}</p>
        )}
        <div className="summary-actions">
          <button onClick={() => setIsEditing((prev) => !prev)}>
            {isEditing ? "Cancel" : "Edit"}
          </button>
          {isEditing && <button onClick={handleConfirm}>Confirm</button>}
        </div>
        {submitStatus && <div className="submit-status">{submitStatus}</div>}
      </div>
    </div>
  );
};

export default Review;
