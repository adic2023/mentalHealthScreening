import React, { useState, useRef, useEffect } from 'react';
import './Chatbox.css';

function Chatbox({ childData, userRole, userEmail }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [testId, setTestId] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(null);
  const [suggestedOption, setSuggestedOption] = useState(null);
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Validate props on mount
  useEffect(() => {
    if (!childData || !userRole || !userEmail) {
      setMessages([{
        role: 'assistant',
        content: 'Error: Missing required information. Please restart the assessment.'
      }]);
    }
  }, [childData, userRole, userEmail]);

  const startTest = async () => {
    if (!childData || !userRole || !userEmail) {
      alert('Missing required information. Please restart the assessment.');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: childData.age,
          child_name: childData.name,
          child_id: childData.child_id,
          respondent_type: userRole === 'student' ? 'child' : userRole,
          email: userEmail
        })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to start test');
      }

      const data = await res.json();
      setMessages([{ role: 'assistant', content: data.message }]);
      setTestId(data.test_id);
      setQuestionIndex(data.question_index);
      setStarted(true);

    } catch (err) {
      console.error('Start test error:', err);
      setMessages([{
        role: 'assistant',
        content: `Error starting test: ${err.message}. Please try again.`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleUserInput = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          age: childData.age,
          child_name: childData.name,
          child_id: childData.child_id,
          test_id: testId,
          question_index: questionIndex,
          chat_history: updated,
          suggested_option: suggestedOption || null
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
      
      if (!testId) setTestId(data.test_id);
      setQuestionIndex(data.question_index);
      setSuggestedOption(data.suggested_option || null);

      // Check if test is completed
      if (data.completed) {
        setTestCompleted(true);
        setTimeout(() => {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: 'Test completed! Would you like to submit your responses? Type "submit" to submit or continue chatting.'
          }]);
        }, 1000);
      }

    } catch (err) {
      console.error('Chat response error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your response. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitTest = async () => {
    if (!testId) {
      alert('No test to submit');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/test/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_id: testId })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to submit test');
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Test submitted successfully! Thank you for completing the assessment. You can now close this window or return to your dashboard.'
      }]);

    } catch (err) {
      console.error('Submit test error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error submitting test: ${err.message}. Please try again.`
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Handle submit command in chat
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.role === 'user' && lastMessage.content.toLowerCase() === 'submit') {
      handleSubmitTest();
    }
  }, [messages]);

  // Show error if missing data
  if (!childData || !userRole || !userEmail) {
    return (
      <div className="chatbox-container">
        <div className="error-container">
          <h2>Error</h2>
          <p>Missing required information. Please restart the assessment.</p>
          <button onClick={() => window.history.back()}>Go Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="chatbox-container">
      <div className="chatbox-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <div className="chat-role">
              <strong>{msg.role === 'assistant' ? '🤖 Assistant' : '🧍 You'}</strong>
            </div>
            <div className="chat-content">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <div className="chat-role">
              <strong>🤖 Assistant</strong>
            </div>
            <div className="chat-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {!started ? (
        <div className="start-section">
          <div className="welcome-message">
            <h3>Ready to begin the SDQ assessment?</h3>
            <p>This will take approximately 5-10 minutes to complete.</p>
            {childData.message && (
              <p className="child-message">{childData.message}</p>
            )}
          </div>
          <button 
            className="start-btn" 
            onClick={startTest}
            disabled={loading}
          >
            {loading ? 'Starting...' : 'Begin Assessment'}
          </button>
        </div>
      ) : (
        <form onSubmit={handleUserInput} className="chatbox-form">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={loading ? "Processing..." : "Type your reply..."}
            className="chatbox-input"
            disabled={loading}
          />
          <button 
            className="chatbox-submit" 
            type="submit"
            disabled={loading || !input.trim()}
          >
            {loading ? '...' : 'Send'}
          </button>
        </form>
      )}
    </div>
  );
}

export default Chatbox;