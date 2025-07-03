import React, { useState } from 'react';
import './Chatbox.css'; 

function Chatbox() {
  const [formData, setFormData] = useState({ response: '' });
  const [chatLog, setChatLog] = useState([]); // stores messages

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch('http://localhost:8000/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    const data = await res.json();

    const newMessages = [
      { role: 'user', content: formData.response },
      { role: 'llm', content: data.llm_reply },
      { role: 'preset', content: data.preset_reply }
    ];

    setChatLog(prev => [...prev, ...newMessages]);
    setFormData({ response: '' });
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-history">
        {chatLog.map((entry, index) => (
          <div key={index} className={`chat-message ${entry.role}`}>
            <strong>{entry.role === 'user' ? 'You' : entry.role === 'llm' ? 'LLM' : 'System'}:</strong> {entry.content}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="chatbox-form">
        <input
          name="response"
          placeholder="Type your response..."
          value={formData.response}
          onChange={handleChange}
        /><br />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default Chatbox;
