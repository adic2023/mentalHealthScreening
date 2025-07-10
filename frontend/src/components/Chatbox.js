import React, { useState } from 'react';
import './Chatbox.css';

function Chatbox() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Welcome to the screening test. Please enter the child’s age to begin.' }
  ]);

  const [age, setAge] = useState('');
  const [input, setInput] = useState('');
  const [testId, setTestId] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(-1);
  const [suggestedOption, setSuggestedOption] = useState(null);

  // Step 1: Start the screening by sending age
  const startTest = async () => {
    try {
      const res = await fetch('http://localhost:8000/chat/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: parseInt(age) }),
      });

      const data = await res.json();
      setTestId(data.test_id);
      setQuestionIndex(data.question_index);

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.message }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'system', content: 'Failed to start test. Try again.' }
      ]);
    }
  };

  // Step 2: Send user's freeform response to current question
  const handleSubmit = async (e) => {
    e.preventDefault();

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);

    try {
      const res = await fetch('http://localhost:8000/chat/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: parseInt(age),
          question_index: questionIndex,
          chat_history: [...messages, userMsg],
        }),
      });

      const data = await res.json();

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.message }
      ]);
      setSuggestedOption(data.suggested_option);
      setInput('');
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'system', content: 'Error during response. Try again.' }
      ]);
    }
  };

  // Step 3: User confirms suggested option
  const confirmOption = async () => {
    try {
      const res = await fetch('http://localhost:8000/chat/confirm-option', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_id: testId,
          age: parseInt(age),
          question_index: questionIndex,
          selected_option: suggestedOption,
        }),
      });

      const data = await res.json();

      setMessages(prev => [
        ...prev,
        { role: 'system', content: `Confirmed: "${suggestedOption}"` },
        { role: 'assistant', content: data.message }
      ]);
      setSuggestedOption(null);
      setQuestionIndex(data.question_index);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'system', content: 'Error confirming option. Try again.' }
      ]);
    }
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div className="chat-role">{msg.role}</div>
            <div className="chat-content">{msg.content}</div>
          </div>
        ))}
      </div>

      {/* AGE FORM — only shown before test starts */}
      {!testId && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            startTest();
          }}
          className="chatbox-form"
        >
          <input
            className="chatbox-input"
            type="number"
            placeholder="Enter child's age..."
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />
          <button className="chatbox-submit" type="submit">Start</button>
        </form>
      )}

      {/* CONFIRMATION UI — shown after LLM suggests an answer */}
      {testId && suggestedOption && (
        <div className="chatbox-form">
          <p className="chatbox-input" style={{ background: '#fff9c4', flex: 1 }}>
            LLM suggests: "<strong>{suggestedOption}</strong>". Confirm?
          </p>
          <button className="chatbox-submit" onClick={confirmOption}>Yes</button>
          <button
            className="chatbox-submit"
            onClick={() => setSuggestedOption(null)}
            style={{ backgroundColor: '#f87171' }}
          >
            No
          </button>
        </div>
      )}

      {/* MAIN TEXT INPUT — only shown after test starts */}
      {testId && !suggestedOption && (
        <form onSubmit={handleSubmit} className="chatbox-form">
          <input
            className="chatbox-input"
            placeholder="Type your response..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="chatbox-submit" type="submit">Send</button>
        </form>
      )}
    </div>
  );
}

export default Chatbox;
