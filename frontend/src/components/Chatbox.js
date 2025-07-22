import React, { useState, useRef, useEffect } from 'react';
import './Chatbox.css';

function Chatbox() {
  const [messages, setMessages] = useState([]);
  const [age, setAge] = useState('');
  const [name, setName] = useState('');
  const [input, setInput] = useState('');
  const [testId, setTestId] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(null);
  const [suggestedOption, setSuggestedOption] = useState(null);
  const [started, setStarted] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleUserInput = async (e) => {
    e.preventDefault();
    const userMsg = { role: 'user', content: input };
    const updated = [...messages, userMsg];
    setMessages(updated);

    const res = await fetch('http://localhost:8000/chat/respond', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        age: parseInt(age),
        child_name: name,
        test_id: testId,
        question_index: questionIndex,
        chat_history: updated,
        suggested_option: suggestedOption || null
      })
    });
    const data = await res.json();
    setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
    if (!testId) setTestId(data.test_id);
    setQuestionIndex(data.question_index);
    setSuggestedOption(data.suggested_option || null);
    setInput('');
  };

  const startTest = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/chat/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ age: parseInt(age), child_name: name })
    });
    const data = await res.json();
    setStarted(true);
    setTestId(data.test_id);
    setQuestionIndex(data.question_index);
    setMessages([{ role: 'assistant', content: data.message }]);
  };

  return (
    <div className="chatbox-container">
      <h1>Strengths and Difficulties Questionnaire</h1>
      <div className="chatbox-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div className="chat-role">
              <strong>{msg.role === 'assistant' ? '🤖 Assistant' : '🧍 User'}</strong>
            </div>
            <div className="chat-content">{msg.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {!started ? (
        <form onSubmit={startTest} className="chatbox-form">
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Enter child name"
            className="chatbox-input"
            required
          />
          <input
            type="number"
            value={age}
            onChange={e => setAge(e.target.value)}
            placeholder="Enter age"
            className="chatbox-input"
            required
          />
          <button className="chatbox-submit" type="submit">Begin Test</button>
        </form>
      ) : (
        <form onSubmit={handleUserInput} className="chatbox-form">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your reply..."
            className="chatbox-input"
          />
          <button className="chatbox-submit" type="submit">Send</button>
        </form>
      )}
    </div>
  );
}

export default Chatbox;
