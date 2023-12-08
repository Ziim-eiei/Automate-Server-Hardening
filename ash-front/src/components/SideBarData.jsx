import React from "react";
import HomeIcon from "@mui/icons-material/Home";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import ManageHistoryOutlinedIcon from "@mui/icons-material/ManageHistoryOutlined";
import StorageIcon from "@mui/icons-material/Storage";
import FolderIcon from "@mui/icons-material/Folder";

export const SideBarData = [
  // {
  //   title: "Home",
  //   icon: <HomeIcon />,
  //   link: "/Home",
  // },
  {
    title: "Project",
    icon: <FolderIcon />,
    link: "/project",
  },
  // {
  //   title: "Server",
  //   icon: <StorageIcon />,
  //   link: "/server",
  // },
  {
    title: "Hardening & Audit",
    icon: <SettingsOutlinedIcon />,
    link: "/hardening",
  },
  // {
  //   title: "Audit History",
  //   icon: <ManageHistoryOutlinedIcon />,
  //   link: "/Home",
  // },
  // {
  //   title: "Hardening History",
  //   icon: <ManageHistoryOutlinedIcon />,
  //   link: "/Home",
  // },
];
