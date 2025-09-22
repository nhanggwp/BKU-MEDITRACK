// src/layouts/home/HomePage.js
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  FaUsers,
  FaExclamationTriangle,
  FaBell,
  FaPills,
  FaVials,
  FaPen,
} from "react-icons/fa";
import avatarUrl from "../../assets/doctor-avatar.png";
import "./HomePage.css";

const demoStats = {
  totalPatients: 10,
  criticalCases: 1,
  todaysPrescriptions: 5,
  newAlerts: 3,
};

const demoNotifications = [
  {
    id: 1,
    message:
      "Remember to review the lab test results for patient Nguyen Trung N today",
    type: "alert",
  },
  {
    id: 2,
    message: "New prescription submitted",
    date: "today",
    time: "10:30 AM",
  },
  {
    id: 3,
    message: "Blood test result of Ho Minh N available",
    date: "today",
    time: "11:45 AM",
  },
];

export default function HomePage({
  stats = demoStats,
  notifications = demoNotifications,
  doctorName = "Dr. Panda Nguyen",
}) {
  const navigate = useNavigate();

  return (
    <div className="home-wrapper">
      {/* Header Greeting */}
      <header className="home-header">
        <div className="home-greeting">
          <h1>Welcome back, {doctorName}</h1>
        </div>
        <img src={avatarUrl} alt="Doctor avatar" className="home-avatar" />
      </header>

      {/* Blue Background Section */}
      <div className="home-content">
        {/* Stats Cards */}
        <section className="home-stats-grid">
          <DashboardStatCard
            color="primary"
            icon={<FaUsers />}
            label="Total Patients"
            value={stats.totalPatients}
            onClick={() => navigate("/home/patients")}
          />
          <DashboardStatCard
            color="warning"
            icon={<FaExclamationTriangle />}
            label="Critical Cases"
            value={stats.criticalCases}
          />
          <DashboardStatCard
            color="accent"
            icon={<FaPills />}
            label="Today's Prescriptions"
            value={stats.todaysPrescriptions}
          />
          <DashboardStatCard
            color="info"
            icon={<FaBell />}
            label="New Alerts"
            value={stats.newAlerts}
            onClick={() => navigate("/home/notifications")}
          />
        </section>

        {/* Notifications + Activity Panel */}
        <section className="home-main-section">
          {/* Notifications List */}
          <div
            className="home-notifications"
            onClick={() => navigate("/home/notifications")}
            style={{ cursor: "pointer" }}
          >
            <h2>Notifications</h2>
            <hr />
            <ul className="notifications-list">
              {notifications.map((n) => (
                <li key={n.id} className={`notif-item ${n.type}`}>
                  <span className="notif-icon">
                    <FaBell />
                  </span>
                  <span className="notif-text">{n.message}</span>
                </li>
              ))}
              {notifications.length === 0 && (
                <li className="notif-empty">No new notifications.</li>
              )}
            </ul>
          </div>

          {/* Today's Activity */}
          <div className="home-activity">
            <h2>Today's Activities</h2>
            <hr />
            <ul className="activity-list">
              <li className="activity-item">
                <span className="activity-icon blue">
                  <FaPills />
                </span>
                Checked 4 prescriptions
              </li>
              <li className="activity-item">
                <span className="activity-icon blue">
                  <FaVials />
                </span>
                Reviewed 2 lab results
              </li>
              <li className="activity-item">
                <span className="activity-icon blue">
                  <FaBell />
                </span>
                Responded to 3 alerts
              </li>
              <li className="activity-item">
                <span className="activity-icon blue">
                  <FaPen />
                </span>
                Added notes to 2 patients
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}

/* ---------------- Helper Component ---------------- */
function DashboardStatCard({ color, icon, label, value, onClick }) {
  return (
    <div
      className={`stat-card ${color}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="stat-icon">{icon}</div>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
