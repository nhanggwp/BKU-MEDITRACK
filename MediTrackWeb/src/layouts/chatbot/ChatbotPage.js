import React, { useState } from "react";
import "./ChatbotPage.css";
import botAvatar from "../../assets/logo.png";
import { FaSmile, FaPaperclip, FaPaperPlane } from "react-icons/fa";
import aiService from "../../services/aiService";

const ChatbotPage = () => {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! I'm your medical assistant. I can help you with medication information, drug interactions, and general health questions. How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (input.trim() === "" || isLoading) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      // Add typing indicator
      setMessages((prev) => [...prev, { sender: "bot", text: "Thinking...", isTyping: true }]);

      // Call AI service
      const response = await aiService.chatInteraction(userMessage);
      
      // Remove typing indicator and add real response
      setMessages((prev) => {
        const filtered = prev.filter(msg => !msg.isTyping);
        return [...filtered, { 
          sender: "bot", 
          text: response.explanation || "I'm sorry, I couldn't process that request. Could you please rephrase your question?",
          tokens_used: response.tokens_used 
        }];
      });

    } catch (error) {
      console.error("AI service error:", error);
      // Remove typing indicator and add error message
      setMessages((prev) => {
        const filtered = prev.filter(msg => !msg.isTyping);
        return [...filtered, { 
          sender: "bot", 
          text: "I'm experiencing some technical difficulties. Please try again later. In the meantime, you can check drug interactions using the Prescription tab." 
        }];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chatbot-page">
      <div className="chat-window">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`message-row ${
                msg.sender === "bot" ? "left" : "right"
              }`}
            >
              {msg.sender === "bot" && (
                <img src={botAvatar} alt="Bot" className="bot-avatar" />
              )}
              <div className={`chat-message ${msg.sender} ${msg.isTyping ? 'typing' : ''}`}>
                {msg.text}
                {msg.isTyping && (
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="chat-input-container">
          <div className="input-box">
            <FaSmile className="input-icon" style={{ fontSize: "28px" }} />
            <input
              type="text"
              placeholder={isLoading ? "AI is thinking..." : "Ask about medications, interactions, or health questions..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            <FaPaperclip className="input-icon" style={{ fontSize: "28px" }} />
          </div>
          <button 
            className="send-btn" 
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            style={{ 
              opacity: isLoading || !input.trim() ? 0.5 : 1,
              cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;
