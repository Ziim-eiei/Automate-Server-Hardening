import React from "react";
import "../css/Card.css";
import { SideBarData } from "./SideBarData";
import { useNavigate } from "react-router-dom";

function SideBar({ serverId }) {
  const navigate = useNavigate();
  return (
    <span className="sidebar">
      <h1 className="Sidebar-heading HeadText">Hardening & Audit</h1>
      <ul className="SideBarList">
        {SideBarData.map((val, key) => {
          return (
            <li
              key={key}
              className="row SubText cursor-pointer"
              onClick={() => {
                if (val.link == "/hardening" && serverId != null) {
                } else navigate(val.link);
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
