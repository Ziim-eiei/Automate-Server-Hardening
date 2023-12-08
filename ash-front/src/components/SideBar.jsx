import React from "react";
import "../css/Card.css";
import { SideBarData } from "./SideBarData";
import { useNavigate } from "react-router-dom";

function SideBar() {
  const navigate = useNavigate();
  return (
    <span className="sidebar">
      <h1 className="Sidebar-heading">Hardening & Audit</h1>
      <ul className="SideBarList">
        {SideBarData.map((val, key) => {
          return (
            <li
              key={key}
              className="row"
              onClick={() => {
                if (val.link == "/hardening") window.location.href = val.link;
                else navigate(val.link);
              }}
            >
              <div id="icon">{val.icon}</div>
              <div id="title">{val.title}</div>
            </li>
          );
        })}
      </ul>
    </span>
  );
}

export default SideBar;
