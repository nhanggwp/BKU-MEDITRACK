import React, { useState } from "react";
import {
  FaUser,
  FaBell,
  FaPalette,
  FaLock,
  FaGlobe,
  FaPlug,
} from "react-icons/fa";
import "./SettingsPage.css";

const SettingsPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [emailNotif, setEmailNotif] = useState(true);
  const [smsNotif, setSmsNotif] = useState(false);

  const sections = [
    {
      title: "General",
      items: [
        {
          icon: <FaUser />,
          title: "Profile Settings",
          desc: "Update your personal information",
          action: <button className="btn">Edit</button>,
        },
        {
          icon: <FaBell />,
          title: "Notifications",
          desc: (
            <div className="notif-toggles">
              <label>
                Email
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={emailNotif}
                    onChange={() => setEmailNotif(!emailNotif)}
                  />
                  <span className="slider" />
                </label>
              </label>
              <label>
                SMS
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={smsNotif}
                    onChange={() => setSmsNotif(!smsNotif)}
                  />
                  <span className="slider" />
                </label>
              </label>
            </div>
          ),
        },
        {
          icon: <FaPalette />,
          title: "Theme",
          desc: "Light / Dark mode",
          action: (
            <label className="switch">
              <input
                type="checkbox"
                checked={darkMode}
                onChange={() => setDarkMode(!darkMode)}
              />
              <span className="slider" />
            </label>
          ),
        },
      ],
    },
    {
      title: "Security",
      items: [
        {
          icon: <FaLock />,
          title: "Security & Privacy",
          desc: "Change password & 2FA",
          action: <button className="btn">Manage</button>,
        },
      ],
    },
    {
      title: "Preferences",
      items: [
        {
          icon: <FaGlobe />,
          title: "Language & Region",
          desc: "Select language and locale",
          action: (
            <select className="select">
              <option value="en">English</option>
              <option value="vi">Tiếng Việt</option>
            </select>
          ),
        },
        {
          icon: <FaPlug />,
          title: "Integrations",
          desc: "Manage API keys & webhooks",
          action: <button className="btn">Manage</button>,
        },
      ],
    },
  ];

  return (
    <div className="settings-page">
      <h1 className="settings-header">Settings</h1>
      {sections.map((sec, si) => (
        <div key={si} className="settings-section">
          <h2 className="section-title">{sec.title}</h2>
          <div className="settings-items">
            {sec.items.map((it, i) => (
              <div key={i} className="settings-item">
                <div className="settings-icon">{it.icon}</div>
                <div className="settings-content">
                  <div className="settings-title">{it.title}</div>
                  <div className="settings-desc">{it.desc}</div>
                </div>
                <div className="settings-action">{it.action}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SettingsPage;
