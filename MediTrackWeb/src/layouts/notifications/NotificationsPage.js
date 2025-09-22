import React from "react";
import "./NotificationsPage.css";
import { FaBell } from "react-icons/fa";

// Demo notification data (you could later replace this with real API data)
const demoNotifications = [
  {
    id: 1,
    message: "Review Nguyen Trung N lab results",
    date: "today",
    time: "09:15 AM",
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
  {
    id: 4,
    message: "Vaccination update pediatric",
    date: "yesterday",
    time: "03:20 PM",
  },
  {
    id: 5,
    message: "Schedule follow‑up Ho Minh N",
    date: "yesterday",
    time: "04:10 PM",
  },
  {
    id: 6,
    message: "System maintenance notice",
    date: "2days",
    time: "08:00 AM",
  },
  {
    id: 7,
    message: "New patient registration",
    date: "2days",
    time: "09:30 AM",
  },
  {
    id: 8,
    message: "Appointment cancellation: Mark T.",
    date: "2days",
    time: "11:00 AM",
  },
  { id: 9, message: "Monthly report available", date: "1week", time: "Monday" },
  { id: 10, message: "Team meeting scheduled", date: "1week", time: "Tuesday" },
  {
    id: 11,
    message: "Feedback request from Anna",
    date: "1week",
    time: "Wednesday",
  },
  {
    id: 12,
    message: "New doctor joined the clinic",
    date: "1week",
    time: "Thursday",
  },
];

// Helper function to group notifications by date
const groupByDate = (notifications) => {
  const groups = { today: [], yesterday: [], "2days": [], "1week": [] };
  notifications.forEach((n) => groups[n.date]?.push(n)); // push into correct group if exists
  return groups;
};

export default function NotificationsPage() {
  const groups = groupByDate(demoNotifications); // grouped notifications

  // Map date keys to display labels
  const getGroupLabel = (group) =>
    ({
      today: "Today",
      yesterday: "Yesterday",
      "2days": "2 Days Ago",
      "1week": "1 Week Ago",
    }[group] || group);

  return (
    <div className="notifications-page-wrapper">
      <div className="notifications-container">
        {/* Page title */}
        <h1 className="page-title">Notifications Center</h1>

        {/* Loop through each group (today, yesterday, etc.) */}
        {Object.entries(groups).map(([group, items]) =>
          items.length > 0 ? ( // Only show if there are items
            <section key={group} className="notif-section">
              <h2>
                {getGroupLabel(group)}
                <span className="notif-count">({items.length})</span>
              </h2>

              <ul className="notif-list">
                {/* List notifications under this group */}
                {items.map((n, idx) => (
                  <li
                    key={n.id}
                    className="notif-item"
                    style={{ animationDelay: `${idx * 0.08}s` }} // stagger animation effect
                  >
                    <FaBell className="notif-icon" />
                    <span className="notif-message">{n.message}</span>
                    <span className="notif-time">{n.time}</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : null
        )}
      </div>
    </div>
  );
}
