import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { 
      role: "assistant", 
      content: "Hi! 👋 I'm PropAssist, your personal property advisor.\n\nLooking to **buy, rent or invest** in India? I'll help you find the perfect property in just a few questions!", 
      actions: [] 
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const parseActions = (content) => {
    const match = content.match(/\[ACTIONS:(.*?)\]/);
    if (match) {
      const actions = match[1].split(',').map(a => a.trim());
      const cleanContent = content.replace(/\[ACTIONS:.*?\]/, '').trim();
      return { cleanContent, actions };
    }
    return { cleanContent: content, actions: [] };
  };

  const sendMessage = async (messageText) => {
    const userMessage = messageText || input.trim();
    if (!userMessage || loading) return;
    setInput("");

    setMessages(prev => [...prev, { role: "user", content: userMessage, actions: [] }]);
    setLoading(true);
    setMessages(prev => [...prev, { role: "assistant", content: "", actions: [] }]);

    try {
      const response = await fetch("https://propertyassist-3aws.onrender.com/api/chat/stream/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage, session_id: sessionId })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                fullContent += data.chunk;
                const { cleanContent } = parseActions(fullContent);
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    role: "assistant",
                    content: cleanContent,
                    actions: []
                  };
                  return updated;
                });
              }
              if (data.done) {
                const { cleanContent, actions } = parseActions(fullContent);
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = {
                    role: "assistant",
                    content: cleanContent,
                    actions: actions
                  };
                  return updated;
                });
              }
            } catch {}
          }
        }
      }
    } catch {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          actions: []
        };
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestions = [
    { icon: "🏙️", text: "Buy a flat in Hyderabad" },
    { icon: "💰", text: "Properties under 50 lakhs" },
    { icon: "🏗️", text: "Invest in Bangalore" },
  ];

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">
          <div className="logo-icon">🏠</div>
          <span>PropAssist</span>
        </div>

        <div className="sidebar-label">Quick Start</div>
        {suggestions.map((s, i) => (
          <div key={i} className="suggestion" onClick={() => sendMessage(s.text)}>
            <span className="suggestion-icon">{s.icon}</span>
            <span>{s.text}</span>
          </div>
        ))}

        <div className="sidebar-footer">
          Powered by AI · Real Estate Only
        </div>
      </div>

      <div className="chat">
        <div className="chat-header">
          <div className="agent-info">
            <div className="agent-avatar">PA</div>
            <div>
              <div className="agent-name">PropAssist</div>
              <div className="agent-status">
                <span className="status-dot"></span>
                {loading ? "Typing..." : "Online"}
              </div>
            </div>
          </div>
        </div>

        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.role === "assistant" && <div className="avatar">PA</div>}
              <div className="message-wrapper">
                <div className="bubble">
                  {msg.content}
                  {msg.role === "assistant" && msg.content === "" && (
                    <span className="typing">
                      <span></span><span></span><span></span>
                    </span>
                  )}
                </div>
                {msg.actions && msg.actions.length > 0 && (
                  <div className="actions">
                    {msg.actions.map((action, j) => (
                      <button
                        key={j}
                        className="action-btn"
                        onClick={() => sendMessage(action)}
                        disabled={loading}
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="input-area">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about properties, prices, locations..."
            rows={1}
            disabled={loading}
          />
          <button onClick={() => sendMessage()} disabled={loading || !input.trim()}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;