import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { FaPlusCircle, FaQrcode, FaChartBar } from "react-icons/fa";
import "./PrescriptionLayout.css";

const PrescriptionLayout = () => {
  return (
    <div className="prescription-layout">
      <div className="prescription-toolbar">
        {/* Prescription Scanner */}
        <NavLink to="prescription-scan" className="toolbar-item">
          <FaQrcode size={28} />
          <span>Scan</span>
        </NavLink>
        {/* Prescription Checker  */}
        <NavLink to="prescription-check" className="toolbar-item">
          <FaPlusCircle size={28} />
          <span>Add</span>
        </NavLink>

        {/* Prescription Results */}
        <NavLink to="result" className="toolbar-item">
          <FaChartBar size={28} />
          <span>Results</span>
        </NavLink>
      </div>
      <div className="prescription-content">
        <Outlet />
      </div>
    </div>
  );
};

export default PrescriptionLayout;
