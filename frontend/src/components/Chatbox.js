// import React, { useState } from 'react';
// import './Chatbox.css'; 

// function Chatbox() {
//   const [formData, setFormData] = useState({ response: '' });
//   const [chatLog, setChatLog] = useState([]); // stores messages

//   const handleChange = (e) => {
//     setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     const res = await fetch('http://localhost:8000/submit', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(formData),
//     });

//     const data = await res.json();

//     const newMessages = [
//       { role: 'user', content: formData.response },
//       { role: 'llm', content: data.llm_reply },
//       { role: 'preset', content: data.preset_reply }
//     ];

//     setChatLog(prev => [...prev, ...newMessages]);
//     setFormData({ response: '' });
//   };

//   return (
//     <div className="chatbox-container">
//       <div className="chatbox-history">
//         {chatLog.map((entry, index) => (
//           <div key={index} className={`chat-message ${entry.role}`}>
//             <strong>{entry.role === 'user' ? 'You' : entry.role === 'llm' ? 'LLM' : 'System'}:</strong> {entry.content}
//           </div>
//         ))}
//       </div>

//       <form onSubmit={handleSubmit} className="chatbox-form">
//         <input
//           name="response"
//           placeholder="Type your response..."
//           value={formData.response}
//           onChange={handleChange}
//         /><br />
//         <button type="submit">Submit</button>
//       </form>
//     </div>
//   );
// }

// export default Chatbox;


import React, { useState, useRef, useEffect } from 'react';
import './Chatbox.css';

function Chatbox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const endRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);

    const res = await fetch('http://localhost:8000/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response: input }),
    });

    const data = await res.json();

    const botReply = { role: 'assistant', content: data.llm_reply };
    const presetReply = { role: 'system', content: data.preset_reply };

    setMessages(prev => [...prev, botReply, presetReply]);
    setInput('');
  };

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

return (
  <div className="chatbox-container">
    <div className="chatbox-messages">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`chat-message ${msg.role}`}
        >
          <div className="chat-role">{msg.role}</div>
          <div className="chat-content">{msg.content}</div>
        </div>
      ))}
      <div ref={endRef} />
    </div>

    <form onSubmit={handleSubmit} className="chatbox-form">
      <input
        className="chatbox-input"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button type="submit" className="chatbox-submit">Send</button>
    </form>
  </div>
);
}

export default Chatbox;
