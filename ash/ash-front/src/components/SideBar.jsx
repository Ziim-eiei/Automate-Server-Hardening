import React, { useRef } from "react";
import "../css/Card.css";
import { SideBarData } from "./SideBarData";
import { useNavigate } from "react-router-dom";

function SideBar({ serverId }) {
  const navigate = useNavigate();
  const path = useRef(null);
  if (window.location.pathname.split("/").length > 1) {
    if (window.location.pathname.split("/")[1] === "server") {
      path.current = "/project";
    } else path.current = "/" + window.location.pathname.split("/")[1];
  } else {
    path.current = window.location.pathname;
  }
  // console.log(path.current);
  return (
    <span className="sidebar">
      <h1 className="Sidebar-heading HeadText">Hardening & Audit</h1>
      <ul className="SideBarList">
        {SideBarData.map((val, key) => {
          return (
            <li
              key={key}
              className={
                val.link === path.current
                  ? "row SubText cursor-pointer bg-gradient-to-r from-[#7E73FF] to-slate-80 rounded-md"
                  : "row SubText cursor-pointer hover:bg-[#0E1625] rounded-md"
              }
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
