import React, { useState } from "react";
import "./ChatbotPage.css";
import botAvatar from "../../assets/logo.png";
import { FaSmile, FaPaperclip, FaPaperPlane } from "react-icons/fa";
import aiService from "../../services/aiService";

const ChatbotPage = () => {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (input.trim() === "") return;

    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setInput("");

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "I'm just a demo. In the future I’ll be smarter!",
        },
      ]);
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
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
              <div className={`chat-message ${msg.sender}`}>{msg.text}</div>
            </div>
          ))}
        </div>
        <div className="chat-input-container">
          <div className="input-box">
            <FaSmile className="input-icon" style={{ fontSize: "28px" }} />
            <input
              type="text"
              placeholder="Type a message"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <FaPaperclip className="input-icon" style={{ fontSize: "28px" }} />
          </div>
          <button className="send-btn" onClick={sendMessage}>
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;
