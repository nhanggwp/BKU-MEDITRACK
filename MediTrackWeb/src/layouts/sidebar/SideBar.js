import React from "react";
import {
  FaHome,
  FaUserInjured,
  FaNotesMedical,
  FaBell,
  FaCog,
  FaSignOutAlt,
  FaMoneyBillAlt,
  FaExchangeAlt,
  FaRobot,
} from "react-icons/fa";
import { GiPill } from "react-icons/gi";
import { NavLink, useNavigate } from "react-router-dom";
import "./SideBar.css";
import logo from "../../assets/logo.png";
import { useAuth } from "../../context/AuthContext";

const SideBar = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/");
    } catch (error) {
      console.error("Logout failed:", error);
      // Even if logout API fails, redirect to login
      navigate("/");
    }
  };
  return (
    <div className="sidebar">
      <div className="logo">
        <img src={logo} alt="Logo" className="logo-img" />
        <span className="logo-text">
          <span className="highlight-blue">MEDI</span>
          <span className="highlight-green">TRACK</span>
        </span>
      </div>

      <div className="menu">
        {[
          { to: "/home", icon: <FaHome />, label: "Home" },
          { to: "/home/patients", icon: <FaUserInjured />, label: "Patients" },

          { to: "/home/prescription", icon: <GiPill />, label: "Prescription" },
          {
            to: "/home/notifications",
            icon: <FaBell />,
            label: "Notifications",
          },
          { to: "/home/settings", icon: <FaCog />, label: "Settings" },
          { to: "/home/chatbot", icon: <FaRobot />, label: "Chatbot" },
        ].map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end
            className={({ isActive }) =>
              `menu-item${isActive ? " active" : ""}`
            }
          >
            {icon}
            {label}
          </NavLink>
        ))}

        <hr className="divider" />
        {/* <div className="report-label">Report</div>

        {[
          {
            to: "/home/payments",
            icon: <FaMoneyBillAlt />,
            label: "Payment Details",
          },
          {
            to: "/home/transactions",
            icon: <FaExchangeAlt />,
            label: "Transactions",
          },
        ].map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `menu-item${isActive ? " active" : ""}`
            }
          >
            {icon}
            {label}
          </NavLink>
        ))} */}
      </div>

      <button className="logout-button" onClick={handleLogout}>
        <FaSignOutAlt /> Log out
      </button>
    </div>
  );
};

export default SideBar;
