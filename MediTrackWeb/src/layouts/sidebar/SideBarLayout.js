import React from "react";
import SideBar from "./SideBar";
import { Outlet } from "react-router-dom";
import "./SideBarLayout.css";

const SideBarLayout = () => {
  return (
    <div className="layout">
      <SideBar />
      <div className="content">
        <Outlet /> {/* This renders the child route like MedicalRecord */}
      </div>
    </div>
  );
};

export default SideBarLayout;
