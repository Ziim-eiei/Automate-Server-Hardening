import React from "react";
import "../css/Card.css";
import { SideBarData } from "./SideBarData";

function SideBar() {
  return (
    <span class="sidebar">
      <h1 className="Sidebar-heading">Hardening & Audit</h1>
      <ul className="SideBarList">
        {SideBarData.map((val, key) => {
          return (
            <li
              key={key}
              className="row"
              onClick={() => {
                window.location.pathname = val.link;
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
